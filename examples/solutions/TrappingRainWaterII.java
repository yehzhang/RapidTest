import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class TrappingRainWaterII {
    public int trapRainWater(int[][] heightMap) {
        if (heightMap.length <= 2 || heightMap[0].length <= 2) {
            return 0;
        }

        Queue<Grid> sortedGrids = new PriorityQueue<>(Comparator.comparing(Grid::getHeight));
        boolean[][] visited = new boolean[heightMap.length][heightMap[0].length];
        for (int i = 0; i < heightMap.length; i++) {
            sortedGrids.offer(visitGrid(heightMap, i, 0, visited));
            sortedGrids.offer(visitGrid(heightMap, i, heightMap[i].length - 1, visited));
        }
        for (int i = 1; i < heightMap[0].length - 1; i++) {
            sortedGrids.offer(visitGrid(heightMap, 0, i, visited));
            sortedGrids.offer(visitGrid(heightMap, heightMap.length - 1, i, visited));
        }

        int total = 0;
        while (!sortedGrids.isEmpty()) {
            Grid g = sortedGrids.poll();
            for (int[] direction : DIRECTIONS) {
                int m = g.m + direction[0];
                int n = g.n + direction[1];
                if (m < 0 || m >= heightMap.length || n < 0 || n >= heightMap[0].length) {
                    continue;
                }
                if (visited[m][n]) {
                    continue;
                }
                int depth = Math.max(0, g.h - heightMap[m][n]);
                total += depth;
                heightMap[m][n] = Math.max(g.h, heightMap[m][n]);
                sortedGrids.offer(visitGrid(heightMap, m, n, visited));
            }
        }

        return total;
    }

    Grid visitGrid(int[][] heightMap, int m, int n, boolean[][] visited) {
        visited[m][n] = true;
        return new Grid(m, n, heightMap[m][n]);
    }

    class Grid {
        int m;
        int n;
        int h;

        Grid(int m, int n, int h) {
            this.m = m;
            this.n = n;
            this.h = h;
        }

        int getHeight() {
            return h;
        }
    }

    static final int[][] DIRECTIONS = {{0, 1}, {0, -1}, {1, 0}, {-1, 0}};
}
