import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True
                print('mines: ', i, j)

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        mine_set = self.cells
        return mine_set

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        safe_set = self.cells
        return safe_set

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        mine_cell =set()
        mine_cell.add(cell)
        if self.cells == mine_cell:
            self.count = 1
        elif self.cells > mine_cell:
            self.cells = self.cells - mine_cell
            self.count = self.count - 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        safe_cell =set()
        safe_cell.add(cell)
        if self.cells == safe_cell:
            self.count = 0
        elif self.cells > safe_cell:
            self.cells = self.cells - safe_cell


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        move = cell    # move as current revealed cell
        self.moves_made.add(move)
        cells = set()
        cells.add(move)
        move_sentence = Sentence(cells, 0)
        self.knowledge.append(move_sentence)
        self.mark_safe(move)

        # add a new sentence to the AI knowledge base and update
        # loop cells as neighbors to the move
        neighbor_cells = set()
        for i in range(move[0]-1, move[0]+2):
            for j in range(move[1]-1, move[1]+2):
                if (i, j) == move:
                    continue
                if 0 <=i < self.height and 0 <= j <self.width:
                    cell = (i, j)
                    neighbor_cells.add(cell)
        self.knowledge.append(Sentence(neighbor_cells, count))

        #  Update AI knowledge according to count and cells
        n = -10000
        if count == 0:
            for cell in neighbor_cells:
                self.mark_safe(cell)
                n = 0
        elif count == len(neighbor_cells):
            for cell in neighbor_cells:
                self.mark_mine(cell)
                n = 1

        if n >= -10:
            for cell in neighbor_cells:
                cells = set()
                cells.add(cell)
                self.knowledge.append(Sentence(cells, n))

        # add any new sentences to the AI's knowledge base
        # if they can be inferred from existing knowledge
        new_knowledge = []
        for sen in self.knowledge:
            for sentence in self.knowledge:
                if sen == sentence:
                    continue
                elif sen.cells < sentence.cells:
                    new_set = sentence.cells - sen.cells
                    new_count = sentence.count - sen.count
                    new_knowledge.append(Sentence(new_set, new_count))

                    if new_count == 0:
                        for cell in new_set:
                            self.mark_safe(cell)
                    if new_count == len(new_set):
                        for cell in new_set:
                            self.mark_mine(cell)

        self.knowledge.extend(new_knowledge)

        for sentence in self.knowledge:
            if sentence.count == 0:
                safe_set = sentence.known_safes()
                self.safes.union(safe_set)
            if sentence.count == len(sentence.cells):
                mine_set = sentence.known_mines()
                self.mines.union(mine_set)

        # reduce redundant sentences
        knowledge_reduced = []
        index_set = set()
        for sentence in self.knowledge:
            index = list()
            for i in range(len(self.knowledge)):
                if sentence.cells == self.knowledge[i].cells:
                    index.append(i)
            sorted(index)
            index_set.add(tuple(index))

        for index in index_set:
            knowledge_reduced.append(self.knowledge[index[0]])

        self.knowledge = knowledge_reduced

        for sentence in self.knowledge:
            print(sentence, len(self.knowledge))


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        candidates = self.safes - self.moves_made
        print('safe move candidates : ', candidates)
        if len(candidates) > 0:
            move = random.choice(list(candidates))
            return move
        else:
            return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        all_cells = set()
        for i in range(self.height):
            for j in range(self.width):
                all_cells.add((i, j))
        random_candidates = all_cells - self.mines - self.moves_made
        print('random move candidates : ', random_candidates)

        if len(random_candidates) > 0:
            move = random.choice(list(random_candidates))
            return move
        else:
            return None
