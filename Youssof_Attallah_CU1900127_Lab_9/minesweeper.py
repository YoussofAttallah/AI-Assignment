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
        if self.count == len(self.cells):
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, mine_cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if mine_cell in self.cells:
            self.cells.remove(mine_cell)
            self.count = self.count - 1

    def mark_safe(self, safe_cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if safe_cell in self.cells:
            self.cells.remove(safe_cell)


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
        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) mark the cell as safe
        self.mark_safe(cell)

        # 3) add a new sentance to the AI's kb
        current_cell_i = cell[0]
        current_cell_j = cell[1]
        inferred_sentence = set()
        for i in range(current_cell_i-1, current_cell_i+2):  # loops on all adjacent columns
            for j in range(current_cell_j-1, current_cell_j+2):  # loops on all adjacent rows
                if (i, j) == cell:
                    continue
                if (i, j) in self.safes:
                    continue
                if (i, j) in self.mines:
                    count = count - 1
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    inferred_sentence.add((i, j))
        self.knowledge.append(Sentence(inferred_sentence, count))
        # 4) mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
        knowledge_changed = True
        while knowledge_changed == True:
            knowledge_changed = False
            safes = set()
            mines = set()
            for sentence in self.knowledge:
                safes = safes.union(sentence.known_safes())
                mines = mines.union(sentence.known_mines())
            if safes:
                knowledge_changed = True
                for safe in safes:
                    self.mark_safe(safe)
            if mines:
                knowledge_changed = True
                for mine in mines:
                    self.mark_mine(mine)
            empty = Sentence(set(), 0)
            empty_knowledge = []
            for x in self.knowledge:
                if x == empty:
                    empty_knowledge.append(x)
            for x in empty_knowledge:
                self.knowledge.remove(x)
        # 5) add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
            for small_sentence in self.knowledge:
                for big_sentence in self.knowledge:
                    if small_sentence.cells == big_sentence.cells:
                        continue
                    if small_sentence.cells.issubset(big_sentence.cells):
                        inferred_sentence_cells = big_sentence.cells - small_sentence.cells
                        inferred_sentence_count = big_sentence.count - small_sentence.count
                        inferred_sentence = Sentence(
                            inferred_sentence_cells, inferred_sentence_count)
                        if inferred_sentence not in self.knowledge:
                            knowledge_changed = True
                            self.knowledge.append(inferred_sentence)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safe_moves = self.safes - self.moves_made
        if len(safe_moves) > 0:
            move = random.choice(list(safe_moves))
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
        available_moves = set()
        for i in range(0, self.height):
            for j in range(0, self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    available_moves.add((i, j))
        if available_moves:
            move = random.choice(list(available_moves))
            return move
        else:
            return None
