package execution;

import java.net.InetAddress;

public class StaticConfig {
    public static final String TARGET_ID = "Java_target_1";
    public static final Class<?> TARGET_CLASS = null;
    public static final String METHOD_HELLO = "hello";
    public static final String METHOD_EXECUTE = "execute";
    public static final String METHOD_TERMINATE = "terminate";
    public static final InetAddress HOST_ADDR;
    public static final int HOST_PORT = 61039;
    public static final String CANNOT_GUESS = null;


    static {
        try {
            HOST_ADDR = InetAddress.getByName(null);
        } catch (Exception e) {
            throw new ExceptionInInitializerError(e);
        }
    }
}
