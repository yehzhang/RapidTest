import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class NextGreaterElementIII {
    public int nextGreaterElement(int n) {
        int[] nums = String.valueOf(n).chars().map(c -> c - '0').toArray();

        try {
            nextPermutation(nums);
        }
        catch (RuntimeException ignored) {
            return -1;
        }

        String nextGreaterElement = Arrays.stream(nums).boxed()
            .map(String::valueOf)
            .collect(Collectors.joining());
        try {
            return Integer.parseInt(nextGreaterElement);
        }
        catch (NumberFormatException ignored) {
            return -1;
        }
    }

    void nextPermutation(int[] nums) {
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

        throw new RuntimeException();
    }
}