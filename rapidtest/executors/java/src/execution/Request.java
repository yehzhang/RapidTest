package execution;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;

import static execution.Json.Deserializable;

public class Request implements Deserializable {
    Request(String method, Object[] params, String id) {
        this.method = method;
        this.params = (params == null) ? new Object[0] : params;
        this.id = id;
    }

    Request(String method, Object[] params) {
        this(method, params, null);
    }

    @SuppressWarnings("unchecked")
    <T> Object invoke(T o, Reflection reflection) throws NoSuchMethodException,
            InvocationTargetException, IllegalAccessException {
        Method meth = reflection.getMethod(o, method, params);
        method = meth.getName();
        return meth.invoke(o, params);
    }

    @Override
    public String toString() {
        String paramStr = Utils.join(", ", params);
        return String.format("%s(%s)", method, paramStr);
    }

    String method;
    Object[] params;
    String id;
}
