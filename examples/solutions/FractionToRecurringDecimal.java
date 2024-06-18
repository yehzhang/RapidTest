import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class FractionToRecurringDecimal {
    public String fractionToDecimal(int numerator, int denominator) {
        if (numerator == 0 && denominator != 0) {
            return "0";
        }

        String sign = "";
        long longNumerator = numerator;
        long longDenominator = denominator;
        if (longNumerator < 0 && longDenominator < 0) {
            longNumerator = longNumerator * -1;
            longDenominator *= -1;
        } else if (longNumerator < 0) {
            longNumerator *= -1;
            sign = "-";
        } else if (longDenominator < 0) {
            longDenominator *= -1;
            sign = "-";
        }

        long integerPart = longNumerator / longDenominator;

        return sign + integerPart + getFraction(longNumerator, longDenominator);
    }

    String getFraction(long longNumerator, long longDenominator) {
        long remainder = longNumerator % longDenominator;
        if (remainder == 0) {
            return "";
        }

        Map<Long, Integer> seenRemainders = new HashMap<>();
        List<String> digits = new ArrayList<>();
        int repeatingStartsAt = -1;
        while (true) {
            if (seenRemainders.containsKey(remainder)) {
                repeatingStartsAt = seenRemainders.get(remainder);
                break;
            }
            seenRemainders.put(remainder, digits.size());

            remainder *= 10;
            String segment = "" + remainder / longDenominator;
            digits.add(segment);
            remainder -= remainder / longDenominator * longDenominator;

            if (remainder == 0) {
                break;
            }
        }

        String result;
        if (repeatingStartsAt != -1) {
            result = digits.stream().limit(repeatingStartsAt).collect(Collectors.joining())
                + "("
                + digits.stream().skip(repeatingStartsAt).collect(Collectors.joining())
                + ")";
        } else {
            result = digits.stream().collect(Collectors.joining());
        }

        return "." + result;
    }
}
