package execution;

import java.io.PrintWriter;
import java.io.StringWriter;

@SuppressWarnings({"FieldCanBeLocal", "unused"})
public class Response {
    public Response(Throwable ex, String requestId) {
        this(requestId);

        StringWriter writer = new StringWriter();
        ex.printStackTrace(new PrintWriter(writer));
        this.error = writer.toString();
    }

    public Response(Object result, String requestId) {
        this(requestId);
        this.result = result;
    }

    private Response(String requestId) {
        if (requestId == null) {
            throw new IllegalArgumentException("Request is not specified or is a notification");
        }
        id = requestId;
    }

    private Response() {
    }

    private Object result;
    private String error;
    private String id;
}
