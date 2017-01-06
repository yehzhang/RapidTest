package execution;

import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import static execution.Json.Deserializable;

public class Operations implements Deserializable {
    /**
     * @return Output of executing target
     */
    Object execute(Reflection reflection) throws NoSuchMethodException,
            InvocationTargetException, IllegalAccessException {
        List<Object> output = new ArrayList<>();
        for (Request op : operations) {
            Object ret = op.invoke(targetInstance, reflection);
            output.add(inPlace ? op.params : ret);
        }
        return output;
    }

    @Override
    public String toString() {
        return "operations: " + Utils.join("\n", operations);
    }

    String[] listExecutedMethods() {
        return Arrays.stream(operations).map(op -> op.method).toArray(String[]::new);
    }

    Deserializable targetInstance;
    Request[] operations;
    boolean inPlace;
}
