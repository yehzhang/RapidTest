package execution;

import java.lang.reflect.InvocationTargetException;
import java.util.Arrays;

import static execution.StaticConfig.REQUEST_ID_PREFIX;

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
    Object invoke(Class clazz, Object o) throws NoSuchMethodException, InvocationTargetException,
            IllegalAccessException {
        return clazz.getMethod(method, getParamTypes()).invoke(o, params);
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

    String method;
    Object[] params;
    String id;

    private static int countRequests;
}
