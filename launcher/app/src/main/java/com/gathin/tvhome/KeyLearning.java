package com.gathin.tvhome;

import android.content.Context;
import android.view.KeyEvent;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;

/** One-shot remote-button learning for the Windows setup program. */
final class KeyLearning {
    static final String ACTION = "com.gathin.tvhome.LEARN_KEY";
    private static final String REQUEST = "learn-key.request";
    private static final String RESULT = "learn-key.result";

    private KeyLearning() {
    }

    static synchronized String arm(Context context) throws IOException {
        File dir = Config.dir(context);
        if (dir == null || (!dir.isDirectory() && !dir.mkdirs())) {
            throw new IOException("external storage is unavailable");
        }
        File result = new File(dir, RESULT);
        if (result.exists() && !result.delete()) throw new IOException("could not clear old key result");
        File request = new File(dir, REQUEST);
        try (FileOutputStream output = new FileOutputStream(request, false)) {
            output.write("waiting\n".getBytes(StandardCharsets.UTF_8));
        }
        return result.getAbsolutePath();
    }

    /** Capture only the first key-down while a request is armed. */
    static synchronized boolean capture(Context context, KeyEvent event) {
        File dir = Config.dir(context);
        if (dir == null) return false;
        File request = new File(dir, REQUEST);
        if (!request.isFile()) return false;
        if (event.getAction() != KeyEvent.ACTION_DOWN) return true;
        File result = new File(dir, RESULT);
        String line = "keycode=" + event.getKeyCode()
                + " scancode=" + event.getScanCode()
                + " name=" + KeyEvent.keyCodeToString(event.getKeyCode()) + "\n";
        try (FileOutputStream output = new FileOutputStream(result, false)) {
            output.write(line.getBytes(StandardCharsets.UTF_8));
            if (!request.delete()) result.delete();
            return result.isFile();
        } catch (IOException ignored) {
            return false;
        }
    }
}
