import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class LongestSubstringwithAtMostTwoDistinctCharacters {
    public int lengthOfLongestSubstringTwoDistinct(String s) {
        char[] chars = s.toCharArray();
        int r = 0;
        int l = 0;
        Map<Character, Integer> existingCharsCounter = new HashMap<>();
        int longest = 0;
        while (r < s.length()) {
            while (r < s.length() &&
                   (existingCharsCounter.size() < 2 || existingCharsCounter.containsKey(chars[r]))) {
                existingCharsCounter.merge(chars[r], 1, (oldV, v) -> oldV + v);
                r++;
            }

            longest = Math.max(longest, existingCharsCounter.entrySet().stream().mapToInt(e -> e.getValue()).sum());

            while (existingCharsCounter.size() == 2) {
                existingCharsCounter.compute(chars[l], (k, v) -> --v == 0 ? null : v);
                l++;
            }
        }
        return longest;
    }
}