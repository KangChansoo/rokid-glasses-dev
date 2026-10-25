package dev.rokidapps.common;

import android.app.Activity;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.StateListDrawable;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;

/** Ordinary Android controls: mouse click, focus/Enter and system Back remain native. */
public abstract class GlassesActivity extends Activity {
    public static final int GREEN = Color.rgb(64, 255, 94);
    protected LinearLayout shell;
    protected FrameLayout content;
    protected TextView title, status;

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
        shell = new LinearLayout(this);
        shell.setOrientation(LinearLayout.VERTICAL);
        shell.setBackgroundColor(Color.BLACK);
        int height = getResources().getDisplayMetrics().heightPixels;
        shell.setPadding(dp(12), height / 8, dp(12), height / 8);
        title = text(18); title.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        shell.addView(title, new LinearLayout.LayoutParams(-1, -2));
        content = new FrameLayout(this);
        LinearLayout.LayoutParams body = new LinearLayout.LayoutParams(-1, 0, 1);
        body.topMargin = dp(4); body.bottomMargin = dp(4);
        shell.addView(content, body);
        status = text(12); status.setMaxLines(2);
        shell.addView(status, new LinearLayout.LayoutParams(-1, dp(36)));
        setContentView(shell);
    }
    protected int dp(float value) { return Math.round(value * getResources().getDisplayMetrics().density); }
    protected TextView text(int size) {
        TextView view = new TextView(this);
        view.setTextColor(GREEN); view.setTextSize(size);
        return view;
    }
    protected LinearLayout row() {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(-1, dp(38));
        params.topMargin = dp(4); shell.addView(row, params);
        return row;
    }
    protected Button button(LinearLayout row, String label, Runnable action) {
        Button button = new Button(this);
        button.setId(View.generateViewId());
        button.setText(label); button.setTextSize(14); button.setAllCaps(false);
        button.setTextColor(GREEN); button.setGravity(Gravity.CENTER);
        button.setMinWidth(0); button.setMinimumWidth(0);
        button.setMinHeight(0); button.setMinimumHeight(0);
        button.setPadding(dp(2), 0, dp(2), 0); button.setFocusable(true);
        StateListDrawable background = new StateListDrawable();
        background.addState(new int[]{android.R.attr.state_pressed}, border(0xff204020));
        background.addState(new int[]{android.R.attr.state_focused}, border(0xff163016));
        background.addState(new int[]{}, border(Color.BLACK));
        button.setBackground(background);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(0, -1, 1);
        params.setMargins(dp(2), 0, dp(2), 0); row.addView(button, params);
        button.setOnClickListener(view -> action.run());
        return button;
    }
    private GradientDrawable border(int fill) {
        GradientDrawable shape = new GradientDrawable();
        shape.setColor(fill); shape.setCornerRadius(dp(3)); shape.setStroke(dp(1), GREEN);
        return shape;
    }
    protected void say(String message) { status.setText(message); }
}
