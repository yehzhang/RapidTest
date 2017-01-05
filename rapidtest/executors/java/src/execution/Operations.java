package execution;

import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;
import java.util.List;

public class Operations extends Request {
    public Operations(Object[] initParams, List<Request> operations, boolean inPlace, String
            requestMethod, String requestId) {
        super(requestMethod, null, requestId);
        this.initParams = initParams;
        this.operations = operations;
        this.inPlace = inPlace;
    }

    /**
     * @return Output of executing target
     */
    Object execute(Class<?> target, Reflection reflection) throws InvocationTargetException,
            NoSuchMethodException, InstantiationException, IllegalAccessException {
        return invoke(reflection.newInstance(target, initParams), reflection);
    }

    @Override
    Object invoke(Object instance, Reflection reflection) throws NoSuchMethodException,
            InvocationTargetException, IllegalAccessException {
        List<Object> output = new ArrayList<>();
        for (Request op : operations) {
            Object ret = op.invoke(instance, reflection);
            output.add(inPlace ? op.params : ret);
        }
        return output;
    }

    @Override
    public String toString() {
        return "operations: " + Utils.join("\n", operations.stream());
    }

    String[] listExecutedMethods() {
        return operations.stream().map(op -> op.method).toArray(String[]::new);
    }

    final Object[] initParams;
    final List<Request> operations;
    final boolean inPlace;
}
