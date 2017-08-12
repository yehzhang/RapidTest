import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class Dota2Senate {
    public String predictPartyVictory(String senate) {
        Queue<Integer> qR = new ArrayDeque<>();
        Queue<Integer> qD = new ArrayDeque<>();
        for (int i = 0; i < senate.length(); i++) {
            (senate.charAt(i) == 'R' ? qR : qD).offer(i);
        }
        while (!qR.isEmpty() && !qD.isEmpty()) {
            int iR = qR.poll();
            int iD = qD.poll();
            if (iR < iD) {
                qR.offer(iR + senate.length());
            }
            else {
                qD.offer(iD + senate.length());
            }
        }
        return qR.isEmpty() ? "Dire" : "Radiant";
    }
}
