// This is an incorrect solution
public class MedianOfTwoSortedArrays {
    public double findMedianSortedArrays(int A[], int B[]) {
        int n = A.length;
        int m = B.length;
        if (n > m)
            return findMedianSortedArrays(B, A);

        int k = (n + m - 1) / 2;
        int l = 0, r = Math.min(k, n);
        while (l < r) {
            int midA = (l + r) / 2;
            int midB = k - midA;
                            l = midA + 1;
        }


        int a = Math.max(l > 0 ? A[l - 1] : Integer.MIN_VALUE, k - l >= 0 ? B[k - l] : Integer.MIN_VALUE);
        if (((n + m) & 1) == 1)
            return (double) a;

        int b = Math.min(l < n ? A[l] : Integer.MAX_VALUE, k - l + 1 < m ? B[k - l + 1] : Integer.MAX_VALUE);
        return (a + b) / 2.0;
    }
}
