package com.gathin.tvhome;

import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Small, optional weather line. It uses Open-Meteo without an API key and never blocks the launcher UI. */
final class WeatherWidget {
    private static final long REFRESH_MS = 30L * 60L * 1000L;

    private final TextView view;
    private final String city;
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final Handler handler = new Handler(Looper.getMainLooper());
    private boolean stopped;

    WeatherWidget(TextView view, String city) {
        this.view = view;
        this.city = city == null ? "" : city.trim();
    }

    void start() {
        if (city.isEmpty()) {
            view.setVisibility(View.GONE);
            return;
        }
        view.setVisibility(View.VISIBLE);
        view.setText("Погода: загрузка…");
        refresh();
    }

    private void refresh() {
        if (stopped) return;
        executor.execute(() -> {
            String result;
            try {
                result = fetch();
            } catch (Exception ignored) {
                result = "Погода: нет соединения";
            }
            String text = result;
            view.post(() -> {
                if (!stopped) view.setText(text);
            });
        });
        handler.postDelayed(this::refresh, REFRESH_MS);
    }

    private String fetch() throws Exception {
        String query = URLEncoder.encode(city, StandardCharsets.UTF_8.name());
        JSONObject geocoding = getJson("https://geocoding-api.open-meteo.com/v1/search?name="
                + query + "&count=1&language=ru&format=json");
        JSONArray results = geocoding.optJSONArray("results");
        if (results == null || results.length() == 0) throw new IllegalStateException("city not found");
        JSONObject place = results.getJSONObject(0);
        double latitude = place.getDouble("latitude");
        double longitude = place.getDouble("longitude");
        JSONObject forecast = getJson("https://api.open-meteo.com/v1/forecast?latitude="
                + latitude + "&longitude=" + longitude
                + "&current=temperature_2m,weather_code&timezone=auto");
        JSONObject current = forecast.getJSONObject("current");
        int code = current.getInt("weather_code");
        double temperature = current.getDouble("temperature_2m");
        return String.format(Locale.US, "%s: %.0f°C, %s", city, temperature, description(code));
    }

    private static JSONObject getJson(String address) throws Exception {
        HttpURLConnection connection = (HttpURLConnection) new URL(address).openConnection();
        connection.setConnectTimeout(5_000);
        connection.setReadTimeout(5_000);
        connection.setRequestMethod("GET");
        connection.setRequestProperty("Accept", "application/json");
        try {
            if (connection.getResponseCode() != HttpURLConnection.HTTP_OK) {
                throw new IllegalStateException("weather request failed");
            }
            try (InputStream stream = connection.getInputStream();
                 BufferedReader reader = new BufferedReader(new InputStreamReader(stream, StandardCharsets.UTF_8))) {
                StringBuilder json = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) json.append(line);
                return new JSONObject(json.toString());
            }
        } finally {
            connection.disconnect();
        }
    }

    static String description(int code) {
        if (code == 0) return "ясно";
        if (code <= 3) return "облачно";
        if (code == 45 || code == 48) return "туман";
        if (code >= 51 && code <= 57) return "морось";
        if (code >= 61 && code <= 67) return "дождь";
        if (code >= 71 && code <= 77) return "снег";
        if (code >= 80 && code <= 82) return "ливень";
        if (code >= 85 && code <= 86) return "снегопад";
        if (code >= 95) return "гроза";
        return "переменная погода";
    }

    void stop() {
        stopped = true;
        handler.removeCallbacksAndMessages(null);
        executor.shutdownNow();
    }
}
