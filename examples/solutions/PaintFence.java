import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class Solution {
    public int numWays(int n, int k) {
        if (n == 0 || k == 0) {
            return 0;
        }
        if (n == 1) {
            return k;
        }

        int countSameColor = k * 1;
        int countDifferentColor = k * (k - 1);
        for (int i = 2; i < n; i++) {
            int nextCountDifferentColor = countDifferentColor * (k - 1) + countSameColor * (k - 1);
            int nextSameDifferentColor = countDifferentColor;
            countDifferentColor = nextCountDifferentColor;
            countSameColor = nextSameDifferentColor;
        }
        return countSameColor + countDifferentColor;
    }
}
