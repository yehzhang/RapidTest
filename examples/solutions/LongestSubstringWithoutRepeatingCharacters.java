import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class LongestSubstringWithoutRepeatingCharacters {
    public int lengthOfLongestSubstring(String s) {
        char[] chars = s.toCharArray();
        int r = 0;
        int l = 0;
        Set<Character> existingChars = new HashSet<>();
        int longest = 0;
        while (r < s.length()) {
            while (r < s.length() && !existingChars.contains(chars[r])) {
                existingChars.add(chars[r]);
                r++;
            }

            longest = Math.max(longest, existingChars.size());

            existingChars.remove(chars[l]);
            l++;
        }
        return longest;
    }
}