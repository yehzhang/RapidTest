package execution;

import java.net.InetAddress;

public class StaticConfig {
    //    public static final Class<{{ TARGET_NAME }}> TARGET_CLASS;
    public static final Class<Solution> TARGET_CLASS = Solution.class;
    public static final String REQUEST_ID_PREFIX = "Java_";
    public static final String METHOD_EXECUTE = "execute";
    public static final String METHOD_STOP = "close";
    public static final InetAddress HOST_ADDR;
    public static final int HOST_PORT = 1234;
    public static final String WHO_I_AM = "java_executor_1";

    static {
        try {
            HOST_ADDR = InetAddress.getByName(null);
        } catch (Exception e) {
            throw new ExceptionInInitializerError(e);
        }
    }
}
