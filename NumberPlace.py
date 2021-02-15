from os import spawnl
import sys
import copy
import random
from itertools import product
from pathlib import Path
from typing import List, Tuple, Set

SIZE = 9
BSIZE = 3
UNFIXED = -1

class Cell:
    def __init__(self, row: int, column: int):
        # 0 <= row, column < 9
        self.row = row
        self.column = column
        # if fixed, 0 <= number < 9, otherwise UNFIXED
        self.number = UNFIXED
        self.rest_row = None
        self.rest_column = None
        self.rest_block = None

    def is_fixed(self):
        return UNFIXED < self.number

    def get_candidates(self) -> List[int]:
        candidates = []
        if not self.is_fixed():
            numbers_in_common = self.rest_row & self.rest_column & self.rest_block
            candidates = list(numbers_in_common)
        return candidates

    def is_fixable(self) -> Tuple[bool, int]:
        result = (False, UNFIXED)
        if not self.is_fixed():
            candidates = self.get_candidates()
            if len(candidates) == 1:
                result = (True, candidates[0])
        return result

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
        print('   ', '-'.join(['-' for i in range(SIZE)]))
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
                    if not self.cells[row][c].is_fixed():
                        self.fix(row, c, number)
                        break

        for column in range(SIZE):
            rest = self.columns[column]
            if len(rest) == 1:
                changed = True
                number = rest.pop()
                #print(f'column {column} fixed, {number}')
                for r in range(SIZE):
                    if not self.cells[r][column].is_fixed():
                        self.fix(r, column, number)
                        break

        for brow, bcolumn in product(range(SIZE // BSIZE), repeat=2):
            rest = self.blocks[brow][bcolumn]
            if len(rest) == 1:
                changed = True
                number = rest.pop()
                brow_base = brow * BSIZE
                bcolumn_base = bcolumn * BSIZE
                #print(f'block {brow}, {bcolumn} fixed, {number}')
                for r, c in product(range(BSIZE), repeat=2):
                    if not self.cells[brow_base + r][bcolumn_base + c].is_fixed():
                        self.fix(brow_base + r, bcolumn_base + c, number)
                        break

        for row, column in product(range(SIZE), repeat=2):
            cell = self.cells[row][column]
            if not cell.is_fixed():
                fixable, number = cell.is_fixable()
                if fixable:
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

    def is_fixed(self) -> bool:
        successful = True
        for row, column in product(range(SIZE), repeat=2):
            if not self.cells[row][column].is_fixed():
                successful = False
                break
        return successful

    def is_solved(self) -> bool:
        successful = True
        if successful:
            for row in range(SIZE):
                numbers = set()
                for column in range(SIZE):
                    numbers.add(self.cells[row][column].number)
                if len(numbers) != SIZE:
                    successful = False
                    #print(f'wrong row {row}')
                    break

        if successful:
            for column in range(SIZE):
                numbers = set()
                for row in range(SIZE):
                    numbers.add(self.cells[row][column].number)
                if len(numbers) != SIZE:
                    successful = False
                    #print(f'wrong column {column}')
                    break
        
        if successful:
            for brow, bcolumn in product(range(BSIZE), repeat=2):
                numbers = set()
                for r, c in product(range(SIZE // BSIZE), repeat=2):
                    numbers.add(self.cells[brow * BSIZE + r][bcolumn * BSIZE + c].number)
                if len(numbers) != SIZE:
                    successful = False
                    #print(f'wrong block {row} {column}')
                    break

        return successful

    def clear(self):
        self.__init__()

    def generate(self, sprawl_ratio):
        # assumption: no cell is fixed
        solved = False
        while not solved:
            self.clear()
            for row, column in product(range(SIZE), repeat=2):
                cell = self.cells[row][column]
                if not cell.is_fixed():
                    candidates = cell.get_candidates()
                    if len(candidates) == 0:
                        continue
                    elif len(candidates) == 1:
                        self.fix(row, column, candidates[0])
                        self.satulate()
                    else:
                        index = random.randrange(0, len(candidates))
                        self.fix(row, column, candidates[index])
                        self.satulate()
            solved = self.is_solved()
            #print(self.is_solved())
            #self.show()

        count = int(SIZE * SIZE * sprawl_ratio)
        while 0 < count:
            row = random.randrange(0, SIZE)
            column = random.randrange(0, SIZE)
            cell = self.cells[row][column]
            if cell.is_fixed():
                cell.number = UNFIXED
                count -= 1

    def save_as_problem(self, path_problem: str):
        path = Path(path_problem)
        if not path.parent.exists():
            path.parent.mkdir()
        with open(path, 'w', encoding='utf-8') as file:
            for row in range(SIZE):
                line = list(map(lambda c: str(c.number + 1), self.cells[row]))
                file.write(''.join(line) + '\n')

def load_problem(path_problem: str) -> List[Tuple[int, int, int]]:
    given = []
    with open(path_problem, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    for row in range(SIZE):
        line = lines[row]
        for column in range(SIZE):
            number = int(line[column])
            if 0 < number:
                given.append((row, column, number - 1))
    return given

def solve(path_problem):
    finished_boards = set()
    board = Board()
    problem = load_problem(path_problem)
    board.initialize(problem)
    print('-- Problem\n')
    board.show(from_one=True)
    board.satulate()
    if board.is_fixed():
        finished_boards.add(board)
    else:
        current_boards = [board]
        while 0 < len(current_boards):
            current_board = current_boards.pop()
            row, column, candidates = current_board.find_splittable()
            if candidates is None:
                if current_board.is_fixed():
                    #current_board.show()
                    if current_board.is_solved():
                        finished_boards.add(current_board)
            else:
                for candidate in candidates:
                    cloned_board = copy.deepcopy(current_board)
                    cloned_board.fix(row, column, candidate)
                    cloned_board.add_split_history(row, column, candidate)
                    cloned_board.satulate()
                    current_boards.append(cloned_board)

    print('-- Solutions\n')
    for board in finished_boards:
        board.show(from_one=True)
    print(f'# of solutions: {len(finished_boards)}')

def generate(path_problem: str, sprawl_ratio: float):
    board = Board()
    board.generate(sprawl_ratio)
    board.save_as_problem(path_problem)

def usage():
    print('Usage:')
    print('\tpython NumberPlace.py solve <path to problem>')
    print('\tpython NumberPlace.py generate <path to problem> <sprawl ratio>')

if __name__ == '__main__':
    path_problem = 'problems/problem149.txt'
    if 1 < len(sys.argv):
        command = sys.argv[1]
        path_problem = sys.argv[2]
        if command == 'solve':
            solve(path_problem)
        elif command == 'generate':
            sprawl_ratio = float(sys.argv[3])
            generate(path_problem, sprawl_ratio)
        else:
            usage()
    else:
        usage()
