import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class ExcelSheetColumnTitle {
    public String convertToTitle(int n) {
        List<String> chars = new ArrayList<>();
        while (true) {
            n--;
            chars.add(String.valueOf((char) (n % 26 + 'A')));
            if (n < 26) {
                break;
            }
            n /= 26;
        }
        String revRes = chars.stream().collect(Collectors.joining());
        return new StringBuffer(revRes).reverse().toString();
    }
}
