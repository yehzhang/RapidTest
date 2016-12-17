from Solution import Solution
from rapidtest import Test, Case

with Test(Solution) as test:
    Case([[0,0],[1,0],[2,0]], result=2)
    Case([[2,2]], result=0)
    Case([], result=0)
    Case([[1,1],[2,2],[3,3]], result=2)
    Case([[0,3],[4,0],[0,0],[0,8],[9,0]], result=4)
    Case([[0,0],[1,0],[0,1],[1,1]], result=8)
