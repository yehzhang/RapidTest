package execution;

import java.io.PrintWriter;
import java.io.StringWriter;
import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Map;

@SuppressWarnings({"FieldCanBeLocal", "unused"})
public class Response {
    Response(Object result, Request request) {
        this(result, null, request);
    }

    private Response(Object result, Object error, Request request) {
        if (request == null || request.id == null) {
            throw new IllegalArgumentException("Request is not specified or is a notification");
        }
        this.result = result;
        this.error = error;
        id = request.id;
    }

    static Response fromException(Throwable ex, Request request) {
        Map<String, Object> ctorArgs = new HashMap<>();

        StringWriter writer = new StringWriter();
        ex.printStackTrace(new PrintWriter(writer));
        String trace = writer.toString();
        trace = trace.substring(trace.indexOf("\n") + 1);
        ctorArgs.put("stack_trace", trace);

        boolean fromTarget;
        if (ex instanceof InvocationTargetException) {
            fromTarget = true;
            ex = ex.getCause();
        }
        else {
            fromTarget = false;
        }
        ctorArgs.put("from_target", fromTarget);

        ctorArgs.put("name", ex.getClass().getSimpleName());
        ctorArgs.put("message", ex.getMessage());

        Object error = destructToJsonPrimitives("ExternalException", ctorArgs, null);
        return new Response(null, error, request);
    }

    static Object destructToJsonPrimitives(String typeName, Object constructorParams, Map<String,
            Object> attributes) {
        // TODO move to serializer
        Map<String, Object> obj = (attributes == null) ? new HashMap<>() : new HashMap<>
                (attributes);
        obj.put("__jsonclass__", new Object[]{typeName, constructorParams});
        return obj;
    }

    final Object result;
    final Object error;
    final String id;
}
