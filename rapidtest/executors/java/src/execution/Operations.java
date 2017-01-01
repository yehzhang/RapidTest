package execution;

import com.google.gson.JsonDeserializationContext;
import com.google.gson.JsonDeserializer;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public class Operations extends Request {
    public Operations(Request initOperation, List<Request> operations, boolean inPlace, String
            requestMethod, String requestId) {
        super(requestMethod, null, requestId);
        this.initOperation = initOperation;
        this.operations = operations;
        this.inPlace = inPlace;
    }

    <T> Response execute(Class<T> target) throws InvocationTargetException,
            NoSuchMethodException, InstantiationException, IllegalAccessException {
        T instance = newInstance(target);
        Object output = invoke(target, instance);
        return new Response(output, id);
    }

    @Override
    Object invoke(Class target, Object instance) throws NoSuchMethodException,
            InvocationTargetException, IllegalAccessException {
        List<Object> output = new ArrayList<>();
        for (Request op : operations) {
            Object ret = op.invoke(target, instance);
            output.add(inPlace ? op.params : ret);
        }
        return output;
    }


    @Override
    <T> T newInstance(Class<T> target) throws NoSuchMethodException, IllegalAccessException,
            InvocationTargetException, InstantiationException {
        return initOperation.newInstance(target);
    }

    final Request initOperation;
    final List<Request> operations;
    final boolean inPlace;

    static class Deserializer implements JsonDeserializer<Operations> {

        @Override
        public Operations deserialize(JsonElement jsonElement, Type type,
                                      JsonDeserializationContext jsonDeserializationContext)
                throws JsonParseException {
            JsonObject request = jsonElement.getAsJsonObject();

            Iterator<JsonElement> iterParams = request.get("params").getAsJsonArray().iterator();

            JsonObject kwargs = iterParams.next().getAsJsonObject();
            Boolean inPlace = kwargs.get("in_place").getAsBoolean();

            Request initOperation = iterParams.hasNext() ? jsonDeserializationContext.deserialize
                    (iterParams.next(), Request.class) : null;
            List<Request> operations = new ArrayList<>();
            iterParams.forEachRemaining(param -> operations.add(jsonDeserializationContext
                    .deserialize(param, Request.class)));

            String method = request.get("method").getAsString();
            String id = request.get("id").getAsString();

            return new Operations(initOperation, operations, inPlace, method, id);
        }
    }
}
