package com.gathin.tvhome;

import android.accessibilityservice.AccessibilityService;
import android.animation.Animator;
import android.animation.AnimatorListenerAdapter;
import android.animation.ValueAnimator;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.os.Build;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.view.animation.AccelerateInterpolator;

/** A brief, failure-safe fade before Android puts the TV into standby. */
final class ScreenSleep {
    static final long FADE_DURATION_MS = 240L;
    private static final long REMOVE_COVER_DELAY_MS = 1000L;

    private ScreenSleep() { }

    static boolean canFade(boolean accessibilityService, int sdk) {
        return accessibilityService && sdk >= Build.VERSION_CODES.P;
    }

    /**
     * Returns false only before any visual change, so the caller can lock the screen immediately instead.
     * The cover always removes itself: a firmware which refuses the global action must never leave a black UI.
     */
    static boolean fadeAndLock(AccessibilityService service) {
        if (!canFade(true, Build.VERSION.SDK_INT)) return false;
        WindowManager windowManager = service.getSystemService(WindowManager.class);
        if (windowManager == null) return false;

        View cover = new View(service);
        cover.setBackgroundColor(Color.BLACK);
        cover.setAlpha(0f);
        cover.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);
        int flags = WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                | WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE
                | WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN
                | WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS;
        WindowManager.LayoutParams params = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY,
                flags,
                PixelFormat.TRANSLUCENT);
        params.gravity = Gravity.TOP | Gravity.START;

        try {
            windowManager.addView(cover, params);
        } catch (RuntimeException ignored) {
            return false;
        }

        Runnable removeCover = () -> {
            try {
                windowManager.removeViewImmediate(cover);
            } catch (RuntimeException ignored) {
                // Already removed because the display went to sleep.
            }
        };
        ValueAnimator fade = ValueAnimator.ofFloat(0f, 1f);
        fade.setDuration(FADE_DURATION_MS);
        fade.setInterpolator(new AccelerateInterpolator());
        fade.addUpdateListener(animation -> cover.setAlpha((float) animation.getAnimatedValue()));
        fade.addListener(new AnimatorListenerAdapter() {
            private boolean cancelled;

            @Override public void onAnimationCancel(Animator animation) {
                cancelled = true;
                removeCover.run();
            }

            @Override public void onAnimationEnd(Animator animation) {
                if (cancelled) return;
                if (!service.performGlobalAction(AccessibilityService.GLOBAL_ACTION_LOCK_SCREEN)) {
                    removeCover.run();
                    return;
                }
                cover.postDelayed(removeCover, REMOVE_COVER_DELAY_MS);
            }
        });
        try {
            fade.start();
            return true;
        } catch (RuntimeException ignored) {
            removeCover.run();
            return false;
        }
    }
}
