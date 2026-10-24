package dev.rokidapps.paperviewer;

import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.pdf.PdfDocument;
import android.graphics.pdf.PdfRenderer;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.os.ParcelFileDescriptor;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.View;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;
import dev.rokidapps.common.GlassesActivity;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.util.Arrays;
import java.util.Comparator;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Local PDF files only. No internet, account, broad storage or vendor SDK permissions. */
public final class MainActivity extends GlassesActivity {
    private static final int PICK_PDF = 10;
    private static final float[] ZOOMS = {1f, 1.6f, 2.4f, 3.2f};
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private volatile boolean destroyed;
    private volatile int documentToken, renderToken;
    // Renderer belongs exclusively to the single worker thread.
    private PdfRenderer renderer;
    private PdfCanvas pageView;
    private TextView empty;
    private Button previous, next, zoomButton;
    private int pageIndex, pageCount, zoomIndex;
    private boolean loaded, isDemo;

    private interface Source { InputStream open() throws IOException; }

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        title.setText("Paper Viewer · PDF");
        pageView = new PdfCanvas(this); content.addView(pageView);
        empty = text(18);
        empty.setText("PDF 열기로 안경 안의 파일을 선택하세요.\n처음에는 데모로 표시를 확인할 수 있습니다.");
        empty.setGravity(Gravity.CENTER);
        content.addView(empty, new FrameLayout.LayoutParams(-1, -1));
        LinearLayout files = row();
        Button open = button(files, "PDF 열기", this::choosePdf);
        button(files, "앱 폴더", this::chooseAppFile);
        button(files, "데모", this::openDemo);
        LinearLayout controls = row();
        previous = button(controls, "이전", () -> move(-1));
        next = button(controls, "다음", () -> move(1));
        zoomButton = button(controls, "확대", this::toggleZoom);
        button(controls, "문서 제거", this::confirmClear);
        pageView.addOnLayoutChangeListener((v, l, t, r, b, ol, ot, or, ob) -> {
            if (loaded && (r - l != or - ol || b - t != ob - ot)) render(false);
        });
        say("원본 PDF 페이지 · 확대 후 드래그 · 뒤로가기로 종료");
        updateControls(); open.requestFocus();
        Uri uri = getIntent().getData();
        if (Intent.ACTION_VIEW.equals(getIntent().getAction()) && uri != null && "content".equals(uri.getScheme())) {
            importPdf(() -> getContentResolver().openInputStream(uri));
        } else if (currentFile().isFile()) {
            pageIndex = getPreferences(0).getInt("page", 0);
            openStored();
        }
    }

    private File currentFile() { return new File(getFilesDir(), "current.pdf"); }
    private boolean current(int token) { return !destroyed && documentToken == token; }
    private void ui(int token, Runnable action) { runOnUiThread(() -> { if (current(token)) action.run(); }); }
    private int beginLoad() {
        int token = ++documentToken; renderToken++;
        loaded = false; updateControls(); say("PDF를 읽는 중…");
        return token;
    }

    private void choosePdf() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("application/pdf");
        intent.putExtra(Intent.EXTRA_LOCAL_ONLY, true);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        try { startActivityForResult(intent, PICK_PDF); }
        catch (ActivityNotFoundException | SecurityException exception) {
            say("시스템 파일 선택기가 없습니다. 앱 폴더에서 PDF를 선택하세요.");
            chooseAppFile();
        }
    }
    @Override protected void onActivityResult(int request, int result, Intent data) {
        super.onActivityResult(request, result, data);
        if (request == PICK_PDF && result == RESULT_OK && data != null && data.getData() != null) {
            Uri uri = data.getData();
            importPdf(() -> getContentResolver().openInputStream(uri));
        }
    }

    private void chooseAppFile() {
        File folder = getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS);
        if (folder == null || (!folder.isDirectory() && !folder.mkdirs())) {
            say("앱 전용 문서 폴더를 열 수 없습니다."); return;
        }
        File[] files = folder.listFiles(file -> file.isFile() && file.getName().toLowerCase(java.util.Locale.ROOT).endsWith(".pdf"));
        if (files == null || files.length == 0) {
            new AlertDialog.Builder(this).setTitle("앱 전용 PDF 폴더")
                .setMessage("도구 상자의 파일 업로드에서 이 폴더를 선택할 수 있으면 PDF를 넣어 주세요.\n\n" + folder.getAbsolutePath() + "\n\n앱 밖의 폴더를 직접 검색하지 않습니다.")
                .setPositiveButton("확인", null).show();
            return;
        }
        Arrays.sort(files, Comparator.comparing(File::getName));
        String[] names = Arrays.stream(files).map(File::getName).toArray(String[]::new);
        new AlertDialog.Builder(this).setTitle("PDF 선택").setItems(names, (dialog, index) -> {
            File file = files[index];
            try {
                if (!file.getCanonicalFile().toPath().startsWith(folder.getCanonicalFile().toPath())) {
                    say("앱 폴더 밖의 파일은 열 수 없습니다."); return;
                }
                importPdf(() -> new FileInputStream(file));
            } catch (IOException exception) { say("PDF를 열 수 없습니다."); }
        }).setNegativeButton("취소", null).show();
    }

    private void importPdf(Source source) {
        int token = beginLoad();
        worker.execute(() -> {
            if (!current(token)) return;
            File pending = null;
            PdfRenderer candidate = null;
            try {
                pending = File.createTempFile("selected-", ".pdf", getCacheDir());
                try (InputStream input = source.open(); FileOutputStream output = new FileOutputStream(pending)) {
                    if (input == null) throw new IOException("No stream");
                    byte[] buffer = new byte[64 * 1024];
                    long total = 0; int count;
                    while ((count = input.read(buffer)) != -1) {
                        if (!current(token)) return;
                        total += count;
                        if (total > ReaderMath.MAX_PDF_BYTES) throw new IOException("PDF too large");
                        output.write(buffer, 0, count);
                    }
                }
                candidate = openRenderer(pending);
                if (!current(token)) return;
                // Replace only the app's private copy; never write to the selected original.
                Files.move(pending.toPath(), currentFile().toPath(), StandardCopyOption.REPLACE_EXISTING);
                closeRenderer(); renderer = candidate; candidate = null;
                final int pages = renderer.getPageCount();
                getPreferences(0).edit().putInt("page", 0).apply();
                ui(token, () -> ready(pages, 0, false));
            } catch (IOException | RuntimeException exception) {
                ui(token, () -> { loaded = false; updateControls(); say("PDF를 열지 못했습니다. 파일 접근·암호·손상 여부와 200MB 제한을 확인하세요."); });
            } finally {
                if (candidate != null) candidate.close();
                if (pending != null && pending.exists()) pending.delete();
            }
        });
    }

    private PdfRenderer openRenderer(File file) throws IOException {
        ParcelFileDescriptor descriptor = ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY);
        try { return new PdfRenderer(descriptor); }
        catch (IOException | RuntimeException exception) { descriptor.close(); throw exception; }
    }
    private void openStored() {
        int savedPage = pageIndex, token = beginLoad();
        worker.execute(() -> {
            if (!current(token)) return;
            try {
                PdfRenderer candidate = openRenderer(currentFile());
                closeRenderer(); renderer = candidate;
                int pages = renderer.getPageCount();
                ui(token, () -> ready(pages, savedPage, false));
            } catch (IOException | RuntimeException exception) { ui(token, () -> say("저장된 PDF를 열 수 없습니다. PDF 열기로 다시 선택하세요.")); }
        });
    }
    private void openDemo() {
        int token = beginLoad();
        worker.execute(() -> {
            if (!current(token)) return;
            File file = new File(getCacheDir(), "original-demo.pdf");
            try {
                PdfDocument document = new PdfDocument();
                try {
                    for (int number = 1; number <= 3; number++) {
                        PdfDocument.Page page = document.startPage(new PdfDocument.PageInfo.Builder(480, 640, number).create());
                        page.getCanvas().drawColor(Color.WHITE);
                        Paint ink = new Paint(Paint.ANTI_ALIAS_FLAG); ink.setColor(Color.BLACK); ink.setTextSize(28);
                        page.getCanvas().drawText("Paper Viewer - Demo " + number, 30, 65, ink);
                        ink.setTextSize(20);
                        page.getCanvas().drawText("Hello PDF! Original local demo.", 30, 120, ink);
                        page.getCanvas().drawText("No real paper is bundled.", 30, 160, ink);
                        page.getCanvas().drawText("Next / Previous / Zoom", 30, 200, ink);
                        page.getCanvas().drawText("확대 후 드래그해서 읽으세요.", 30, 240, ink);
                        ink.setStyle(Paint.Style.STROKE); ink.setStrokeWidth(3);
                        page.getCanvas().drawRect(30, 300, 450, 510, ink);
                        page.getCanvas().drawLine(30, 510, 450, 300, ink);
                        document.finishPage(page);
                    }
                    try (FileOutputStream output = new FileOutputStream(file)) { document.writeTo(output); }
                } finally { document.close(); }
                PdfRenderer candidate = openRenderer(file);
                closeRenderer(); renderer = candidate;
                ui(token, () -> ready(3, 0, true));
            } catch (IOException | RuntimeException exception) { ui(token, () -> say("데모 PDF 생성에 실패했습니다.")); }
        });
    }
    private void ready(int count, int page, boolean demo) {
        pageCount = count; pageIndex = ReaderMath.clampPage(page, count);
        zoomIndex = 0; isDemo = demo; loaded = true;
        empty.setVisibility(View.GONE);
        updateControls(); pageView.post(() -> render(true));
    }
    private void move(int delta) {
        if (!loaded) return;
        int page = ReaderMath.clampPage(pageIndex + delta, pageCount);
        if (page == pageIndex) return;
        pageIndex = page;
        if (!isDemo) getPreferences(0).edit().putInt("page", pageIndex).apply();
        updateControls(); render(true);
    }
    private void toggleZoom() {
        if (!loaded) return;
        zoomIndex = (zoomIndex + 1) % ZOOMS.length;
        updateControls(); render(true);
    }
    private void updateControls() {
        previous.setEnabled(loaded && pageIndex > 0);
        next.setEnabled(loaded && pageIndex + 1 < pageCount);
        zoomButton.setEnabled(loaded);
        zoomButton.setText(zoomIndex == 0 ? "확대" : String.format(java.util.Locale.ROOT, "%.1fx", ZOOMS[zoomIndex]));
    }

    private void render(boolean resetPan) {
        if (!loaded || destroyed || pageView.getWidth() <= 0 || pageView.getHeight() <= 0) return;
        int document = documentToken, sequence = ++renderToken, index = pageIndex;
        int width = pageView.getWidth(), height = pageView.getHeight(); float zoom = ZOOMS[zoomIndex];
        say((isDemo ? "DEMO · " : "PDF · ") + (index + 1) + " / " + pageCount + " · 읽는 중…");
        worker.execute(() -> {
            if (!current(document) || sequence != renderToken || renderer == null) return;
            Bitmap bitmap = null;
            try (PdfRenderer.Page page = renderer.openPage(index)) {
                int[] size = ReaderMath.renderSize(page.getWidth(), page.getHeight(), width, height, zoom);
                bitmap = Bitmap.createBitmap(size[0], size[1], Bitmap.Config.ARGB_8888);
                bitmap.eraseColor(Color.WHITE);
                page.render(bitmap, null, null, PdfRenderer.Page.RENDER_MODE_FOR_DISPLAY);
                Bitmap result = bitmap; bitmap = null;
                runOnUiThread(() -> {
                    if (!current(document) || sequence != renderToken) { result.recycle(); return; }
                    pageView.display(result, zoom, resetPan);
                    say((isDemo ? "DEMO · " : "PDF · ") + (index + 1) + " / " + pageCount + " · 확대 후 드래그/휠");
                });
            } catch (RuntimeException | OutOfMemoryError exception) {
                ui(document, () -> { if (sequence == renderToken) say("이 페이지를 표시하지 못했습니다. 다른 페이지나 작은 배율을 선택하세요."); });
            } finally { if (bitmap != null) bitmap.recycle(); }
        });
    }

    private void confirmClear() {
        new AlertDialog.Builder(this).setTitle("앱에 복사한 문서를 지울까요?")
            .setMessage("앱 내부 PDF와 읽던 위치를 지웁니다. 선택했던 원본 PDF는 그대로 있습니다.")
            .setPositiveButton("문서 제거", (dialog, which) -> clearDocument())
            .setNegativeButton("취소", null).show();
    }
    private void clearDocument() {
        int token = ++documentToken; renderToken++; loaded = false; pageIndex = 0;
        updateControls(); pageView.display(null, 1, true); empty.setVisibility(View.VISIBLE);
        getPreferences(0).edit().clear().apply();
        worker.execute(() -> {
            closeRenderer();
            boolean removed = !currentFile().exists() || currentFile().delete();
            ui(token, () -> say(removed ? "앱 내부 문서를 제거했습니다." : "앱 내부 문서를 제거하지 못했습니다."));
        });
    }
    private void closeRenderer() { if (renderer != null) { renderer.close(); renderer = null; } }
    @Override public boolean onKeyUp(int code, KeyEvent event) {
        if (code == KeyEvent.KEYCODE_PAGE_DOWN) { move(1); return true; }
        if (code == KeyEvent.KEYCODE_PAGE_UP) { move(-1); return true; }
        return super.onKeyUp(code, event);
    }
    @Override protected void onDestroy() {
        destroyed = true; documentToken++; renderToken++;
        pageView.display(null, 1, true);
        worker.execute(this::closeRenderer); worker.shutdown();
        super.onDestroy();
    }
}
