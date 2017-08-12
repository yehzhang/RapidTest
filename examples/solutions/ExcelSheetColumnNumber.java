import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class ExcelSheetColumnNumber {
    public int titleToNumber(String s) {
        int base = 1;
        int sum = 0;
        String revS = new StringBuilder(s).reverse().toString();
        for (char ch : revS.toCharArray()) {
            sum += (ch - 'A' + 1) * base;
            base *= 26;
        }
        return sum;
    }
}
