from os import pardir
from typing import List
import copy
import pdb

class Cell:
    def __init__(self, row: int, column: int):
        # 0 <= row, column < 9
        self.row = row
        self.column = column
        # if fixed, 0 <= number < 9, otherwise -1
        self.number = -1
        self.excluded = [False] * 9

    def fix(self, number):
        self.number = number

    def exclude(self, number):
        self.excluded[number] = True

    def remaining(self):
        return 0 if 0 <= self.number else self.excluded.count(False)

    def get_candidates(self):
        candidates = []
        if self.number < 0:
            for index, fixed in enumerate(self.excluded):
                if not fixed:
                    candidates.append(index)
        return candidates

    def determinable(self):
        result = (False, -1)
        if self.number < 0:
            candidates = self.get_candidates()
            if len(candidates) == 1:
                result = (True, candidates[0])
        return result

class Board:
    def __init__(self):
        self.cells = [[Cell(row, column) for column in range(0, 9)] for row in range(0, 9)]

    def show(self):
        for row in range(0, 9):
            numbers = list(map(lambda cell: str(cell.number + 1), self.cells[row]))
            print(' '.join(numbers))
        print()
    
    def show_remainings(self):
        for row in range(0, 9):
            numbers = list(map(lambda cell: str(cell.remaining()), self.cells[row]))
            print('-'.join(numbers))
        print()

    def fix(self, row, column, number):
        ''' fix the number for cell (row, column) and 
        propagate the information to its row, column, and block.
        '''
        self.cells[row][column].fix(number)
        for r0 in range(0, 9):
            if r0 == row:
                continue
            else:
                self.cells[r0][column].exclude(number)
        for c0 in range(0, 9):
            if c0 == column:
                continue
            else:
                self.cells[row][c0].exclude(number)
        block_row = (row // 3) * 3
        block_column = (column // 3) * 3
        for r in range(0, 3):
            br = block_row + r
            for c in range(0, 3):
                bc = block_column + c
                if br == row and bc == column:
                    continue
                else:
                    self.cells[br][bc].exclude(number)

    def load(self, matrix: List[str]):
        for row in range(0, 9):
            for column in range(0, 9):
                number = int(matrix[row][column])
                if 0 < number:
                    self.fix(row, column, number - 1)

    def determine(self):
        newly_determined = set()
        for row in range(0, 9):
            for column in range(0, 9):
                determinable, number = self.cells[row][column].determinable()
                if determinable:
                    newly_determined.add((row, column, number))
        return newly_determined

    def from_file(self, path_problem):
        with open(path_problem, 'r', encoding='utf-8') as file:
            example = file.readlines()
        return example

    def find_splittable(self):
        for row in range(0, 9):
            for column in range(0, 9):
                candidates = self.cells[row][column].get_candidates()
                if 1 < len(candidates):
                    return (row, column, candidates)
        return (-1, -1, None)

if __name__ == '__main__':
    board = Board()
    problem = board.from_file('problem149.txt')
    board.load(problem)
    next_determined = board.determine()
    print()
    while 0 < len(next_determined):
        for row, column, number in next_determined:
            board.fix(row, column, number)
        next_determined = board.determine()
        #board.show()
    #board.show_remainings()

    current_boards = [board]
    finished_boards = set()

    while 0 < len(current_boards):
        current_board = current_boards.pop()
        row, column, candidates = current_board.find_splittable()
        if 0 <= row:
            for candidate in candidates:
                cloned_board = copy.deepcopy(current_board)
                cloned_board.fix(row, column, candidate)
                next_determined = cloned_board.determine()
                while 0 < len(next_determined):
                    for r, c, number in next_determined:
                        cloned_board.fix(r, c, number)
                    next_determined = cloned_board.determine()
                current_boards.append(cloned_board)
        else:
            finished_boards.add(current_board)

    print('--solutions')
    for board in finished_boards:
        board.show()
    print(f'# of solutions: {len(finished_boards)}')

