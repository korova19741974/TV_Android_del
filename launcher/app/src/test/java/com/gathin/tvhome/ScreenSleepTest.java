package com.gathin.tvhome;

import android.os.Build;

import org.junit.Test;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

public class ScreenSleepTest {
    @Test public void fadeRequiresAccessibilityAndAndroidNineOrNewer() {
        assertFalse(ScreenSleep.canFade(false, Build.VERSION_CODES.UPSIDE_DOWN_CAKE));
        assertFalse(ScreenSleep.canFade(true, Build.VERSION_CODES.O_MR1));
        assertTrue(ScreenSleep.canFade(true, Build.VERSION_CODES.P));
    }
}
