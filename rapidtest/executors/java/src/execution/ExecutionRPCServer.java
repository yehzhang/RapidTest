package execution;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.io.BufferedReader;
import java.io.Closeable;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.io.Reader;
import java.net.Socket;

import static execution.StaticConfig.HOST_ADDR;
import static execution.StaticConfig.HOST_PORT;
import static execution.StaticConfig.METHOD_HELLO;
import static execution.StaticConfig.TARGET_ID;

public class ExecutionRPCServer implements Closeable {
    public ExecutionRPCServer() throws IOException {
        GsonBuilder builder = new GsonBuilder();
        gson = builder.registerTypeAdapter(Operations.class, new Operations.Deserializer())
                .create();

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
        Request request = new Request(METHOD_HELLO, new Object[]{TARGET_ID}, true);
        send(request);
    }

    public void respond(Exception exc, Request request) {
        send(new Response(exc, request));
    }

    public void respond(Object result, Request request) {
        send(new Response(result, request));
    }

    protected <T extends Request> T receive(Class<T> clazz) throws IOException {
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
            System.out.println("Java received empty");
            return null;
        }
        String data = buffer.toString();
        System.out.println("Java received data: " + data);
        return gson.fromJson(data, clazz);
    }

    protected void send(Object o) {
        String data = gson.toJson(o);
        if (data.isEmpty()) {
            return;
        }

        // Prepend length to socket
        out.print(data.length());
        out.print(" ");

        out.print(data);
        out.flush();
        System.out.println("Java sent data: " + data);
    }

    @Override
    public void close() throws IOException {
        socket.close();
    }

    private Socket socket;
    private PrintWriter out;
    private Reader in;
    private Gson gson;
}