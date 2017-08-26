import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class NextPermutation {
    public void nextPermutation(int[] nums) {
        for (int i = nums.length - 2; i >= 0; i--) {
            if (!(nums[i] < nums[i + 1])) {
                continue;
            }

            final int fi = i;
            int indexMinNum = IntStream.range(i + 1, nums.length).boxed()
                .filter(index -> nums[index] > nums[fi])
                .min(Comparator.comparingInt(index -> nums[index]))
                .get();

            int tmp = nums[i];
            nums[i] = nums[indexMinNum];
            nums[indexMinNum] = tmp;

            Arrays.sort(nums, i + 1, nums.length);

            return;
        }

        Arrays.sort(nums, 0, nums.length);
    }
}