import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class PartitionEqualSubsetSum {
    public boolean canPartition(int[] nums) {
        int twoSetsSum = Arrays.stream(nums).sum();
        if (twoSetsSum % 2 == 1) {
            return false;
        }
        int setSum = twoSetsSum / 2;

        boolean[][] d = new boolean[nums.length + 1][setSum + 1];
        d[0][0] = true;

        for (int i = 1; i <= nums.length; i++) {
            int weight = nums[i - 1];
            for (int expectedWeight = 1; expectedWeight <= setSum; expectedWeight++) {
                d[i][expectedWeight] = d[i - 1][expectedWeight];
                if (expectedWeight - weight >= 0) {
                    d[i][expectedWeight] |= d[i - 1][expectedWeight - weight];
                }
            }
        }

        return d[nums.length][setSum];
    }
}
