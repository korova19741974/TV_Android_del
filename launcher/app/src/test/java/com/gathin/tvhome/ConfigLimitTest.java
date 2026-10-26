package com.gathin.tvhome;

import org.junit.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.Assert.assertEquals;

public class ConfigLimitTest {
    @Test public void pushedDockIsCappedAtTwelveAndKeepsOrder() {
        List<String> apps = new ArrayList<>();
        for (int i = 0; i < 15; i++) apps.add("com.example.app" + i);
        List<String> limited = Config.limitDockApps(apps);
        assertEquals(12, limited.size());
        assertEquals("com.example.app0", limited.get(0));
        assertEquals("com.example.app11", limited.get(11));
    }
}
