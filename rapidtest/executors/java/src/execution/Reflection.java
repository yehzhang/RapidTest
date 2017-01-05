package execution;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Supplier;

import static execution.StaticConfig.CANNOT_GUESS;

public class Reflection {
    Reflection() {
        defaultMethodCache = new HashMap<>();
        methodsCache = new HashMap<>();
    }

    <T> T newInstance(Class<T> clazz, Object[] params) throws NoSuchMethodException,
            IllegalAccessException, InvocationTargetException, InstantiationException {
        return getConstructor(clazz, params).newInstance(params);
    }


    <T> Method getMethod(Object o, String name, Object[] params) {
        return getMethod(o.getClass(), name, asTypes(params));
    }

    /**
     * Return the method to execute according to its name and parameter types.
     * In case methodName or types is null, a method of best matching is returned.
     */
    <T> Method getMethod(Class<T> clazz, String name, Class[] types) {
        if (name == null) {
            return putIfAbsent(defaultMethodCache, clazz,
                    () -> guessMethod(clazz, ANY_NAME, types));
        }
        try {
            return clazz.getMethod(name, types);
        } catch (NoSuchMethodException ignored) {
            return guessMethod(clazz, name, types);
        }
    }

    Object invoke(Object o, Method method, Object[] params) throws InvocationTargetException,
            IllegalAccessException {
        try {
            return method.invoke(o, params);
        } catch (IllegalArgumentException e) {
            String fmt = "%s(%s) got parameter types (%s)";
            String expected = Utils.join(", ", Class::getSimpleName, method.getParameterTypes());
            String got = Utils.join(", ", Class::getSimpleName, asTypes(params));
            String msg = String.format(fmt, method.getName(), expected, got);
            throw new IllegalArgumentException(msg);
        }
    }

    private <T> Method guessMethod(Class<T> clazz, Object nameComparator, Class[] types) {
        // Filter possible methods from declared methods
        Method[] methods = putIfAbsent(methodsCache, clazz, () -> {
            // TODO find all methods in all super classes?
            Method[] meths = clazz.getDeclaredMethods();
            return Arrays.stream(meths)
                    .filter(meth -> {
                        String methName = meth.getName();
                        int mods = meth.getModifiers();
                        // Is different name?
                        if (!nameComparator.equals(methName)) {
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
        });
        if (methods.length == 1) {
            return methods[0];
        }

        // TODO Compare types and casting

        throw new IllegalArgumentException(CANNOT_GUESS);
    }


    private <T> Constructor<T> getConstructor(Class<T> clazz, Object[] params) throws
            NoSuchMethodException {
        return clazz.getConstructor(asTypes(params));
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

    private Map<Class, Method> defaultMethodCache;
    private Map<Class, Method[]> methodsCache;

    private static final Object ANY_NAME = new Any();
    private static final Class[] MAIN_PARAM_TYPES = new Class[]{String[].class};

    static class Any {
        @Override
        public boolean equals(Object obj) {
            return true;
        }
    }
}
