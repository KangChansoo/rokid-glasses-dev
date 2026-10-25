package dev.rokidapps.adbhelper;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import dev.rokidapps.common.GlassesActivity;

/** Opens only documented Settings actions. Never writes settings or starts an ADB daemon. */
public final class MainActivity extends GlassesActivity {
    private TextView details;
    private String lastRequest;

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        title.setText(R.string.title);
        lastRequest = state == null ? getString(R.string.idle)
                : state.getString("lastRequest", getString(R.string.idle));
        ScrollView scroll = new ScrollView(this);
        details = text(16);
        details.setPadding(0, dp(6), 0, dp(6));
        scroll.addView(details);
        content.addView(scroll);

        LinearLayout first = row();
        Button developer = button(first, getString(R.string.developer),
                () -> open(Settings.ACTION_APPLICATION_DEVELOPMENT_SETTINGS, R.string.developer));
        button(first, getString(R.string.wifi), () -> open(Settings.ACTION_WIFI_SETTINGS, R.string.wifi));
        LinearLayout second = row();
        button(second, getString(R.string.device_info),
                () -> open(Settings.ACTION_DEVICE_INFO_SETTINGS, R.string.device_info));
        button(second, getString(R.string.settings), () -> open(Settings.ACTION_SETTINGS, R.string.settings));
        LinearLayout third = row();
        button(third, getString(R.string.refresh), this::refresh);
        button(third, getString(R.string.exit), this::finish);
        refresh();
        developer.requestFocus();
    }

    private void open(String action, int label) {
        try {
            startActivity(new Intent(action));
            lastRequest = getString(R.string.dispatched, getString(label));
        } catch (ActivityNotFoundException unavailable) {
            lastRequest = getString(R.string.missing, getString(label));
        } catch (SecurityException denied) {
            lastRequest = getString(R.string.denied, getString(label));
        }
        refresh();
    }

    private void refresh() {
        if (details == null) return;
        String summary = getString(R.string.summary, Build.MODEL, Build.VERSION.RELEASE,
                Build.VERSION.SDK_INT);
        details.setText(getString(R.string.body, summary, lastRequest, getString(R.string.guide)));
        say(getString(R.string.status));
    }

    @Override protected void onResume() { super.onResume(); refresh(); }
    @Override protected void onSaveInstanceState(Bundle state) {
        super.onSaveInstanceState(state);
        state.putString("lastRequest", lastRequest);
    }
}
