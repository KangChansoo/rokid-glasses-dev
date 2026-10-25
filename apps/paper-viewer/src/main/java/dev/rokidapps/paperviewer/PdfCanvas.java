package dev.rokidapps.paperviewer;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.ColorMatrixColorFilter;
import android.graphics.Paint;
import android.graphics.RectF;
import android.view.MotionEvent;
import android.view.View;
import dev.rokidapps.common.GlassesActivity;

/** White becomes black; dark PDF ink becomes green. Zoomed pages support mouse drag/wheel. */
public final class PdfCanvas extends View {
    private Bitmap bitmap;
    private long lastScrollLog;
    private float zoom = 1, panX, panY, lastX, lastY;
    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG | Paint.FILTER_BITMAP_FLAG);
    private final RectF destination = new RectF();
    public PdfCanvas(Context context) {
        super(context);
        setContentDescription("PDF 페이지. 확대 후 드래그하거나 휠로 이동");
        paint.setColorFilter(new ColorMatrixColorFilter(new float[]{
            -.05336f, -.17950f, -.01812f, 0, 64,
            -.21260f, -.71520f, -.07220f, 0, 255,
            -.07837f, -.26364f, -.02661f, 0, 94,
            0, 0, 0, 1, 0
        }));
        setBackgroundColor(Color.BLACK); setClickable(true);
    }
    public void display(Bitmap next, float factor, boolean resetPan) {
        bitmap = next; zoom = factor;
        if (resetPan) { panX = 0; panY = 0; }
        invalidate();
        // Let GC release previously displayed bitmaps: RenderThread may still hold them.
    }
    private float scale() { return bitmap == null ? 1 : Math.min((float) getWidth() / bitmap.getWidth(), (float) getHeight() / bitmap.getHeight()) * zoom; }
    @Override protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        if (bitmap == null) return;
        float w = bitmap.getWidth() * scale(), h = bitmap.getHeight() * scale();
        panX = ReaderMath.clampPan(panX, w, getWidth()); panY = ReaderMath.clampPan(panY, h, getHeight());
        float left = (getWidth() - w) / 2 + panX, top = (getHeight() - h) / 2 + panY;
        destination.set(left, top, left + w, top + h);
        canvas.drawBitmap(bitmap, null, destination, paint);
    }
    @Override public boolean onTouchEvent(MotionEvent event) {
        switch (event.getActionMasked()) {
            case MotionEvent.ACTION_DOWN: lastX = event.getX(); lastY = event.getY(); return true;
            case MotionEvent.ACTION_MOVE:
                panX += event.getX() - lastX; panY += event.getY() - lastY;
                lastX = event.getX(); lastY = event.getY(); invalidate(); return true;
            case MotionEvent.ACTION_UP:
                GlassesActivity.trace(getContext(), "pdf_pan x=" + Math.round(panX) + " y=" + Math.round(panY));
                performClick(); return true;
            case MotionEvent.ACTION_CANCEL: return true;
            default: return super.onTouchEvent(event);
        }
    }
    @Override public boolean onGenericMotionEvent(MotionEvent event) {
        if (event.getAction() == MotionEvent.ACTION_SCROLL && bitmap != null) {
            panY += event.getAxisValue(MotionEvent.AXIS_VSCROLL) * 45;
            panX += event.getAxisValue(MotionEvent.AXIS_HSCROLL) * 45;
            if (event.getEventTime() - lastScrollLog >= 200) {
                GlassesActivity.trace(getContext(), "pdf_scroll horizontal=" + event.getAxisValue(MotionEvent.AXIS_HSCROLL)
                        + " vertical=" + event.getAxisValue(MotionEvent.AXIS_VSCROLL));
                lastScrollLog = event.getEventTime();
            }
            invalidate(); return true;
        }
        return super.onGenericMotionEvent(event);
    }
    @Override public boolean performClick() { return super.performClick(); }
}
