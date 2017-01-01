package execution;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.io.BufferedReader;
import java.io.Closeable;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.lang.reflect.InvocationTargetException;
import java.net.Socket;
import java.util.HashMap;
import java.util.Map;

import static execution.StaticConfig.HOST_ADDR;
import static execution.StaticConfig.HOST_PORT;
import static execution.StaticConfig.METHOD_EXECUTE;
import static execution.StaticConfig.METHOD_STOP;
import static execution.StaticConfig.WHO_I_AM;


public class Executor implements Closeable {
    public Executor() throws IOException {
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

    public <T> boolean run(Class<T> target) throws IOException {
        sayHello(target);

        while (true) {
            Operations operations = receive(Operations.class);
            try {
                switch (operations.method) {
                    case METHOD_STOP:
                        return true;
                    case METHOD_EXECUTE:
                        break;
                    default:
                        throw new AssertionError("Unknown method: " + operations.method);
                }
                Response output = operations.execute(target);
                send(output);
            } catch (InvocationTargetException e) {
                send(new Response(e.getCause(), operations.id));
            } catch (Exception e) {
                send(new Response(e, operations.id));
                return false;
            }
        }
    }

    @Override
    public void close() throws IOException {
        socket.close();
    }

    private void sayHello(Class target) {
        Map<String, Object> params = new HashMap<>();
        params.put("name", WHO_I_AM);
        params.put("target", target.getName());
        Request request = new Request(null, new Object[]{params}, true);
        send(request);
    }

    private <T extends Request> T receive(Class<T> clazz) throws IOException {
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = in.readLine()) != null) {
            sb.append(line);
        }

        return gson.fromJson(sb.toString(), clazz);
    }

    private void send(Object o) {
        out.print(gson.toJson(o));
    }

    private Gson gson;
    private Socket socket;
    private PrintWriter out;
    private BufferedReader in;
}
