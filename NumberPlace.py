import sys
import copy
from itertools import product
from typing import List, Tuple, Set

class Cell:
    def __init__(self, row: int, column: int):
        # 0 <= row, column < 9
        self.row = row
        self.column = column
        # if fixed, 0 <= number < 9, otherwise -1
        self.number = -1
        self.rest_row = None
        self.rest_column = None
        self.rest_block = None

    def get_candidates(self) -> List[int]:
        candidates = []
        if self.number < 0:
            numbers_in_common = self.rest_row & self.rest_column & self.rest_block
            candidates = list(numbers_in_common)
        return candidates

    def determinable(self) -> Tuple[bool, int]:
        result = (False, -1)
        if self.number < 0:
            candidates = self.get_candidates()
            if len(candidates) == 1:
                result = (True, candidates[0])
        return result

SIZE = 9
BSIZE = 3

class Board:
    def __init__(self):
        self.debug = False
        self.cells = [[Cell(row, column) for column in range(SIZE)] for row in range(SIZE)]
        self.rows: List[Set[int]] = []
        self.columns: List[Set[int]] = []
        for _ in range(SIZE):
            self.rows.append({i for i in range(SIZE)})
            self.columns.append({i for i in range(SIZE)})
        self.blocks: List[List[Set[int]]] = []
        for brow in range(SIZE // BSIZE):
            block_row = []
            self.blocks.append(block_row)
            for bcolumn in range(SIZE // BSIZE):
                block_row.append({n for n in range(SIZE)})
        for row, column in product(range(SIZE), repeat=2):
            cell = self.cells[row][column]
            cell.rest_row = self.rows[row]
            cell.rest_column = self.columns[column]
            cell.rest_block = self.blocks[row // BSIZE][column // BSIZE]
        self.split_history: List[Tuple[int, int, int]] = []

    def show(self, from_one = False):
        print('   ', ' '.join([str(i+1) if from_one else str(i) for i in range(SIZE)]))
        print('   ', ' '.join(['-' for i in range(SIZE)]))
        for row in range(SIZE):
            numbers = []
            for cell in self.cells[row]:
                if cell.number == -1:
                    symbol = '-'
                elif from_one:
                    symbol = str(cell.number + 1)
                else:
                    symbol = str(cell.number)
                numbers.append(symbol)
            row_number = row + 1 if from_one else row
            print(f'{row_number}: ',' '.join(numbers))
        print()
        if self.debug:
            print('rows:')
            for row in range(SIZE):
                print(row, self.rows[row])
            print()
            print('columns:')
            for column in range(SIZE):
                print(column, self.columns[column])
            print()
            print('blocks:')
            for brow, bcolumn in product(range(SIZE // BSIZE), repeat=2):
                print(brow, bcolumn, self.blocks[brow][bcolumn])
            print()
            if 0 < len(self.split_history):
                print('split history:')
                for row, column, number in self.split_history:
                    print(row, column, number)
                print()

    def fix(self, row: int, column: int, number: int):
        changed = False
        if (0 <= row < SIZE) and (0 <= column < SIZE) and (0 <= number < SIZE):
            #print('fixed', row, column, (row // BSIZE, column // BSIZE), number)
            cell = self.cells[row][column]
            cell.number = number
            cell.rest_row.discard(number)
            cell.rest_column.discard(number)
            cell.rest_block.discard(number)
            #self.show()
        return changed

    def sweep(self):
        changed = False
        for row in range(SIZE):
            rest = self.rows[row]
            if len(rest) == 1:
                changed = True
                number = rest.pop()
                #print(f'row {row} fixed, {number}')
                for c in range(SIZE):
                    if self.cells[row][c].number == -1:
                        self.fix(row, c, number)
                        break

        for column in range(SIZE):
            rest = self.columns[column]
            if len(rest) == 1:
                changed = True
                number = rest.pop()
                #print(f'column {column} fixed, {number}')
                for r in range(SIZE):
                    if self.cells[r][column].number == -1:
                        self.fix(r, column, number)
                        break

        for brow, bcolumn in product(range(SIZE // BSIZE), repeat=2):
            rest = self.blocks[brow][bcolumn]
            if len(rest) == 1:
                changed = True
                number = rest.pop()
                brow_base = (row // BSIZE) * BSIZE
                bcolumn_base = (column // BSIZE) * BSIZE
                #print(f'block {brow}, {bcolumn} fixed, {number}')
                for r, c in product(range(BSIZE), repeat=2):
                    if self.cells[brow_base + r][bcolumn_base + c].number == -1:
                        self.fix(brow_base + r, bcolumn_base + c, number)
                        break

        for row, column in product(range(SIZE), repeat=2):
            cell = self.cells[row][column]
            if cell.number == -1:
                numbers_in_common = cell.rest_row & cell.rest_column & cell.rest_block
                if len(numbers_in_common) == 1:
                    number = numbers_in_common.pop()
                    #print(f'intersection {row}, {column} ({row // BSIZE}, {column // BSIZE}) fixed, {number}')
                    self.fix(row, column, number)
                    changed = True

        return changed

    def satulate(self):
        changed = True
        while changed:
            changed = False
            changed = changed or self.sweep()

    def initialize(self, problem):
        for row, column, number in problem:
            self.fix(row, column, number)
        self.satulate()

    def find_splittable(self) -> Tuple[int, int, List[int]]:
        splittable = None
        for row, column in product(range(SIZE), repeat=2):
            candidates = self.cells[row][column].get_candidates()
            if 1 < len(candidates):
                splittable = (row, column, candidates)
                break
        return (-1, -1, None) if splittable is None else splittable
    
    def add_split_history(self, row: int, column: int, number: int):
        self.split_history.append((row, column, number))

    def is_successful(self) -> bool:
        successful = True
        for row, column in product(range(SIZE), repeat=2):
            if self.cells[row][column].number == -1:
                successful = False
                break
        return successful

def load_problem(path_problem: str) -> List[Tuple[int, int, int]]:
    determined = []
    with open(path_problem, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    for row in range(SIZE):
        for column in range(SIZE):
            number = int(lines[row][column])
            if 0 < number:
                determined.append((row, column, number - 1))
    return determined

def main(path_problem):
    finished_boards = set()
    board = Board()
    problem = load_problem(path_problem)
    board.initialize(problem)
    if board.is_successful():
        finished_boards.add(board)
    else:
        current_boards = [board]
        while 0 < len(current_boards):
            current_board = current_boards.pop()
            row, column, candidates = current_board.find_splittable()
            if 0 <= row:
                for candidate in candidates:
                    cloned_board = copy.deepcopy(current_board)
                    cloned_board.fix(row, column, candidate)
                    cloned_board.add_split_history(row, column, candidate)
                    cloned_board.satulate()
                    current_boards.append(cloned_board)
            else:
                if current_board.is_successful():
                    #current_board.show()
                    finished_boards.add(current_board)

    print('-- Solutions')
    for board in finished_boards:
        board.show(from_one=True)
    print(f'# of solutions: {len(finished_boards)}')

if __name__ == '__main__':
    path_problem = 'problems/problem150.txt'
    if 1 < len(sys.argv):
        path_problem = sys.argv[1]
    main(path_problem)
