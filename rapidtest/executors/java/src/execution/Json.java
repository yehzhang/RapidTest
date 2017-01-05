package execution;

import com.google.gson.FieldNamingPolicy;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonDeserializationContext;
import com.google.gson.JsonDeserializer;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import com.google.gson.JsonPrimitive;
import com.google.gson.TypeAdapter;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonToken;
import com.google.gson.stream.JsonWriter;

import java.io.IOException;
import java.io.Serializable;
import java.lang.reflect.Type;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.function.Function;

public class Json {
    Json() {
        GsonBuilder builder = new GsonBuilder();

        TypeAdapter primitiveTypeAdapter = new MostStrictNumberTypeAdaptor();
        gson = builder
                .registerTypeAdapter(Operations.class, new OperationsDeserializer())
                .registerTypeAdapter(Request.class, new RequestDeserializer())
                .registerTypeAdapter(Serializable.class, new MostStrictStringDeserializer())
                .registerTypeAdapter(Number.class, primitiveTypeAdapter)
                .registerTypeAdapter(byte.class, primitiveTypeAdapter)
                .registerTypeAdapter(short.class, primitiveTypeAdapter)
                .registerTypeAdapter(int.class, primitiveTypeAdapter)
                .registerTypeAdapter(long.class, primitiveTypeAdapter)
                .registerTypeAdapter(float.class, primitiveTypeAdapter)
                .registerTypeAdapter(double.class, primitiveTypeAdapter)
                .setFieldNamingPolicy(FieldNamingPolicy.LOWER_CASE_WITH_UNDERSCORES)
                .create();
    }

    String dump(Object o) {
        return gson.toJson(o);
    }

    <T> T load(String data, Class<T> clazz) {
        return gson.fromJson(data, clazz);
    }

    private Gson gson;

    static class OperationsDeserializer implements JsonDeserializer<Operations> {

        @Override
        public Operations deserialize(JsonElement json, Type typeOfT, JsonDeserializationContext
                context) throws JsonParseException {
            JsonObject request = json.getAsJsonObject();

            Iterator<JsonElement> iterParams = request.get("params").getAsJsonArray().iterator();

            JsonObject kwargs = iterParams.next().getAsJsonObject();
            Boolean inPlace = kwargs.get("in_place").getAsBoolean();

            Request initOperation = iterParams.hasNext() ? context.deserialize(iterParams.next(),
                    Request.class) : new Request(null, null, null);
            List<Request> operations = new ArrayList<>();
            iterParams.forEachRemaining(param -> operations.add(context.deserialize(param,
                    Request.class)));

            String method = RequestDeserializer.getAsStringOrNull(request, "method");
            String id = RequestDeserializer.getAsStringOrNull(request, "id");

            return new Operations(initOperation, operations, inPlace, method, id);
        }
    }

    static class RequestDeserializer implements JsonDeserializer<Request> {

        @Override
        public Request deserialize(JsonElement json, Type typeOfT, JsonDeserializationContext
                context) throws JsonParseException {
            JsonObject request = json.getAsJsonObject();

            String method = getAsStringOrNull(request, "method");
            String id = getAsStringOrNull(request, "id");

            JsonElement paramsElem = request.get("params");
            Object[] paramsArr;
            if (paramsElem.isJsonNull()) {
                paramsArr = new Object[0];
            }
            else {
                List<Object> params = new ArrayList<>();
                request.get("params").getAsJsonArray().iterator().forEachRemaining(param -> {
                    Class hint = Object.class;
                    if (param.isJsonPrimitive()) {
                        JsonPrimitive p = param.getAsJsonPrimitive();
                        if (p.isNumber()) {
                            hint = Number.class;
                        }
                        else if (p.isString()) {
                            hint = Serializable.class;
                        }
                    }
                    params.add(context.deserialize(param, hint));
                });
                paramsArr = params.toArray();
            }

            return new Request(method, paramsArr, id);
        }

        static String getAsStringOrNull(JsonObject json, String key) {
            JsonElement elem = json.get(key);
            return elem.isJsonNull() ? null : elem.getAsString();
        }
    }

    // Use Serializable to avoid objects and lists while including Number and String.
    // Also included Boolean TODO or is it?
    static class MostStrictNumberTypeAdaptor extends TypeAdapter<Number> {

        public MostStrictNumberTypeAdaptor() {
            numberParsers = new ArrayList<>();
            numberParsers.add(Byte::parseByte);
            numberParsers.add(Short::parseShort);
            numberParsers.add(Integer::parseInt);
            numberParsers.add(Long::parseLong);
            numberParsers.add(BigInteger::new);
            numberParsers.add(Float::parseFloat);
            numberParsers.add(Double::parseDouble);
            numberParsers.add(BigDecimal::new);
        }

        @Override
        public void write(JsonWriter out, Number o) throws IOException {
            if (o == null) {
                out.nullValue();
            }
            else {
                out.value(o);
            }
        }

        @Override
        public Number read(JsonReader in) throws IOException {
            JsonToken peek = in.peek();
            switch (peek) {
                case NUMBER:
                    return parseNumber(in.nextString());
                default:
                    throw new IllegalStateException("expected NUMBER or STRING types but was " +
                            peek);
            }
        }

        Number parseNumber(String data) {
            for (Function<String, Number> parser : numberParsers) {
                try {
                    return parser.apply(data);
                } catch (IllegalArgumentException ignored) {
                }
            }
            throw new IllegalArgumentException("expected number, got " + data);
        }

        List<Function<String, Number>> numberParsers;
    }

    // Use serializable as a hack to super both String and Character
    static class MostStrictStringDeserializer implements JsonDeserializer<Serializable> {
        @Override
        public Serializable deserialize(JsonElement json, Type typeOfT, JsonDeserializationContext
                context) throws JsonParseException {
            // assert only called with json string
            String s = json.getAsJsonPrimitive().getAsString();
            if (s.length() == 1) {
                return s.charAt(0);
            }
            return s;
        }
    }
}
