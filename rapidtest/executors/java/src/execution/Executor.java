package execution;

import java.io.Closeable;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Logger;

import static execution.StaticConfig.LOGGING_LEVEL;
import static execution.StaticConfig.METHOD_EXECUTE;
import static execution.StaticConfig.TARGET_CLASS;


class Executor implements Closeable {
    Executor() {
        Logger.getLogger("").setLevel(LOGGING_LEVEL);

        reflection = new Reflection();

        List<Class<?>> dependencies = new ArrayList<>();
        dependencies.add(TARGET_CLASS);
        dependencies.add(Operations.class);
        dependencies.add(Dependencies.ListNode.class);
        dependencies.add(Dependencies.TreeNode.class);
        server = new ExecutionRPCServer(new Json(reflection, dependencies));
    }

    boolean run() throws IOException {
        server.connect();

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
