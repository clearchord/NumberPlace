import sys
from typing import List, Tuple, Set
import copy

class Cell:
    def __init__(self, row: int, column: int):
        # 0 <= row, column < 9
        self.row = row
        self.column = column
        # if fixed, 0 <= number < 9, otherwise -1
        self.number = -1
        self.excluded = [False] * 9

    def fix(self, number: int):
        self.number = number

    def exclude(self, number: int):
        self.excluded[number] = True

    def remaining(self) -> int:
        return 0 if 0 <= self.number else self.excluded.count(False)

    def get_candidates(self) -> List[int]:
        candidates = []
        if self.number < 0:
            for index, fixed in enumerate(self.excluded):
                if not fixed:
                    candidates.append(index)
        return candidates

    def determinable(self) -> Tuple[bool, int]:
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
        # For code simplicity, it is OK to perform exclude() on cell (row, column) 3 times.
        for r0 in range(0, 9):
            self.cells[r0][column].exclude(number)
        for c0 in range(0, 9):
            self.cells[row][c0].exclude(number)
        block_row = (row // 3) * 3
        block_column = (column // 3) * 3
        for r in range(0, 3):
            br = block_row + r
            for c in range(0, 3):
                bc = block_column + c
                self.cells[br][bc].exclude(number)

    def apply(self, determined: Set[Tuple[int, int, int]]):
        for row, column, number in determined:
            self.fix(row, column, number)

    def determine(self) -> Set[Tuple[int, int, int]]:
        newly_determined = set()
        for row in range(0, 9):
            for column in range(0, 9):
                determinable, number = self.cells[row][column].determinable()
                if determinable:
                    newly_determined.add((row, column, number))
        return newly_determined

    def satulate(self, determined: Set[Tuple[int, int, int]]={}):
        if 0 < len(determined):
            self.apply(determined)
        next_determined = self.determine()
        while 0 < len(next_determined):
            self.apply(next_determined)
            next_determined = self.determine()

    def find_splittable(self) -> Tuple[int, int, List[int]]:
        splittable = None
        for row in range(0, 9):
            for column in range(0, 9):
                candidates = self.cells[row][column].get_candidates()
                if 1 < len(candidates):
                    splittable = (row, column, candidates)
                    break
            if splittable:
                break
        return (-1, -1, None) if splittable is None else splittable
    
    def is_successful(self) -> bool:
        successful = True
        for row in range(0, 9):
            for column in range(0, 9):
                if self.cells[row][column].number == -1:
                    successful = False
                    break
            if not successful:
                break
        return successful


def load_problem(path_problem: str) -> Set[Tuple[int, int, int]]:
    determined = set()
    with open(path_problem, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    for row in range(0, 9):
        for column in range(0, 9):
            number = int(lines[row][column])
            if 0 < number:
                determined.add((row, column, number - 1))
    return determined

def main(path_problem):
    finished_boards = set()
    board = Board()
    next_determined = load_problem(path_problem)
    board.satulate(next_determined)
    current_boards = [board]
    while 0 < len(current_boards):
        current_board = current_boards.pop()
        row, column, candidates = current_board.find_splittable()
        if 0 <= row:
            for candidate in candidates:
                cloned_board = copy.deepcopy(current_board)
                cloned_board.satulate([(row, column, candidate)])
                current_boards.append(cloned_board)
        else:
            if current_board.is_successful():
                finished_boards.add(current_board)

    print('--solutions')
    for board in finished_boards:
        board.show()
    print(f'# of solutions: {len(finished_boards)}')

if __name__ == '__main__':
    path_problem = 'problem149.txt'
    if 1 < len(sys.argv):
        path_problem = sys.argv[1]
    main(path_problem)
