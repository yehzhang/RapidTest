package execution;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Predicate;
import java.util.function.Supplier;

import static execution.StaticConfig.CANNOT_GUESS;


public class Request {
    protected Request() {
        countRequests++;
    }

    public Request(String method, Object[] params, String id) {
        this();
        this.method = method;
        this.params = params;
        this.id = id;
    }

    public Request(String method, Object[] params, boolean notification) {
        this(method, params, notification ? null : REQUEST_ID_PREFIX + countRequests);
    }

    @SuppressWarnings("unchecked")
    <T> Object invoke(Class<T> clazz, T o) throws NoSuchMethodException,
            InvocationTargetException, IllegalAccessException {
        Method target = null;
        Method[] methods = null;
        if (method == null) {
            methods = putIfAbsent(defaultMethods, clazz,
                    () -> getDeclaredMethods(clazz, meth -> {
                        int mod = meth.getModifiers();
                        return Modifier.isPublic(mod) && !meth.getName().equals("main");
                    }));
        }
        else {
            try {
                target = clazz.getMethod(method, getParamTypes());
            } catch (NoSuchMethodException e) {
//                Map<String, Method> methods = putIfAbsent(classMethods, clazz, () -> {
//                    return new HashMap<>();
//                });

            }
        }

        if (target == null) {

            if (methods.length != 1) {
                throw new IllegalArgumentException(CANNOT_GUESS);
            }
            target = methods[0];
        }
        return target.invoke(o, params);
    }

    /**
     * Instantiate clazz with init_args by the constructor of corresponding signature
     */
    <T> T newInstance(Class<T> clazz) throws NoSuchMethodException, IllegalAccessException,
            InvocationTargetException, InstantiationException {
        return clazz.getConstructor(getParamTypes()).newInstance(params);
    }

    Class[] getParamTypes() {
        return Arrays.stream(params).map(Object::getClass).toArray(Class[]::new);
    }

    <T> Method[] getDeclaredMethods(Class<T> clazz, Predicate<Method> shouldGet) {
        return Arrays.stream(clazz.getDeclaredMethods()).filter(shouldGet).toArray(Method[]::new);
    }

    <K, V> V putIfAbsent(Map<K, V> mapping, K key, Supplier<V> supplier) {
        if (mapping.containsKey(key)) {
            return mapping.get(key);
        }
        V value = supplier.get();
        mapping.put(key, value);
        return value;
    }

    String method;
    Object[] params;
    String id;

    private static Map<Class, Method[]> defaultMethods = new HashMap<>();
    private static Map<Class, Map<String, Method>> classMethods = new HashMap<>();

    public static final String REQUEST_ID_PREFIX = "Java_target_request_";

    private static int countRequests;
}
