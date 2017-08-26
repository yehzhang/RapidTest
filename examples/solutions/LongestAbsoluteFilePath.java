import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class LongestAbsoluteFilePath {
    public int lengthLongestPath(String input) {
        int maxLength = 0;
        int dirLength = 0;
        Stack<Integer> pathLengths = new Stack<>();
        pathLengths.push(dirLength);
        for (String line : input.split("\n")) {
            int indentation = line.lastIndexOf("\t") + 1;

            int currLevel = indentation + 1;
            if (currLevel > pathLengths.size()) {
                pathLengths.push(dirLength);
            }
            else {
                while (currLevel < pathLengths.size()) {
                    dirLength = pathLengths.pop();
                }
            }

            String entity = line.substring(indentation);
            int currLength = pathLengths.peek() + (pathLengths.size() == 1 ? "" : "/").length() + entity.length();
            if (entity.contains(".")) {
                // File
                maxLength = Math.max(maxLength, currLength);
            }
            else {
                // Directory
                dirLength = currLength;
            }
        }

        return maxLength;
    }
}
