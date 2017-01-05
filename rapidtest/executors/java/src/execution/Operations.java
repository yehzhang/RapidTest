package execution;

import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;
import java.util.List;

public class Operations extends Request {
    public Operations(Request initOperation, List<Request> operations, boolean inPlace, String
            requestMethod, String requestId) {
        super(requestMethod, new Object[0], requestId);
        this.initOperation = initOperation;
        this.operations = operations;
        this.inPlace = inPlace;
    }

    /**
     * @return Output of executing target
     */
    <T> Object execute(Class<T> target) throws InvocationTargetException,
            NoSuchMethodException, InstantiationException, IllegalAccessException {
        T instance = newInstance(target);
        return invoke(instance);
    }

    @Override
    <T> Object invoke(T instance) throws NoSuchMethodException,
            InvocationTargetException, IllegalAccessException {
        List<Object> output = new ArrayList<>();
        for (Request op : operations) {
            Object ret = op.invoke(instance);
            output.add(inPlace ? op.params : ret);
        }
        return output;
    }

    @Override
    <T> T newInstance(Class<T> target) throws NoSuchMethodException, IllegalAccessException,
            InvocationTargetException, InstantiationException {
        return initOperation.newInstance(target);
    }

    @Override
    public String toString() {
        return "operations: " + Utils.join("\n", operations.stream());
    }

    String[] listExecutedMethods() {
        return operations.stream().map(op -> op.method).toArray(String[]::new);
    }

    final Request initOperation;
    final List<Request> operations;
    final boolean inPlace;
}
