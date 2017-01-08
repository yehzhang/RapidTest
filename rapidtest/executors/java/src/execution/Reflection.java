package execution;

import java.lang.reflect.Constructor;
import java.lang.reflect.Executable;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Predicate;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static execution.StaticConfig.CANNOT_GUESS;
import static execution.Utils.Tuple2;
import static execution.Utils.Tuple4;

class Reflection {
    Reflection() {
        methodsCache = new HashMap<>();
        ctorsCache = new HashMap<>();
    }

    Constructor<?> guessConstructor(Class<?> clazz, int paramsCount) {
        return putIfAbsent(ctorsCache, new Tuple2<>(clazz, paramsCount), () -> {
            List<Predicate<? super Constructor>> predicates = new ArrayList<>();
            predicates.add(IS_NOT_PRIVATE);
            predicates.add(hasSameParametersCount(paramsCount));
            return guessOne(clazz.getDeclaredConstructors(), predicates);
        });
    }

    Method getMethod(Object o, String name, Object[] params) throws NoSuchMethodException {
        return getMethod(o.getClass(), name, params);
    }

    /**
     * Return the method to execute according to its name and parameter types.
     * In case methodName or types is null, a method of best matching is returned.
     */
    Method getMethod(Class<?> clazz, String name, Object[] params) throws NoSuchMethodException {
        try {
            return guessMethod(clazz, name, false, params.length);
        } catch (IllegalArgumentException ignored) {
        }
        return clazz.getMethod(name, asTypes(params)); // cache?
    }

    Method guessMethod(Class<?> clazz, String name, boolean isFactory, int paramsCount) {
        return putIfAbsent(methodsCache, new Tuple4<>(clazz, name, isFactory, paramsCount), () -> {
            List<Predicate<? super Method>> predicates = new ArrayList<>();
            if (name != null) {
                predicates.add(meth -> meth.getName().equals(name));
            }
            predicates.add(isFactory ? IS_NOT_PRIVATE : IS_PUBLIC);
            predicates.add(isFactory ? IS_STATIC : IS_STATIC.negate());
            predicates.add(hasSameParametersCount(paramsCount));
            predicates.add(IS_NOT_MAIN);
            return guessOne(clazz.getDeclaredMethods(), predicates);
        });
    }

    private <T> T guessOne(T[] items, List<Predicate<? super T>> predicates) {
        Stream<T> stream = Arrays.stream(items);
        for (Predicate<? super T> predicate : predicates) {
            stream = stream.filter(predicate);
        }
        List<T> results = stream.collect(Collectors.toList());
        if (results.size() == 1) {
            return results.get(0);
        }
        throw new IllegalArgumentException(CANNOT_GUESS);
    }

    private static Class[] asTypes(Object[] objs) {
        return Arrays.stream(objs).map(Object::getClass).toArray(Class[]::new);
    }

    private <K, V> V putIfAbsent(Map<K, V> mapping, K key, Supplier<V> supplier) {
        if (mapping.containsKey(key)) {
            V val = mapping.get(key);
            if (val == null) {
                throw new IllegalArgumentException("exception has thrown last time");
            }
            return val;
        }

        V value;
        try {
            value = supplier.get();
            assert value != null;
        } catch (Exception e) {
            mapping.put(key, null);
            throw e;
        }
        mapping.put(key, value);
        return value;
    }

    private Predicate<Executable> hasSameParametersCount(int count) {
        return meth -> meth.getParameterCount() == count;
    }

    private Map<Tuple4<Class, String, Boolean, Integer>, Method> methodsCache;
    private Map<Tuple2<Class, Integer>, Constructor<?>> ctorsCache;

    private static final Predicate<Executable> IS_NOT_PRIVATE = exe -> !Modifier.isPrivate(exe
            .getModifiers());
    private static final Predicate<Executable> IS_PUBLIC = exe -> Modifier.isPublic(exe
            .getModifiers());
    private static final Predicate<Method> IS_NOT_MAIN = meth ->
            !(Modifier.isStatic(meth.getModifiers()) &&
                    meth.getReturnType() == Void.TYPE &&
                    meth.getName().equals("main") &&
                    Arrays.equals(meth.getParameterTypes(), new Class[]{String[].class}));
    private static final Predicate<Method> IS_STATIC = meth -> Modifier.isStatic(meth
            .getModifiers());
}
