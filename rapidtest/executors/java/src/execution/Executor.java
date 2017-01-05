package execution;

import java.io.Closeable;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;

import static execution.StaticConfig.METHOD_EXECUTE;


public class Executor implements Closeable {
    public Executor() throws IOException {
        reflection = new Reflection();
        json = new Json(reflection);
        server = new ExecutionRPCServer(json);
    }

    public <T> boolean run(Class<T> target) throws IOException {
        json.setTarget(target);

        server.sayHello();

        while (true) {
            Operations operations = null;

            try {
                operations = server.receive(Operations.class);
                if (operations == null) {
                    return true;
                }
                switch (operations.method) {
                    case METHOD_EXECUTE:
                        Object output = operations.execute(target, reflection);
                        // Return method names
                        output = new Object[]{operations.listExecutedMethods(), output};
                        server.respond(output, operations);
                        break;
                    default:
                        return true;
                }
            } catch (InvocationTargetException | InstantiationException | NoSuchMethodException |
                    IllegalAccessException e) {
                server.respond(e, operations);
            } catch (Exception e) {
                if (operations == null) {
                    throw e;
                }
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
    Reflection reflection;
    Json json;
}
