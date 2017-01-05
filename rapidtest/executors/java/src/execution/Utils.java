package execution;

import java.util.Arrays;
import java.util.function.Function;
import java.util.stream.Stream;

public class Utils {
    public static String join(String sep, Object[] objs) {
        return join(sep, Object::toString, objs);
    }

    public static <T> String join(String sep, Stream<T> stream) {
        return join(sep, Object::toString, stream);
    }

    public static <T> String join(String sep, Function<T, String> mapper, T[] obj) {
        return join(sep, mapper, Arrays.stream(obj));
    }

    public static <T> String join(String sep, Function<T, String> mapper, Stream<T>
            stream) {
        String[] strs = stream.map(mapper).toArray(String[]::new);
        return String.join(sep, strs);
    }
}
