package execution;

import java.util.Arrays;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Stream;

class Utils {
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

    static class Tuple2<A, B> {
        Tuple2(A a, B b) {
            _1 = a;
            _2 = b;
        }

        final A _1;
        final B _2;
    }

    static class Tuple3<A, B, C> {
        Tuple3(A a, B b, C c) {
            _1 = a;
            _2 = b;
            _3 = c;
        }

        final A _1;
        final B _2;
        final C _3;
    }

    static class Tuple4<A, B, C, D> {
        Tuple4(A a, B b, C c, D d) {
            _1 = a;
            _2 = b;
            _3 = c;
            _4 = d;
        }

        final A _1;
        final B _2;
        final C _3;
        final D _4;
    }

    static class PyObj implements Json.Serializable {
        PyObj(String name, Map<String, ? extends java.io.Serializable> attributes) {
            this.name = name;
            this.attributes = attributes;
        }

        @Override
        public boolean isAttributes() {
            return true;
        }

        @Override
        public Map<String, ? extends java.io.Serializable> getAttributes() {
            return attributes;
        }

        @Override
        public String getName() {
            return name;
        }

        final String name;
        final Map<String, ? extends java.io.Serializable> attributes;
    }
}
