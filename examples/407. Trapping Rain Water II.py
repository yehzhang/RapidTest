from rapidtest import Test, Case, randints, randstr
from itertools import combinations, chain, permutations
from random import randint, shuffle
from string import ascii_lowercase


with Test('Solution.java') as t:
    def flip(board):
        yield board
        rev_board = board[::-1]
        yield rev_board
        yield [row[::-1] for row in board]
        yield [row[::-1] for row in rev_board]

    def rotate(board):
        yield board
        board = list(zip(*board[::-1]))
        yield board
        board = list(zip(*board[::-1]))
        yield board
        board = list(zip(*board[::-1]))
        yield board

    def transpose(board):
        yield board
        yield list(zip(*board))

    def transform(fs, board):
        boards = [board]
        for f in fs:
            boards = chain.from_iterable(map(f, boards))
        return boards

    Case([
        [0, 0, 1, 0, 0],
        [0, 1, 2, 1, 0],
        [1, 2, 3, 2, 1],
        [0, 1, 2, 1, 0],
        [0, 0, 1, 0, 0],
    ], result=0)

    Case([[10] * 5] * 5, result=0)


    board1 = [
        [1, 4, 3, 1, 3, 2],
        [3, 2, 1, 3, 2, 4],
        [2, 3, 3, 2, 3, 1]
    ]
    for board in transform([flip, rotate, transpose], board1):
        Case(board, result=4)

    board2 = [
        [1, 1, 1, 1],
        [1, 0, 0, 0],
        [1, 0, 0, 1],
        [1, 1, 1, 1],
    ]
    for board in transform([rotate, transpose], board2):
        Case(board, result=0)
