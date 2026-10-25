package dev.rokidapps.common;

import android.app.Activity;
import android.content.Context;
import android.content.pm.ApplicationInfo;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.StateListDrawable;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
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
        DisplayMetrics metrics = getResources().getDisplayMetrics();
        trace("create display=" + metrics.widthPixels + "x" + metrics.heightPixels
                + " dpi=" + metrics.densityDpi + " fontScale=" + getResources().getConfiguration().fontScale);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON | WindowManager.LayoutParams.FLAG_FULLSCREEN);
        getWindow().setDecorFitsSystemWindows(false);
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
    @Override public void onWindowFocusChanged(boolean focused) {
        super.onWindowFocusChanged(focused);
        if (focused) {
            WindowInsetsController controller = getWindow().getInsetsController();
            if (controller != null) {
                controller.setSystemBarsBehavior(WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
                controller.hide(WindowInsets.Type.systemBars());
            }
        }
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
        button.setOnClickListener(view -> {
            trace("button=" + label);
            action.run();
        });
        return button;
    }
    private GradientDrawable border(int fill) {
        GradientDrawable shape = new GradientDrawable();
        shape.setColor(fill); shape.setCornerRadius(dp(3)); shape.setStroke(dp(1), GREEN);
        return shape;
    }
    // Fixed event names and numeric state only. Never pass document text, URIs or filenames.
    public static void trace(Context context, String event) {
        if ((context.getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE) != 0) {
            Log.i("RokidApp", context.getPackageName() + " " + event);
        }
    }
    protected void trace(String event) { trace(this, event); }
    @Override protected void onResume() { super.onResume(); trace("resume"); }
    @Override protected void onPause() { trace("pause"); super.onPause(); }
    @Override protected void onDestroy() { trace("destroy"); super.onDestroy(); }
    @Override public boolean dispatchKeyEvent(KeyEvent event) {
        int key = event.getKeyCode();
        if (event.getRepeatCount() == 0 && (key == KeyEvent.KEYCODE_BACK
                || key == KeyEvent.KEYCODE_ENTER || key == KeyEvent.KEYCODE_DPAD_CENTER
                || (key >= KeyEvent.KEYCODE_DPAD_UP && key <= KeyEvent.KEYCODE_DPAD_RIGHT)
                || key == KeyEvent.KEYCODE_TAB || key == KeyEvent.KEYCODE_PAGE_UP
                || key == KeyEvent.KEYCODE_PAGE_DOWN)) {
            trace("key=" + KeyEvent.keyCodeToString(key) + " " + (event.getAction() == KeyEvent.ACTION_DOWN ? "down" : "up"));
        }
        return super.dispatchKeyEvent(event);
    }
    @Override public boolean dispatchTouchEvent(MotionEvent event) {
        if (event.getActionMasked() == MotionEvent.ACTION_UP) {
            trace("pointer_up x=" + Math.round(event.getX()) + " y=" + Math.round(event.getY()));
        }
        return super.dispatchTouchEvent(event);
    }
    protected void say(String message) { status.setText(message); }
}
