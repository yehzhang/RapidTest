package execution;

import java.util.Arrays;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Stream;

public class Utils {
    static String join(String sep, Object[] objs) {
        return join(sep, Object::toString, objs);
    }

    static <T> String join(String sep, Stream<T> stream) {
        return join(sep, Object::toString, stream);
    }

    static <T> String join(String sep, Function<T, String> mapper, T[] obj) {
        return join(sep, mapper, Arrays.stream(obj));
    }

    static <T> String join(String sep, Function<T, String> mapper, Stream<T>
            stream) {
        String[] strs = stream.map(mapper).toArray(String[]::new);
        return String.join(sep, strs);
    }

    static class Tuple<A, B> {
        public Tuple(A a, B b) {
            this._1 = a;
            this._2 = b;
        }

        public final A _1;
        public final B _2;
    }
}
