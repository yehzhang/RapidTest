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

import java.io.Serializable;
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
                .registerTypeAdapter(PyObj.class, new PyObjSerializer())
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

    private Gson gson;
    private Reflection reflection;
    private Map<String, Class<?>> dependencies;


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

                    // Check if it is a Java Object
                    if (param.isJsonObject()) {
                        // TODO check if __jsonclass__. otherwise dict
                        assert false;
                        continue;
                    }

                    paramsArr[i] = context.deserialize(param, types[i]);
                }
            } catch (Exception e) {
                String fmt = "%s() takes parameters of types (%s)";
                String expected = Utils.join(", ", Class::getSimpleName, types);
                String msg = String.format(fmt, exe.getName(), expected);
                throw new IllegalArgumentException(msg);
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

            // Deserialize to Object of a type
            String className = jsonClassArr.get(0).getAsString();
            Class<?> clazz = getDependency(className);
            JsonElement jsonParams = jsonClassArr.get(1);
            if (jsonParams.isJsonNull()) {
                // Directly deserialize
                return context.deserialize(obj, clazz);
            }
            else {
                // Call constructor
                // Note that parameter types are cast only if constructor is used
                Constructor<?> ctor = reflection.getConstructor(clazz);
                Object[] params = castToCallableParameterTypes(jsonParams, ctor, context);
                try {
                    return ctor.newInstance(params);
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
            JsonArray params = request.get("params").getAsJsonArray();
            if (jsonMethod.isJsonArray()) {
                // Calls method
                JsonArray qualifiedName = jsonMethod.getAsJsonArray();
                String targetName = qualifiedName.get(0).getAsString();
                Class<?> target = getDependency(targetName);
                method = getString(qualifiedName.get(1));
                Method callingMethod = reflection.getMethod(target, method);
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

    interface Deserializable {
    }

    static class PyObj {
        PyObj(String name, Map<String, ? extends Serializable> attributes) {
            this.name = name;
            this.attributes = attributes;
        }

        public Map<String, ? extends Serializable> getAttributes() {
            return attributes;
        }

        public String getName() {
            return name;
        }

        final String name;
        final Map<String, ? extends Serializable> attributes;
    }

    class PyObjSerializer implements JsonSerializer<PyObj> {

        @Override
        public JsonElement serialize(PyObj o, Type type, JsonSerializationContext
                jsonSerializationContext) {
            JsonObject params = new JsonObject();
            for (Map.Entry<String, ? extends Serializable> e : o.getAttributes().entrySet()) {
                Serializable v = e.getValue();
                JsonPrimitive p;
                if (v instanceof Number) {
                    p = new JsonPrimitive((Number) v);
                }
                else if (v instanceof String) {
                    p = new JsonPrimitive((String) v);
                }
                else if (v instanceof Boolean) {
                    p = new JsonPrimitive((Boolean) v);
                }
                else if (v instanceof Character) {
                    p = new JsonPrimitive((Character) v);
                }
                else {
                    p = new JsonPrimitive(v.toString());
                }
                params.add(e.getKey(), p);
            }

            JsonArray constructorArr = new JsonArray();
            constructorArr.add(o.getName());
            constructorArr.add(params);

            JsonObject obj = new JsonObject();
            obj.add("__jsonclass__", constructorArr);
            return obj;
        }
    }
}
