import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class FlipGame {
    public List<String> generatePossibleNextMoves(String s) {
        List<String> res = new ArrayList<>();
        if (s.length() <= 1) {
            return res;
        }

        StringBuilder sb = new StringBuilder(s);
        for (int i = 1; i < s.length(); i++) {
            if (sb.charAt(i) == '+' && sb.charAt(i - 1) == '+') {
                sb.setCharAt(i, '-');
                sb.setCharAt(i - 1, '-');
                res.add(sb.toString());
                sb.setCharAt(i, '+');
                sb.setCharAt(i - 1, '+');
            }
        }
        return res;
    }
}