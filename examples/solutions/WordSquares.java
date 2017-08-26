import java.util.*;
import java.util.function.*;
import java.util.stream.*;
import java.io.*;
import java.math.*;

public class WordSquares {
    public List<List<String>> wordSquares(String[] words) {
        Trie root = Trie.from(words);
        List<List<String>> res = new ArrayList<>();
        for (int i = 0; i < words.length; i++) {
            String word = words[i];
            Stack<String> s = new Stack<>();
            s.push(word);
            dfs(root, res, s, 1, word.length());
        }
        return res;
    }

    void dfs(Trie root, List<List<String>> res, Stack<String> square, int depth, int side) {
        if (depth == side) {
            res.add(new ArrayList<>(square));
            return;
        }

        List<Character> prefix = new ArrayList<>();
        int i = 0;
        for (String s : square) {
            if (i + 1 > s.length()) {
                break;
            }
            i++;
            prefix.add(s.charAt(square.size()));
        }

        int wordLength = (i < square.size()) ? i : side;
        root.findWordStartsWith(prefix).stream()
            .filter(w -> w.length() == wordLength)
            .forEach(word -> {
                square.push(word);
                dfs(root, res, square, depth + 1, side);
                square.pop();
            });
    }

    static class Trie {
        String word;
        Map<Character, Trie> children;

        Trie() {
            children = new HashMap<>();
        }

        static Trie from(String[] words) {
            Trie root = new Trie();
            for (String word : words) {
                Trie node = root;
                for (char c : word.toCharArray()) {
                    node.children.putIfAbsent(c, new Trie());
                    node = node.children.get(c);
                }
                node.word = word;
            }
            return root;
        }

        List<String> findWordStartsWith(Collection<Character> prefix) {
            List<String> res = new ArrayList<>();

            Trie node = this;
            for (Character c : prefix) {
                Trie child = node.children.get(c);
                if (child == null) {
                    return res;
                }
                node = child;
            }

            dfsAllWord(res, node);

            return res;
        }

        void dfsAllWord(List<String> res, Trie root) {
            if (root == null) {
                return;
            }
            if (root.word != null) {
                res.add(root.word);
            }
            root.children.forEach((ignored, child) -> dfsAllWord(res, child));
        }
    }
}