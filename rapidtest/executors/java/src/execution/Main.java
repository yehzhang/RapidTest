package execution;

public class Main {
    public static void main(String args[]) {
        try (Executor executor = new Executor()) {
            executor.run();
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(1);
        }
    }
}
