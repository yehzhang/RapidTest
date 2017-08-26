import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class GeneralizedAbbreviation {
    public List<String> generateAbbreviations(String word) {
        List<String> abbrs = new ArrayList<>();
        dfs(abbrs, new StringBuilder(), word, 0, 0);
        return abbrs;
    }

    void dfs(List<String> abbrs, StringBuilder sb, String word, int currIndex, int cntPrevAbbred) {
        int prevBuilderLength = sb.length();
        if (currIndex == word.length()) {
            if (cntPrevAbbred != 0) {
                sb.append(cntPrevAbbred);
            }
            abbrs.add(sb.toString());
        }
        else {
            // Abbr
            dfs(abbrs, sb, word, currIndex + 1, cntPrevAbbred + 1);

            // Non-abbr
            if (cntPrevAbbred != 0) {
                sb.append(cntPrevAbbred);
            }
            sb.append(word.charAt(currIndex));
            dfs(abbrs, sb, word, currIndex + 1, 0);
        }
        sb.setLength(prevBuilderLength);
    }
}
