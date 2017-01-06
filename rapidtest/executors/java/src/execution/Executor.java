package execution;

import java.io.Closeable;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;
import java.util.List;

import static execution.StaticConfig.METHOD_EXECUTE;
import static execution.StaticConfig.TARGET_CLASS;


public class Executor implements Closeable {
    public Executor() throws IOException {
        reflection = new Reflection();
        List<Class<?>> dependencies = new ArrayList<>();
        dependencies.add(TARGET_CLASS);
        server = new ExecutionRPCServer(reflection, dependencies);
    }

    public boolean run() throws IOException {
        server.sayHello();

        while (true) {
            Request request = null;

            try {
                request = server.receive();
                if (request == null) {
                    return true;
                }
                switch (request.method) {
                    case METHOD_EXECUTE:
                        Operations operations = (Operations) request.params[0];
                        Object output = operations.execute(reflection);
                        // Return method names
                        output = new Object[]{operations.listExecutedMethods(), output};
                        server.respond(output, request);
                        break;
                    default:
                        return true;
                }
            } catch (InvocationTargetException | NoSuchMethodException | IllegalAccessException e) {
                server.respond(e, request);
            } catch (Exception e) {
                if (request == null) {
                    throw e;
                }
                server.respond(e, request);
                return false;
            }
        }
    }

    @Override
    public void close() throws IOException {
        server.close();
    }

    ExecutionRPCServer server;
    Reflection reflection;
}
