import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class ReversePairs {
    public int reversePairs(int[] nums) {
        if (nums == null) {
            return 0;
        }
        return count(nums, 0, nums.length - 1);
    }

    int count(int[] nums, int indexStart, int indexEnd) {
        if (indexStart >= indexEnd) {
            return 0;
        }
        int indexMid = (indexStart + indexEnd) / 2;
        int subCount = count(nums, indexStart, indexMid) + count(nums, indexMid + 1, indexEnd);

        int j = indexMid + 1;
        for (int i = indexStart; i <= indexMid; i++) {
            while (j <= indexEnd) {
                long twiceNumJ = 2L * nums[j];
                if (!(nums[i] > twiceNumJ)) {
                    break;
                }
                j++;
            }
            subCount += j - (indexMid + 1);
        }

        merge(nums, indexStart, indexMid, indexMid + 1, indexEnd);
        return subCount;
    }

    void merge(int[] nums, int indexLeft, int indexLeftEnd, int indexRight, int indexRightEnd) {
        int[] left = Arrays.copyOfRange(nums, indexLeft, indexLeftEnd + 1);
        int[] right = Arrays.copyOfRange(nums, indexRight, indexRightEnd + 1);
        int iLeft = indexLeft;
        int iRight = indexRight;
        for (int i = indexLeft; i <= indexRightEnd; i++) {
            if (iLeft > indexLeftEnd) {
                nums[i] = right[iRight++ - indexRight];
                continue;
            }
            if (iRight > indexRightEnd) {
                nums[i] = left[iLeft++ - indexLeft];
                continue;
            }
            if (left[iLeft - indexLeft] < right[iRight - indexRight]) {
                nums[i] = left[iLeft++ - indexLeft];
            }
            else {
                nums[i] = right[iRight++ - indexRight];
            }
        }
    }
}
