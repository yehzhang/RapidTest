import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class DecodeWays2 {
    public int numDecodings(String s) {
        if (s.isEmpty()) {
            return 0;
        }

        long[] decodeWays = new long[s.length() + 1];
        decodeWays[0] = 1;
        for (int i = 0; i < s.length(); i++) {
            if (i >= 1) {
                decodeWays[i + 1] += decodeWays[i - 1] * getDecodeWaysMultiplier(s.substring(i - 1, i + 1));
                decodeWays[i + 1] %= 1000000007;
            }
            decodeWays[i + 1] += decodeWays[i] * getDecodeWaysMultiplier(s.substring(i, i + 1)) % 1000000007;
            decodeWays[i + 1] %= 1000000007;
        }
        return (int) decodeWays[s.length()];
    }

    int getDecodeWaysMultiplier(String s) {
        if (s.startsWith("0")) {
            return 0;
        }
        if (s.equals("**")) {
            return 15;
        }
        if (s.equals("*")) {
            return 9;
        }
        if (s.startsWith("*")) {
            int lastDigit = Integer.parseInt(s.substring(1));
            if (lastDigit > 6) {
                return 1;
            }
            return 2;
        }
        if (s.endsWith("*")) {
            int firstDigit = Integer.parseInt(s.substring(0, 1));
            if (firstDigit == 0) {
                return 0;
            }
            if (firstDigit == 1) {
                return 9;
            }
            if (firstDigit == 2) {
                return 6;
            }
            return 0;
        }
        int value = Integer.parseInt(s);
        return (1 <= value && value <= 26) ? 1 : 0;
    }
}
