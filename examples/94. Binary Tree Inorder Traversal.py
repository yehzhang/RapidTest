from Solution import Solution
from rapidtest import Test, Case, TreeNode

with Test(Solution) as test:
    Case(TreeNode.from_string('[1,null,2,3]'), result=[1,3,2])
    Case(TreeNode.from_string('[]'), result=[])
    Case(TreeNode.from_string('[1]'), result=[1])
    Case(TreeNode.from_string('[1,2]'), result=[2,1])
    Case(TreeNode.from_string('[1,2]'), result=[2,1])
    Case(TreeNode.from_string('[1,2,null,4,5,null,6,2,null,6,8,4,null,1,2,4,null,6,8,0,9,null,7,5,4,null,3,null,2,3]'),
         result=[4,3,0,1,9,6,2,7,6,5,4,4,8,2,6,3,4,8,2,2,5,1])
