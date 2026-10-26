package com.gathin.tvhome;

import org.junit.Test;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

/** A small repeatable budget for the pure hot path used while arranging the Home tiles. */
public class PerformanceBudgetTest {
    @Test public void twelveTileOrderingStaysWithinOneSecond() {
        List<String> keys = new ArrayList<>();
        for (char c = 'a'; c <= 'l'; c++) keys.add(String.valueOf(c));
        HashSet<String> dock = new HashSet<>(keys.subList(0, 6));
        long started = System.nanoTime();
        List<String> result = null;
        for (int i = 0; i < 100_000; i++) result = DockSlots.dockFirst(keys, 6, dock);
        long elapsed = System.nanoTime() - started;
        assertEquals(keys, result);
        assertTrue("tile ordering exceeded 1 second: " + elapsed / 1_000_000 + " ms",
                elapsed < 1_000_000_000L);
    }
}
