package execution;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.function.Supplier;
import java.util.stream.Collectors;

import static execution.StaticConfig.CANNOT_GUESS;
import static execution.Utils.Tuple;

public class Reflection {
    Reflection() {
        methodsCache = new HashMap<>();
        ctorsCache = new HashMap<>();
    }

    private Constructor<?> guessConstructor(Class<?> clazz) {
        List<Constructor<?>> ctors = Arrays.stream(clazz.getDeclaredConstructors())
                .filter(ctor -> Modifier.isPublic(ctor.getModifiers()))
                .collect(Collectors.toList());
        if (ctors.size() == 1) {
            return ctors.get(0);
        }
        throw new IllegalArgumentException(CANNOT_GUESS);
    }

    Constructor<?> getConstructor(Class<?> clazz) {
        return putIfAbsent(ctorsCache, clazz, () -> guessConstructor(clazz));
    }

    /**
     * Instantiate clazz with init_args by the constructor of corresponding signature
     */
    Object newInstance(Class<?> clazz, Object[] params) throws NoSuchMethodException,
            IllegalAccessException, InvocationTargetException, InstantiationException {
        return getConstructor(clazz).newInstance(params);
    }

    Object invoke(Object o, Method method, Object[] params) throws InvocationTargetException,
            IllegalAccessException {
        try {
            return method.invoke(o, params);
        } catch (IllegalArgumentException ignored) {
        }

        String fmt = "%s(%s) got parameter types (%s)";
        String expected = Utils.join(", ", Class::getSimpleName, method.getParameterTypes());
        String got = Utils.join(", ", Class::getSimpleName, asTypes(params));
        String msg = String.format(fmt, method.getName(), expected, got);
        throw new IllegalArgumentException(msg);
    }


    Method getMethod(Object o, String name, Object[] params) throws NoSuchMethodException {
        return getMethod(o.getClass(), name, asTypes(params));
    }

    /**
     * Return the method to execute according to its name and parameter types.
     * In case methodName or types is null, a method of best matching is returned.
     */
    Method getMethod(Class<?> clazz, String name, Class[] types) throws NoSuchMethodException {
        try {
            return getMethod(clazz, name);
        } catch (IllegalArgumentException ignored) {
        }
        return clazz.getMethod(name, types);
    }

    Method getMethod(Class<?> clazz, String name) {
        return putIfAbsent(methodsCache, new Tuple<>(clazz, name),
                () -> guessMethod(clazz, (name == null) ? str -> true : name::equals));
    }

    /**
     * Find the unique public method declared in clazz
     */
    private Method guessMethod(Class<?> clazz, Function<String, Boolean> isSameName) {
        Method[] methods = Arrays.stream(clazz.getDeclaredMethods())
                .filter(meth -> {
                    String methName = meth.getName();
                    int mods = meth.getModifiers();
                    // Is different name?
                    if (!isSameName.apply(methName)) {
                        return false;
                    }
                    // Is not public?
                    if (!Modifier.isPublic(mods)) {
                        return false;
                    }
                    // Is main?
                    if (Modifier.isStatic(mods) &&
                            meth.getReturnType() == Void.TYPE &&
                            methName.equals("main") &&
                            Arrays.equals(meth.getParameterTypes(), MAIN_PARAM_TYPES)) {
                        return false;
                    }
                    return true;
                })
                .toArray(Method[]::new);

        if (methods.length == 1) {
            return methods[0];
        }

        throw new IllegalArgumentException(CANNOT_GUESS);
    }

    private static Class[] asTypes(Object[] objs) {
        return Arrays.stream(objs).map(Object::getClass).toArray(Class[]::new);
    }

    private <K, V> V putIfAbsent(Map<K, V> mapping, K key, Supplier<V> supplier) {
        if (mapping.containsKey(key)) {
            return mapping.get(key);
        }
        V value = supplier.get();
        mapping.put(key, value);
        return value;
    }

    private Map<Tuple<Class, String>, Method> methodsCache;
    private Map<Class, Constructor<?>> ctorsCache;

    private static final Class[] MAIN_PARAM_TYPES = new Class[]{String[].class};
}
