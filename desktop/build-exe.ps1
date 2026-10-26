# Build a portable Windows bundle with CleanYourTV.exe.
param([switch]$SkipToolPreparation)

$ErrorActionPreference = 'Stop'
$Desktop = $PSScriptRoot
$Root = Split-Path -Parent $Desktop
$Venv = Join-Path $Root 'tools\venv'
$VenvPython = Join-Path $Venv 'Scripts\python.exe'
$BuildRoot = Join-Path $Desktop 'build'
$DistRoot = Join-Path $Desktop 'dist'
$Bundle = Join-Path $DistRoot 'CleanYourTV'
$PyInstallerWork = Join-Path $BuildRoot 'pyinstaller'

function Run-Checked {
    param([string]$File, [string[]]$Arguments, [string]$Failure)
    & $File @Arguments
    if ($LASTEXITCODE -ne 0) { throw $Failure }
}

if (-not $SkipToolPreparation) {
    $powershell = Get-Command powershell.exe -ErrorAction SilentlyContinue
    if (-not $powershell) { throw 'Windows PowerShell was not found.' }
    Run-Checked $powershell.Source @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
        (Join-Path $Desktop 'prepare-windows.ps1')) 'JDK/Android SDK preparation failed.'
}

$pyLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
$python = Get-Command python.exe -ErrorAction SilentlyContinue
$pythonPath = if ($python -and $python.Source -notmatch '\\WindowsApps\\') { $python.Source } else { $null }
if (-not $pyLauncher -and -not $pythonPath) {
    $pythonPath = Get-ChildItem -LiteralPath (Join-Path $env:LOCALAPPDATA 'Programs\Python') -Recurse -Filter python.exe -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch '\\Lib\\' } |
        Select-Object -First 1 -ExpandProperty FullName
}
if (-not $pyLauncher -and -not $pythonPath) {
    throw 'Python 3 was not found. Install Python 3 and run this script again.'
}

$basePythonPath = if ($pyLauncher) {
    (& $pyLauncher.Source -3 -c 'import sys; print(sys.executable)').Trim()
} else {
    $pythonPath
}
if (-not (Test-Path -LiteralPath $basePythonPath)) {
    throw 'The installed Python executable could not be located.'
}

if (-not (Test-Path -LiteralPath $VenvPython)) {
    if ($pyLauncher) {
        Run-Checked $pyLauncher.Source @('-3', '-m', 'venv', $Venv) 'Could not create the Python build environment.'
    } else {
        Run-Checked $pythonPath @('-m', 'venv', $Venv) 'Could not create the Python build environment.'
    }
}

Run-Checked $VenvPython @('-m', 'pip', 'install', '--disable-pip-version-check', '-r',
    (Join-Path $Root 'tools\requirements.txt')) 'Could not install project Python requirements.'
Run-Checked $VenvPython @('-m', 'pip', 'install', '--disable-pip-version-check', '--upgrade', 'pyinstaller') 'Could not install PyInstaller.'

New-Item -ItemType Directory -Force -Path $BuildRoot, $DistRoot | Out-Null
if (Test-Path -LiteralPath $Bundle) {
    Remove-Item -LiteralPath $Bundle -Recurse -Force
}

$pyinstallerArgs = @(
    '-m', 'PyInstaller',
    '--noconfirm',
    '--clean',
    '--windowed',
    '--name', 'CleanYourTV',
    '--distpath', $DistRoot,
    '--workpath', $PyInstallerWork,
    '--specpath', $PyInstallerWork,
    '--hidden-import', 'tools.unified',
    '--hidden-import', 'recovery',
    '--hidden-import', 'catalog',
    (Join-Path $Desktop 'CleanYourTV.py')
)
Run-Checked $VenvPython $pyinstallerArgs 'PyInstaller could not build CleanYourTV.exe.'

# The GUI calls these files as ordinary Windows scripts. Keep them next to the EXE so the
# application can build/install the Android launcher after it has been copied to another PC.
$bundleTools = Join-Path $Bundle 'tools'
New-Item -ItemType Directory -Force -Path $bundleTools | Out-Null
Get-ChildItem -LiteralPath (Join-Path $Root 'tools') -Force |
    Where-Object { $_.Name -ne 'venv' } |
    Copy-Item -Destination $bundleTools -Recurse -Force

# A venv points to the build computer's Python installation. Copy a self-contained Python runtime
# and the already installed project packages instead, then use it from the bundled PowerShell files.
$runtimePython = Join-Path $bundleTools 'python'
Copy-Item -LiteralPath (Split-Path -Parent $basePythonPath) -Destination $runtimePython -Recurse -Force
$runtimeSitePackages = Join-Path $runtimePython 'Lib\site-packages'
New-Item -ItemType Directory -Force -Path $runtimeSitePackages | Out-Null
Get-ChildItem -LiteralPath (Join-Path $Venv 'Lib\site-packages') -Force |
    Copy-Item -Destination $runtimeSitePackages -Recurse -Force

Copy-Item -LiteralPath (Join-Path $Root 'launcher') -Destination $Bundle -Recurse -Force
Copy-Item -LiteralPath (Join-Path $Root 'examples') -Destination $Bundle -Recurse -Force
New-Item -ItemType Directory -Force -Path (Join-Path $Bundle 'desktop') | Out-Null
Copy-Item -LiteralPath (Join-Path $Desktop 'prepare-windows.ps1') -Destination (Join-Path $Bundle 'desktop') -Force
Copy-Item -LiteralPath (Join-Path $Desktop 'start-clean-your-tv.bat') -Destination (Join-Path $Bundle 'desktop') -Force

Write-Host ''
Write-Host 'EXE bundle is ready:'
Write-Host (Join-Path $Bundle 'CleanYourTV.exe')
Write-Host 'Copy the complete desktop\dist\CleanYourTV folder, not only the EXE.'
