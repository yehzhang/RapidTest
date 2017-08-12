import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class DecodeWays {
    public int numDecodings(String s) {
        if (s.isEmpty()) {
            return 0;
        }

        int[] decodeWays = new int[s.length() + 1];
        decodeWays[0] = 1;
        for (int i = 0; i < s.length(); i++) {
            if (i >= 1) {
                if (isValidValue(s.substring(i - 1, i + 1))) {
                    decodeWays[i + 1] += decodeWays[i - 1];
                }
            }
            if (isValidValue(s.substring(i, i + 1))) {
                decodeWays[i + 1] += decodeWays[i];
            }
        }
        return decodeWays[s.length()];
    }

    boolean isValidValue(String s) {
        if (s.startsWith("0")) {
            return false;
        }
        int value = Integer.valueOf(s);
        return 1 <= value && value <= 26;
    }
}
