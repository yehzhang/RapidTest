import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class TrappingRainWater {
    public int trap(int[] heights) {
        if (heights.length == 0) {
            return 0;
        }

        int rightMax = 0;
        int[] rightwardsDepths = new int[heights.length];
        for (int i = 0; i < heights.length; i++) {
            int height = heights[i];
            if (rightMax < height) {
                rightMax = height;
            }
            else {
                rightwardsDepths[i] = rightMax - height;
            }
        }

        int leftMax = 0;
        int[] leftwardsDepths = new int[heights.length];
        for (int i = heights.length - 1; i >= 0; i--) {
            int height = heights[i];
            if (leftMax < height) {
                leftMax = height;
            }
            else {
                leftwardsDepths[i] = leftMax - height;
            }
        }

        int sum = 0;
        for (int i = 0; i < heights.length; i++) {
            sum += Math.min(leftwardsDepths[i], rightwardsDepths[i]);
        }

        return sum;
    }
}
