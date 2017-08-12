import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class MaximumLengthOfPairChain {
    public int findLongestChain(int[][] pairs) {
        Arrays.sort(pairs, (pair, other) -> pair[1] - other[1]);
        int head = Integer.MIN_VALUE;
        int chainLength = 0;
        for (int[] pair : pairs) {
            if (head < pair[0]) {
                head = pair[1];
                chainLength++;
            }
        }
        return chainLength;
    }
}
