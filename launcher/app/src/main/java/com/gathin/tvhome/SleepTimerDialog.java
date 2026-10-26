package com.gathin.tvhome;

import android.app.Activity;
import android.app.AlertDialog;
import android.widget.Toast;

/** Small remote-friendly picker shared by the Home gear and the Settings button panel. */
final class SleepTimerDialog {
    private SleepTimerDialog() {
    }

    static void show(Activity activity) {
        String[] labels = activity.getResources().getStringArray(R.array.sleep_timer_choices);
        int checked = SleepTimer.selectedIndex(SleepTimer.endAt(activity), System.currentTimeMillis());
        new AlertDialog.Builder(activity)
                .setTitle(R.string.sleep_timer)
                .setSingleChoiceItems(labels, checked, (dialog, which) -> {
                    if (which < 0 || which >= SleepTimer.MINUTES.length) return;
                    int minutes = SleepTimer.MINUTES[which];
                    if (minutes > 0 && !HomeKeyService.canOpenPowerMenu()) {
                        Toast.makeText(activity, R.string.sleep_timer_unavailable, Toast.LENGTH_LONG).show();
                        return;
                    }
                    HomeKeyService.setSleepTimer(activity, minutes);
                    Toast.makeText(activity, minutes == 0 ? R.string.sleep_timer_off : R.string.sleep_timer_set,
                            Toast.LENGTH_SHORT).show();
                    dialog.dismiss();
                })
                .setNegativeButton(android.R.string.cancel, null)
                .show();
    }
}
