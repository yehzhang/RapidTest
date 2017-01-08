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
import com.google.gson.JsonPrimitive;
import com.google.gson.JsonSerializationContext;
import com.google.gson.JsonSerializer;

import java.lang.reflect.Constructor;
import java.lang.reflect.Executable;
import java.lang.reflect.Method;
import java.lang.reflect.Type;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Json {
    Json(Reflection reflection, List<Class<?>> dependencies) {
        gson = new GsonBuilder()
                .registerTypeAdapter(Deserializable.class, new DefaultDeserializer())
                .registerTypeAdapter(Request.class, new RequestDeserializer())
                .registerTypeAdapter(Serializable.class, new SerializableSerializer())
                .setFieldNamingPolicy(FieldNamingPolicy.LOWER_CASE_WITH_UNDERSCORES)
                .create();

        this.reflection = reflection;

        dependencies.add(Request.class);
        this.dependencies = new HashMap<>();
        for (Class<?> dependency : dependencies) {
            this.dependencies.put(dependency.getSimpleName(), dependency);
        }
    }

    String dump(Object o) {
        return gson.toJson(o);
    }

    <T> T load(String data, Class<T> clazz) {
        return gson.fromJson(data, clazz);
    }

    Gson gson;
    Reflection reflection;
    Map<String, Class<?>> dependencies;


    abstract class BaseDeserializer<T> implements JsonDeserializer<T> {
        Object[] castToCallableParameterTypes(JsonElement params, Executable exe,
                                              JsonDeserializationContext context) {
            JsonArray arr = params.isJsonNull() ? null : params.getAsJsonArray();
            int arrSize = (arr == null) ? 0 : arr.size();
            Class[] types = exe.getParameterTypes();
            if (arrSize != types.length) {
                String msg = String.format("%s takes %d arguments but %d were given", exe.getName(),
                        types.length, arrSize);
                throw new IllegalArgumentException(msg);
            }

            // Cast each object to its corresponding parameter type in method signature
            Object[] paramsArr = new Object[types.length];
            try {
                for (int i = 0; i < types.length; i++) {
                    JsonElement param = arr.get(i);

                    // Check if it is an External Object
                    Type hint;
                    if (param.isJsonObject() && param.getAsJsonObject().has("__jsonclass__")) {
                        hint = Deserializable.class;
                    }
                    else {
                        hint = types[i];
                    }

                    paramsArr[i] = context.deserialize(param, hint);
                }
            } catch (Exception e) {
                String fmt = "%s() takes parameters of types \"%s\"";
                String expected = Utils.join(", ", Class::getSimpleName, types);
                String msg = String.format(fmt, exe.getName(), expected);
                throw new IllegalArgumentException(msg, e);
            }
            return paramsArr;
        }

        Class<?> getDependency(String name) {
            Class<?> clazz = dependencies.get(name);
            if (clazz == null) {
                throw new RuntimeException("Class named \"" + name + "\" not found");
            }
            return clazz;
        }

        String toCamelCase(String name) {
            String[] words = name.split("_");
            StringBuilder sb = new StringBuilder(words[0].toLowerCase());
            for (int i = 1; i < words.length; i++) {
                sb.append(Character.toUpperCase(words[i].charAt(0)))
                        .append(words[i].substring(1).toLowerCase());
            }
            return sb.toString();
        }
    }


    class DefaultDeserializer extends BaseDeserializer<Object> {
        @Override
        public Object deserialize(JsonElement json, Type typeOfT, JsonDeserializationContext
                context) throws JsonParseException {
            JsonObject obj = json.getAsJsonObject();
            JsonElement jsonClass = obj.remove("__jsonclass__");
            if (jsonClass == null) {
                return context.deserialize(obj, Object.class);
            }
            JsonArray jsonClassArr = jsonClass.getAsJsonArray();

            // Deserialize to object of a certain type
            JsonArray instantiator = jsonClassArr.get(0).getAsJsonArray();
            String className = instantiator.get(0).getAsString();
            Class<?> clazz = getDependency(className);
            JsonElement jsonParams = jsonClassArr.get(1);
            if (jsonParams.isJsonNull()) {
                // Directly deserialize
                return context.deserialize(obj, clazz);
            }
            else {
                // Note that parameter are cast to correct types only if they are used to
                // instantiate an object
                int paramsCount = jsonParams.getAsJsonArray().size();
                JsonElement jsonCallableName = instantiator.get(1);
                try {
                    if (jsonCallableName.isJsonNull()) {
                        // Call constructor
                        Constructor ctor = reflection.guessConstructor(clazz, paramsCount);
                        Object[] params = castToCallableParameterTypes(jsonParams, ctor, context);
                        return ctor.newInstance(params);
                    }
                    else {
                        // Call static factory method
                        String callableName = toCamelCase(jsonCallableName.getAsString());
                        Method factory = reflection.guessMethod(clazz, callableName, true,
                                paramsCount);
                        Object[] params = castToCallableParameterTypes(jsonParams, factory,
                                context);
                        return factory.invoke(null, params);
                    }
                } catch (Exception e) {
                    throw new RuntimeException("Cannot instantiate \"" + className + "\"", e);
                }
            }
        }
    }

    class RequestDeserializer extends BaseDeserializer<Request> {
        @Override
        public Request deserialize(JsonElement json, Type typeOfT, JsonDeserializationContext
                context) throws JsonParseException {
            JsonObject request = json.getAsJsonObject();

            String id = getString(request, "id");

            String method;
            Object[] paramsArr;
            JsonElement jsonMethod = request.get("method");
            JsonElement paramsElem = request.get("params");
            JsonArray params = (paramsElem == null) ? new JsonArray() : paramsElem.getAsJsonArray();
            if (jsonMethod.isJsonArray()) {
                // Calls method
                JsonArray qualifiedName = jsonMethod.getAsJsonArray();
                String targetName = qualifiedName.get(0).getAsString();
                Class<?> target = getDependency(targetName);
                method = getString(qualifiedName.get(1));
                Method callingMethod = reflection.guessMethod(target, method, false, params.size());
                method = callingMethod.getName();
                paramsArr = castToCallableParameterTypes(params, callingMethod, context);
            }
            else {
                // Does not call method
                method = jsonMethod.getAsString();
                paramsArr = context.deserialize(params, Deserializable[].class);
            }

            return new Request(method, paramsArr, id);
        }

        String getString(JsonObject json, String key) {
            JsonElement elem = json.get(key);
            return elem == null ? null : getString(elem);
        }

        String getString(JsonElement json) {
            return json.isJsonNull() ? null : json.getAsString();
        }
    }

    public interface Deserializable {
    }

    interface Serializable extends java.io.Serializable {
        default Map<String, ? extends java.io.Serializable> getAttributes() {
            throw new RuntimeException("not implemented error");
        }

        default List<? extends java.io.Serializable> getParams() {
            throw new RuntimeException("not implemented error");
        }

        boolean isAttributes();

        String getName();
    }

    class SerializableSerializer implements JsonSerializer<Serializable> {

        @Override
        public JsonElement serialize(Serializable o, Type type, JsonSerializationContext
                jsonSerializationContext) {
            JsonElement params = o.isAttributes() ? serialize(o.getAttributes()) : serialize(o
                    .getParams());

            JsonArray constructorArr = new JsonArray();
            constructorArr.add(o.getName());
            constructorArr.add(params);

            JsonObject obj = new JsonObject();
            obj.add("__jsonclass__", constructorArr);
            return obj;
        }

        JsonElement serialize(Map<String, ? extends java.io.Serializable> m) {
            JsonObject params = new JsonObject();
            for (Map.Entry<String, ? extends java.io.Serializable> e : m.entrySet()) {
                java.io.Serializable v = e.getValue();
                params.add(e.getKey(), serialize(v));
            }
            return params;
        }

        JsonElement serialize(List<? extends java.io.Serializable> list) {
            JsonArray params = new JsonArray();
            for (java.io.Serializable item : list) {
                params.add(serialize(item));
            }
            return params;
        }

        JsonPrimitive serialize(java.io.Serializable s) {
            if (s instanceof Number) {
                return new JsonPrimitive((Number) s);
            }
            else if (s instanceof String) {
                return new JsonPrimitive((String) s);
            }
            else if (s instanceof Boolean) {
                return new JsonPrimitive((Boolean) s);
            }
            else if (s instanceof Character) {
                return new JsonPrimitive((Character) s);
            }
            else {
                return new JsonPrimitive(s.toString());
            }
        }
    }
}
