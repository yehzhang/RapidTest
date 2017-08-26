import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class NextGreaterElementII {
    public int[] nextGreaterElements(int[] nums) {
        int[] res = new int[nums.length];
        Arrays.fill(res, -1);

        nums = doubleNums(nums);

        Stack<Integer> stack = new Stack<>();
        for (int i = 0; i < nums.length; i++) {
            int num = nums[i];
            while (!stack.isEmpty() && nums[stack.peek()] < num) {
                int smallerIndex = stack.pop();
                res[smallerIndex % res.length] = num;
            }
            stack.push(i);
        }

        return res;
    }

    int[] doubleNums(int[] nums) {
        int[] newNums = new int[nums.length * 2];
        System.arraycopy(nums, 0, newNums, 0, nums.length);
        System.arraycopy(nums, 0, newNums, nums.length, nums.length);
        return newNums;
    }
}