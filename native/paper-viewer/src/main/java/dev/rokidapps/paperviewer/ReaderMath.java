package dev.rokidapps.paperviewer;

/** Bounds shared by UI and renderer; independent of Android for executable tests. */
public final class ReaderMath {
    public static final long MAX_PIXELS = 4_000_000;
    public static final long MAX_PDF_BYTES = 200L * 1024 * 1024;
    private ReaderMath() {}
    public static int clampPage(int requested, int count) { return Math.max(0, Math.min(Math.max(0, count - 1), requested)); }
    public static int[] renderSize(int pw, int ph, int vw, int vh, float zoom) {
        if (pw <= 0 || ph <= 0 || vw <= 0 || vh <= 0 || !Float.isFinite(zoom) || zoom <= 0) throw new IllegalArgumentException("Invalid render bounds");
        double scale = Math.min((double) vw / pw, (double) vh / ph) * zoom;
        scale = Math.min(scale, 4096.0 / Math.max(pw, ph));
        scale = Math.min(scale, Math.sqrt((double) MAX_PIXELS / ((double) pw * ph)));
        return new int[]{Math.max(1, (int) Math.floor(pw * scale)), Math.max(1, (int) Math.floor(ph * scale))};
    }
    public static float clampPan(float offset, float image, float viewport) {
        float limit = Math.max(0, (image - viewport) / 2);
        return Math.max(-limit, Math.min(limit, offset));
    }
}
