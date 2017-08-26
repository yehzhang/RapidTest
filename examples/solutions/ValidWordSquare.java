import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class Solution {
    public boolean validWordSquare(List<String> words) {
        if (words.size() == 0) {
            return false;
        }
        int maxLength = words.stream().mapToInt(String::length).max().getAsInt();
        int side = Math.max(words.size(), maxLength);
        for (int i = 0; i < side - 1; i++) {
            for (int j = i + 1; j < side; j++) {
                if (!Objects.equals(getChar(words, i, j), getChar(words, j, i))) {
                    return false;
                }
            }
        }
        return true;
    }

    Character getChar(List<String> words, int i, int j) {
        if (i >= words.size()) {
            return null;
        }
        String line = words.get(i);
        if (j >= line.length()) {
            return null;
        }
        return line.charAt(j);
    }
}
