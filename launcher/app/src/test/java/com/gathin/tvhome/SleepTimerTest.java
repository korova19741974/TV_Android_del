package com.gathin.tvhome;

import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

public class SleepTimerTest {
    @Test public void acceptsOnlyVisibleRemotePresets() {
        assertTrue(SleepTimer.isSupported(15));
        assertTrue(SleepTimer.isSupported(120));
        assertTrue(SleepTimer.isSupported(0));
        assertFalse(SleepTimer.isSupported(10));
    }

    @Test public void remainingTimeNeverBecomesNegative() {
        assertEquals(30_000L, SleepTimer.remainingMillis(130_000L, 100_000L));
        assertEquals(0L, SleepTimer.remainingMillis(100_000L, 130_000L));
        assertEquals(0L, SleepTimer.remainingMillis(0L, 130_000L));
    }

    @Test public void currentPresetIsSelectedByNearestRemainingTime() {
        assertEquals(3, SleepTimer.selectedIndex(3_600_000L, 0L));
        assertEquals(0, SleepTimer.selectedIndex(0L, 0L));
    }
}
