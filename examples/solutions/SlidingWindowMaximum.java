import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class SlidingWindowMaximum {
    public int[] maxSlidingWindow(int[] nums, int k) {
        if (nums.length == 0) {
            return new int[0];
        }

        List<Integer> maxes = new ArrayList<>();

        MonotonicQueue queue = new MonotonicQueue();
        for (int i = 0; i < k; i++) {
            queue.push(nums[i]);
        }
        maxes.add(queue.max());

        for (int i = k; i < nums.length; i++) {
            queue.pop();
            queue.push(nums[i]);
            maxes.add(queue.max());
        }

        return maxes.stream().mapToInt(i -> i).toArray();
    }

    class Span {
        int value;
        int countElemsBefore;

        Span(int value, int countElemsBefore) {
            this.value = value;
            this.countElemsBefore = countElemsBefore;
        }
    }

    class MonotonicQueue {
        Deque<Span> maxHeadedWindow = new ArrayDeque<>();

        void push(int value) {
            int countElemsBefore = 0;
            while (!maxHeadedWindow.isEmpty() && value > maxHeadedWindow.getLast().value) {
                Span span = maxHeadedWindow.pollLast();
                countElemsBefore += span.countElemsBefore + 1;
            }
            maxHeadedWindow.offerLast(new Span(value, countElemsBefore));
        }

        int max() {
            return maxHeadedWindow.getFirst().value;
        }

        void pop() {
            if (maxHeadedWindow.getFirst().countElemsBefore > 0) {
                maxHeadedWindow.getFirst().countElemsBefore--;
            }
            else {
                maxHeadedWindow.pollFirst();
            }
        }
    }
}
