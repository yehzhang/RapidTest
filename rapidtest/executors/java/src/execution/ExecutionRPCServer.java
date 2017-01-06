package execution;

import java.io.BufferedReader;
import java.io.Closeable;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.io.Reader;
import java.net.Socket;
import java.util.List;

import static execution.StaticConfig.HOST_ADDR;
import static execution.StaticConfig.HOST_PORT;
import static execution.StaticConfig.METHOD_HELLO;
import static execution.StaticConfig.TARGET_ID;

public class ExecutionRPCServer implements Closeable {
    public ExecutionRPCServer(Reflection reflection, List<Class<?>> dependencies) throws
            IOException {
        dependencies.add(Operations.class);
        this.json = new Json(reflection, dependencies);

        socket = new Socket(HOST_ADDR, HOST_PORT);
        try {
            out = new PrintWriter(socket.getOutputStream());
            in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        } catch (Exception e) {
            socket.close();
            throw e;
        }
    }

    void sayHello() {
        Request request = new Request(METHOD_HELLO, new Object[]{TARGET_ID});
        send(request);
    }

    public void respond(Exception exc, Request request) {
        send(Response.fromException(exc, request));
    }

    public void respond(Object result, Request request) {
        send(new Response(result, request));
    }

    protected Request receive() throws IOException {
        StringBuilder buffer = new StringBuilder();
        int dataLength = -1;

        while (dataLength == -1 || buffer.length() < dataLength) {
            int b = in.read();
            if (b == -1) {
                // Transmission ends before data is completely read
                dataLength = 0;
                break;
            }

            char c = (char) b;
            if (dataLength == -1) {
                if (c == ' ') {
                    dataLength = Integer.valueOf(buffer.toString());
                    buffer.setLength(0);
                    continue;
                }
            }

            buffer.append(c);
        }

        if (dataLength == 0) {
            return null;
        }
        String data = buffer.toString();

//        System.out.println("Java received: " + data);

        return json.load(data, Request.class);
    }

    protected void send(Object o) {
        String data = json.dump(o);
        if (data.isEmpty()) {
            return;
        }

        // Prepend length to socket
        out.print(data.length());
        out.print(" ");

        out.print(data);
        out.flush();

//        System.out.println("Java sent: " + data);
    }

    @Override
    public void close() throws IOException {
        socket.close();
    }

    private Socket socket;
    private PrintWriter out;
    private Reader in;
    private Json json;
}
