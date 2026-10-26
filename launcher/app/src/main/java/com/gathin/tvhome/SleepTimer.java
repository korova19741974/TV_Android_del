package com.gathin.tvhome;

import android.content.Context;
import android.content.SharedPreferences;

/** Persistent sleep-timer state. The accessibility helper performs the actual screen lock. */
final class SleepTimer {
    static final int[] MINUTES = {0, 15, 30, 60, 90, 120};
    private static final String PREFS = "sleep_timer";
    private static final String END_AT = "end_at";

    private SleepTimer() {
    }

    static void set(Context context, int minutes) {
        if (!isSupported(minutes)) throw new IllegalArgumentException("Unsupported sleep timer value");
        SharedPreferences prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        if (minutes == 0) prefs.edit().remove(END_AT).apply();
        else prefs.edit().putLong(END_AT, System.currentTimeMillis() + minutes * 60_000L).apply();
    }

    static long endAt(Context context) {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getLong(END_AT, 0L);
    }

    static long remainingMillis(long endAt, long now) {
        return endAt <= 0L ? 0L : Math.max(0L, endAt - now);
    }

    static boolean isSupported(int minutes) {
        for (int value : MINUTES) if (value == minutes) return true;
        return false;
    }

    static int selectedIndex(long endAt, long now) {
        long remaining = remainingMillis(endAt, now);
        if (remaining <= 0L) return 0;
        long minutes = (remaining + 60_000L - 1L) / 60_000L;
        int best = 1;
        long distance = Math.abs(MINUTES[best] - minutes);
        for (int i = 2; i < MINUTES.length; i++) {
            long candidateDistance = Math.abs(MINUTES[i] - minutes);
            if (candidateDistance < distance) {
                best = i;
                distance = candidateDistance;
            }
        }
        return best;
    }
}
