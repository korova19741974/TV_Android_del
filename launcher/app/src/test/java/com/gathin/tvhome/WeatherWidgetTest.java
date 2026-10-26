package com.gathin.tvhome;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class WeatherWidgetTest {
    @Test
    public void mapsOpenMeteoCodesToRussianLabels() {
        assertEquals("ясно", WeatherWidget.description(0));
        assertEquals("облачно", WeatherWidget.description(3));
        assertEquals("дождь", WeatherWidget.description(63));
        assertEquals("снег", WeatherWidget.description(73));
        assertEquals("гроза", WeatherWidget.description(95));
    }
}
