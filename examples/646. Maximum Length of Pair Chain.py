from rapidtest import Test, Case

with Test('Solution.java') as t:
    Case([[1,2], [2,3], [3,4]], result=2)
    Case([[1,3], [2,5], [3,6]], result=1)
    Case([[1,3], [3,5], [3,6]], result=1)
    Case([[1,3], [3,5]], result=1)
    Case([[1,6], [3,4], [5,6]], result=2)
    Case([[1,2], [5,6], [3,4]], result=3)
    Case([[1,5], [6,7], [2,4], [5,6], [7,8]], result=3)
