import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class NextGreaterElementI {
    public int[] nextGreaterElement(int[] findNums, int[] nums) {
        int[] res = new int[findNums.length];
        Arrays.fill(res, -1);

        Map<Integer, Integer> numsIndices = new HashMap<>();
        for (int i = 0; i < findNums.length; i++) {
            int findNum = findNums[i];
            numsIndices.put(findNum, i);
        }

        Stack<Integer> stack = new Stack<>();
        stack.push(Integer.MAX_VALUE);
        for (int i = 0; i < nums.length; i++) {
            int num = nums[i];
            while (stack.peek() < num) {
                int smallerElement = stack.pop();
                if (numsIndices.containsKey(smallerElement)) {
                    int index = numsIndices.get(smallerElement);
                    res[index] = num;
                }
            }
            stack.push(num);
        }

        return res;
    }
}
