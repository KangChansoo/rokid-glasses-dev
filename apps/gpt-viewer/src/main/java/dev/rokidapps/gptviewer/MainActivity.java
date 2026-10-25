package dev.rokidapps.gptviewer;

import android.os.Bundle;
import android.view.KeyEvent;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import dev.rokidapps.common.GlassesActivity;

public final class MainActivity extends GlassesActivity {
    private static final String[] PAGES = {
        "Hello World!\n안녕하세요.\n안경에서 실행되는 Android APK입니다.",
        "[가상 답변]\n워치 포인터로 아래 버튼을 눌러 보세요.\n실제 OpenAI API 연결은 아직 없습니다.",
        "[가상 답변]\nChatGPT 앱의 기존 대화는 이 앱과 별개입니다.\n뒤로가기로 종료할 수 있습니다."
    };
    private int page, taps;
    private TextView answer;
    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        title.setText("GPT Viewer · APK DEMO");
        ScrollView scroll = new ScrollView(this);
        answer = text(21); answer.setPadding(0, dp(8), 0, dp(8));
        scroll.addView(answer); content.addView(scroll);
        LinearLayout controls = row();
        Button next = button(controls, "다음", () -> move(1));
        button(controls, "이전", () -> move(-1));
        button(controls, "처음", () -> { page = 0; taps = 0; show(); });
        button(controls, "종료", this::finish);
        if (state != null) { page = Math.max(0, Math.min(2, state.getInt("page"))); taps = state.getInt("taps"); }
        show(); next.requestFocus();
    }
    private void move(int delta) { page = Math.max(0, Math.min(PAGES.length - 1, page + delta)); taps++; show(); }
    private void show() { answer.setText(PAGES[page]); say((page + 1) + " / " + PAGES.length + " · 클릭 " + taps); }
    @Override public boolean onKeyUp(int code, KeyEvent event) {
        if (code == KeyEvent.KEYCODE_PAGE_DOWN) { move(1); return true; }
        if (code == KeyEvent.KEYCODE_PAGE_UP) { move(-1); return true; }
        return super.onKeyUp(code, event);
    }
    @Override protected void onSaveInstanceState(Bundle out) { super.onSaveInstanceState(out); out.putInt("page", page); out.putInt("taps", taps); }
}
