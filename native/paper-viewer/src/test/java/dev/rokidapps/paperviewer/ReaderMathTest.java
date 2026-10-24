package dev.rokidapps.paperviewer;
import org.junit.Test;
import static org.junit.Assert.*;

public class ReaderMathTest {
    @Test public void pageBoundsIncludeEmptyAndPastEnd() {
        assertEquals(0, ReaderMath.clampPage(-1, 7));
        assertEquals(6, ReaderMath.clampPage(999, 7));
        assertEquals(0, ReaderMath.clampPage(4, 0));
    }
    @Test public void renderingCannotExceedMemoryBudgetEvenForHugePages() {
        for (int pw : new int[]{1, 595, 20000, Integer.MAX_VALUE}) {
            for (int ph : new int[]{1, 842, 20000, Integer.MAX_VALUE}) {
                int[] size = ReaderMath.renderSize(pw, ph, 480, 400, 3.2f);
                assertTrue(size[0] >= 1 && size[1] >= 1);
                assertTrue(size[0] <= 4096 && size[1] <= 4096);
                assertTrue((long) size[0] * size[1] <= ReaderMath.MAX_PIXELS);
            }
        }
    }
    @Test public void invalidRenderBoundsAreRejected() {
        assertThrows(IllegalArgumentException.class, () -> ReaderMath.renderSize(0, 842, 480, 400, 1));
        assertThrows(IllegalArgumentException.class, () -> ReaderMath.renderSize(595, 842, 480, 400, Float.NaN));
    }
    @Test public void panCannotLoseThePageOutsideTheViewport() {
        assertEquals(0, ReaderMath.clampPan(100, 200, 480), 0);
        assertEquals(260, ReaderMath.clampPan(10000, 1000, 480), 0);
        assertEquals(-260, ReaderMath.clampPan(-10000, 1000, 480), 0);
    }
}
