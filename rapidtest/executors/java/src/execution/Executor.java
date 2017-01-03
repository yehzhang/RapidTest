package execution;

import java.io.Closeable;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;

import static execution.StaticConfig.METHOD_EXECUTE;


public class Executor implements Closeable {
    public Executor() throws IOException {
        server = new ExecutionRPCServer();
    }

    public <T> boolean run(Class<T> target) throws IOException {
        server.sayHello();

        while (true) {
            Operations operations = server.receive(Operations.class);
            if (operations == null) {
                return true;
            }

            try {
                switch (operations.method) {
                    case METHOD_EXECUTE:
                        Object output = operations.execute(target);
                        server.respond(output, operations);
                        break;
                    default:
                        return true;
                }
            } catch (InvocationTargetException e) {
                server.respond(e.getCause(), operations);
            } catch (Exception e) {
                server.respond(e, operations);
                return false;
            }
        }
    }

    @Override
    public void close() throws IOException {
        server.close();
    }

    ExecutionRPCServer server;
}
