package execution;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;


public class Request {
    Request(String method, Object[] params, String id) {
        countRequests++;
        this.method = method;
        this.params = params;
        this.id = id;
    }

    Request(String method, Object[] params, boolean notification) {
        this(method, params, notification ? null : REQUEST_ID_PREFIX + countRequests);
    }

    @SuppressWarnings("unchecked")
    <T> Object invoke(T o) throws NoSuchMethodException, InvocationTargetException,
            IllegalAccessException {
        Method meth = reflection.getMethod(o, method, params);
        method = meth.getName();
        return reflection.invoke(o, meth, params);
    }

    /**
     * Instantiate clazz with init_args by the constructor of corresponding signature
     */
    <T> T newInstance(Class<T> clazz) throws NoSuchMethodException, IllegalAccessException,
            InvocationTargetException, InstantiationException {
        return reflection.newInstance(clazz, params);
    }

    @Override
    public String toString() {
        String paramStr = Utils.join(", ", params);
        return String.format("%s(%s)", method, paramStr);
    }

    String method;
    Object[] params;
    String id;

    static Reflection reflection = new Reflection();

    public static final String REQUEST_ID_PREFIX = "Java_target_request_";

    private static int countRequests;
}
