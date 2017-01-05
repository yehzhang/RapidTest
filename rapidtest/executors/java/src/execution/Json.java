package execution;

import com.google.gson.FieldNamingPolicy;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonDeserializationContext;
import com.google.gson.JsonDeserializer;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;

import java.lang.reflect.Executable;
import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public class Json {
    Json(Reflection reflection) {
        gson = new GsonBuilder()
                .registerTypeAdapter(Operations.class, new OperationsDeserializer())
                .registerTypeAdapter(Request.class, new RequestDeserializer())
                .setFieldNamingPolicy(FieldNamingPolicy.LOWER_CASE_WITH_UNDERSCORES)
                .create();

        this.reflection = reflection;
    }

    String dump(Object o) {
        return gson.toJson(o);
    }

    <T> T load(String data, Class<T> clazz) {
        return gson.fromJson(data, clazz);
    }

    Json setTarget(Class<?> target) {
        this.target = target;
        return this;
    }

    private Gson gson;
    private Reflection reflection;
    private Class target;


    static String getOrNull(JsonObject json, String key) {
        JsonElement elem = json.get(key);
        return elem.isJsonNull() ? null : elem.getAsString();
    }

    private static Object[] castToCallableParameterTypes(JsonElement params, Executable exe,
                                                         JsonDeserializationContext context) {
        JsonArray arr = params.isJsonNull() ? null : params.getAsJsonArray();
        int arrSize = (arr == null) ? 0 : arr.size();
        Class[] types = exe.getParameterTypes();
        if (arrSize != types.length) {
            throw new IllegalArgumentException();
        }

        // Cast each object to its corresponding parameter type in method signature
        Object[] paramsArr = new Object[types.length];
        for (int i = 0; i < types.length; i++) {
            JsonElement param = arr.get(i);

            // Check if it is a Java Object
            if (param.isJsonObject()) {
                // TODO check if __jsonclass__. otherwise dict
                assert false;
                continue;
            }

            paramsArr[i] = context.deserialize(param, types[i]);
        }

        return paramsArr;
    }

    class OperationsDeserializer implements JsonDeserializer<Operations> {

        @Override
        public Operations deserialize(JsonElement json, Type typeOfT, JsonDeserializationContext
                context) throws JsonParseException {
            JsonObject request = json.getAsJsonObject();

            Iterator<JsonElement> iterParams = request.get("params").getAsJsonArray().iterator();

            JsonObject kwargs = iterParams.next().getAsJsonObject();
            Boolean inPlace = kwargs.get("in_place").getAsBoolean();


            Object[] initParams;
            try {
                initParams = castToCallableParameterTypes(kwargs.get("constructor"), reflection
                        .getConstructor(target), context);
            } catch (IllegalArgumentException ignored) {
                throw new RuntimeException("constructor is not an array");
            }

            List<Request> operations = new ArrayList<>();
            iterParams.forEachRemaining(param -> operations.add(context.deserialize(param,
                    Request.class)));

            String method = getOrNull(request, "method");
            String id = getOrNull(request, "id");

            return new Operations(initParams, operations, inPlace, method, id);
        }
    }

    class RequestDeserializer implements JsonDeserializer<Request> {

        @Override
        public Request deserialize(JsonElement json, Type typeOfT, JsonDeserializationContext
                context) throws JsonParseException {
            JsonObject request = json.getAsJsonObject();

            String method = getOrNull(request, "method");
            String id = getOrNull(request, "id");

            Object[] paramsArr;
            try {
                paramsArr = castToCallableParameterTypes(request.get("params"), reflection
                        .getMethod(target, method), context);
            } catch (IllegalArgumentException ignored) {
                throw new RuntimeException("params is not an array");
            }

            return new Request(method, paramsArr, id);
        }
    }
}
