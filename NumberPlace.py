from typing import List

class Cell:
    def __init__(self, row: int, column: int):
        self.row = row
        self.column = column
        self.number = 0
        self.excluded = [False] * 9

class Board:
    def __init__(self):
        self.rows = [[Cell(row, column) for column in range(1, 10)] for row in range(1, 10)]

    def show(self):
        for row in range(0, 9):
            numbers = list(map(lambda cell: str(cell.number), self.rows[row]))
            print(' '.join(numbers))
        print()

    def load(self, matrix: List[str]):
        for row in range(0, 9):
            for column in range(0, 9):
                self.rows[row][column].number = int(matrix[row][column])

    def setup(self):
        self.columns = []
        for column in range(0, 9):
            self.columns.append([self.rows[row][column] for row in range(0, 9)])
            #print(' '.join(list(map(lambda cell: str(cell.number), self.columns[column]))))

        #print()

        self.blocks = []
        for block_row in range(0, 3):
            for block_column in range(0, 3):
                block = []
                self.blocks.append(block)
                for r in range(0, 3):
                    for c in range(0, 3):
                        block.append(self.rows[block_row * 3 + r][block_column * 3 + c])

        #for i in range(0, 9):
        #    numbers = list(map(lambda cell: str(cell.number), self.blocks[i]))
        #    print(' '.join(numbers))

        #print()

    def step(self, row: int, column: int):
        changed = False
        target = self.rows[row][column]
        if target.number == 0:
            for c in range(0, 9):
                if c == column:
                    continue
                cell = self.rows[row][c]
                if 0 < cell.number:
                    target.excluded[cell.number - 1] = True
            for r in range(0, 9):
                if r == row:
                    continue
                cell = self.rows[r][column]
                if 0 < cell.number:
                    target.excluded[cell.number - 1] = True
            block_row = row // 3
            block_column = column // 3
            block = self.blocks[block_row][block_column]
            for r in range(0, 3):
                for c in range(0, 3):
                    cell = self.rows[block_row * 3 + r][block_column * 3 + c]
                    if target == cell:
                        continue
                    if 0 < cell.number:
                        target.excluded[cell.number - 1] = True

            candidates = []
            for n in range(0, 9):
                if not target.excluded[n]:
                    candidates.append(n + 1)

            if len(candidates) == 1:
                target.number = candidates[0]
                changed = True

        return changed

    def solve(self):
        changed = True
        loops = 0
        while changed:
            loops += 1
            changed = False
            for row in range(0, 9):
                for column in range(0, 9):
                    changed = changed or self.step(row, column)
        print(f'Loops: {loops}')
        print()

if __name__ == '__main__':

    example01 = [
        '000607000',
        '010598070',
        '009010500',
        '780020015',
        '051704390',
        '390060084',
        '005030100',
        '060452030',
        '000901000'
    ]

    board = Board()
    board.load(example01)
    board.show()
    board.setup()
    board.solve()
    board.show()


