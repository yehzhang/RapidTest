package execution;

import java.net.InetAddress;
import java.util.logging.Level;

class StaticConfig {
    static final String TARGET_ID = "Java_target_1";
    static final Class<?> TARGET_CLASS = MedianOfTwoSortedArrays.class;
    static final String METHOD_HELLO = "hello";
    static final String METHOD_EXECUTE = "execute";
    static final String METHOD_TERMINATE = "terminate";
    static final InetAddress HOST_ADDR;
    static final int HOST_PORT = 61039;
    static final String CANNOT_GUESS = "cannot guess";
    static final Level LOGGING_LEVEL = Level.ALL;


    static {
        try {
            HOST_ADDR = InetAddress.getByName(null);
        } catch (Exception e) {
            throw new ExceptionInInitializerError(e);
        }
    }
}
