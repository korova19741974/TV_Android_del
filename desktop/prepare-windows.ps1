# Check launcher build tools and install only missing components.
param([switch]$Quiet)

$ErrorActionPreference = 'Stop'
$OutputEncoding = New-Object System.Text.UTF8Encoding $false
$SdkRoot = if ($env:ANDROID_HOME) { $env:ANDROID_HOME } else { Join-Path $env:LOCALAPPDATA 'Android\Sdk' }
$JdkPackage = 'Microsoft.OpenJDK.17'
$SdkToolsUrl = 'https://dl.google.com/android/repository/commandlinetools-win-15859902_latest.zip'
$SdkToolsSha256 = '90ae805d20434428bffcb699c290860f19bb5f66a67e6b330067e3de801fb04a'

function Say([string]$Text) {
    if (-not $Quiet) { Write-Host $Text }
}

function Find-Jdk {
    $candidates = @()
    if ($env:JAVA_HOME) { $candidates += $env:JAVA_HOME }
    $java = Get-Command java.exe -ErrorAction SilentlyContinue
    if ($java) { $candidates += (Split-Path (Split-Path $java.Source -Parent) -Parent) }
    foreach ($root in @('C:\Program Files\Microsoft', 'C:\Program Files\Java', 'C:\Program Files\Android')) {
        if (Test-Path -LiteralPath $root) {
            $candidates += Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue |
                ForEach-Object {
                    $_.FullName
                    Join-Path $_.FullName 'jbr'
                }
        }
    }
    foreach ($candidate in ($candidates | Where-Object { $_ } | Select-Object -Unique)) {
        $javaPath = Join-Path $candidate 'bin\java.exe'
        $javacPath = Join-Path $candidate 'bin\javac.exe'
        if (-not (Test-Path -LiteralPath $javaPath) -or -not (Test-Path -LiteralPath $javacPath)) { continue }
        $previousPreference = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        $version = (& $javaPath -version 2>&1) -join "`n"
        $ErrorActionPreference = $previousPreference
        if ($version -match 'version "([0-9]+)') {
            $major = [int]$Matches[1]
            if ($major -ge 17) { return $candidate }
        }
    }
    return $null
}

function Install-Jdk {
    if (-not (Get-Command winget.exe -ErrorAction SilentlyContinue)) {
        throw 'winget was not found. Install App Installer or JDK 17 manually.'
    }
    Say 'JDK 17 was not found. Installing Microsoft OpenJDK 17...'
    & winget install --id $JdkPackage --exact --source winget --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) { throw 'Could not install JDK 17 through winget.' }
}

function Find-SdkManager {
    $latest = Join-Path $SdkRoot 'cmdline-tools\latest\bin\sdkmanager.bat'
    if (Test-Path -LiteralPath $latest) { return $latest }
    $tools = Join-Path $SdkRoot 'cmdline-tools'
    if (Test-Path -LiteralPath $tools) {
        $found = Get-ChildItem -LiteralPath $tools -Recurse -Filter sdkmanager.bat -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if ($found) { return $found.FullName }
    }
    return $null
}

function Install-SdkTools {
    Say 'Android SDK command-line tools were not found. Downloading the official Google package...'
    $stage = Join-Path $env:TEMP ("cleanyourtv-sdk-" + [guid]::NewGuid().ToString('N'))
    $zip = Join-Path $stage 'commandlinetools.zip'
    $expanded = Join-Path $stage 'expanded'
    $latest = Join-Path $SdkRoot 'cmdline-tools\latest'
    New-Item -ItemType Directory -Force -Path $stage,$expanded,(Join-Path $SdkRoot 'cmdline-tools') | Out-Null
    Invoke-WebRequest -Uri $SdkToolsUrl -OutFile $zip
    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $zip).Hash.ToLowerInvariant()
    if ($hash -ne $SdkToolsSha256) { throw 'Android SDK SHA-256 verification failed.' }
    Expand-Archive -LiteralPath $zip -DestinationPath $expanded
    if (Test-Path -LiteralPath $latest) { throw "Android SDK folder exists but sdkmanager was not found: $latest" }
    Move-Item -LiteralPath (Join-Path $expanded 'cmdline-tools') -Destination $latest
    return (Join-Path $latest 'bin\sdkmanager.bat')
}

function Add-UserPath([string]$PathToAdd) {
    $current = [Environment]::GetEnvironmentVariable('Path', 'User')
    $items = @($current -split ';' | Where-Object { $_ })
    if (-not ($items | Where-Object { $_.TrimEnd('\') -ieq $PathToAdd.TrimEnd('\') })) {
        [Environment]::SetEnvironmentVariable('Path', (($items + $PathToAdd) -join ';'), 'User')
    }
}

$jdk = Find-Jdk
if (-not $jdk) {
    Install-Jdk
    $jdk = Find-Jdk
}
if (-not $jdk) { throw 'JDK 17 was installed but could not be found. Restart Windows and try again.' }

$env:JAVA_HOME = $jdk
$env:Path = "$jdk\bin;$env:Path"
$sdkManager = Find-SdkManager
if (-not $sdkManager) { $sdkManager = Install-SdkTools }
$env:ANDROID_HOME = $SdkRoot
$env:ANDROID_SDK_ROOT = $SdkRoot
$env:Path = "$SdkRoot\platform-tools;$SdkRoot\cmdline-tools\latest\bin;$env:Path"

$missing = @()
if (-not (Test-Path -LiteralPath (Join-Path $SdkRoot 'platform-tools\adb.exe'))) { $missing += 'platform-tools' }
if (-not (Test-Path -LiteralPath (Join-Path $SdkRoot 'platforms\android-34\android.jar'))) { $missing += 'platforms;android-34' }
if (-not (Test-Path -LiteralPath (Join-Path $SdkRoot 'build-tools\34.0.0\aapt2.exe'))) { $missing += 'build-tools;34.0.0' }
if ($missing.Count -gt 0) {
    Say 'Installing Android SDK components required by the project...'
    1..30 | ForEach-Object { 'y' } | & $sdkManager "--sdk_root=$SdkRoot" '--licenses' | Out-Null
    & $sdkManager "--sdk_root=$SdkRoot" $missing
    if ($LASTEXITCODE -ne 0) { throw 'Could not install the required Android SDK components.' }
}

[Environment]::SetEnvironmentVariable('JAVA_HOME', $jdk, 'User')
[Environment]::SetEnvironmentVariable('ANDROID_HOME', $SdkRoot, 'User')
[Environment]::SetEnvironmentVariable('ANDROID_SDK_ROOT', $SdkRoot, 'User')
Add-UserPath (Join-Path $jdk 'bin')
Add-UserPath (Join-Path $SdkRoot 'platform-tools')
Add-UserPath (Join-Path $SdkRoot 'cmdline-tools\latest\bin')
Say 'JDK and Android SDK are ready.'
