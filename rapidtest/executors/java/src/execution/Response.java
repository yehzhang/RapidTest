package execution;

import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.HashMap;
import java.util.Map;

@SuppressWarnings({"FieldCanBeLocal", "unused"})
public class Response {
    public Response(Throwable ex, Request request) {
        this(request);

        Map<String, Object> ctorArgs = new HashMap<>();

        ctorArgs.put("name", ex.getClass().getSimpleName());
        ctorArgs.put("message", ex.getMessage());

        StringWriter writer = new StringWriter();
        ex.printStackTrace(new PrintWriter(writer));
        String trace = writer.toString();
        trace = trace.substring(trace.indexOf("\n") + 1);
        ctorArgs.put("stack_trace", trace);

        ctorArgs.put("runtime", ex instanceof RuntimeException);

        this.error = destructToJsonPrimitives("ExternalException", ctorArgs, null);
    }

    public Response(Object result, Request request) {
        this(request);
        this.result = result;
    }

    private Response(Request request) {
        if (request == null || request.id == null) {
            throw new IllegalArgumentException("Request is not specified or is a notification");
        }
        id = request.id;
    }

    private Response() {
    }

    static Object destructToJsonPrimitives(String typeName, Object constructorParams, Map<String,
            Object> attributes) {
        Map<String, Object> obj = (attributes == null) ? new HashMap<>() : new HashMap<>
                (attributes);
        obj.put("__jsonclass__", new Object[]{typeName, constructorParams});
        return obj;
    }

    private Object result;
    private Object error;
    private String id;
}
