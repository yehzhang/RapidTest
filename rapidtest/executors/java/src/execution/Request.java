package execution;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;


public class Request {
    Request(String method, Object[] params, String id) {
        countRequests++;
        this.method = method;
        this.params = (params == null) ? new Object[0] : params;
        this.id = id;
    }

    Request(String method, Object[] params, boolean notification) {
        this(method, params, notification ? null : REQUEST_ID_PREFIX + countRequests);
    }

    @SuppressWarnings("unchecked")
    <T> Object invoke(T o, Reflection reflection) throws NoSuchMethodException,
            InvocationTargetException, IllegalAccessException {
        Method meth = reflection.getMethod(o, method, params);
        method = meth.getName();
        return reflection.invoke(o, meth, params);
    }

    @Override
    public String toString() {
        String paramStr = Utils.join(", ", params);
        return String.format("%s(%s)", method, paramStr);
    }

    String method;
    Object[] params;
    String id;

    public static final String REQUEST_ID_PREFIX = "Java_target_request_";

    private static int countRequests;
}
