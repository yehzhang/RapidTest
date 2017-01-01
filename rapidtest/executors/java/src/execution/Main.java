package execution;

import static execution.StaticConfig.TARGET_CLASS;

public class Main {
    public static void main(String args[]) {
        try (Executor executor = new Executor()) {
            executor.run(TARGET_CLASS);
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(1);
        }
    }
}
