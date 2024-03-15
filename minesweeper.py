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

    def get_cells_and_count(self):
        return self.cells, self.count

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
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

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


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
        # mark the cell as a move that has been made
        self.moves_made.add(cell)

        # mark the cell as safe
        self.add_safe_cells(cell)

        # add a new sentence to the AI's knowledge base
        # based on the value of `cell` and `count`
        self.add_neighbors(cell, count)

        # Checks for new mines and safe cells
        self.update_mines_safe_cells()

        # Updates knowledge for new mines and safe cells
        self.update_knowledge()

        # Looks for inferred sentences from existing knowledge
        self.check_subsets()
        print('mines: ', self.mines)

    def mine_found(self, cells):
        """
            Adds given cells to self.mines,
            if they were not already added.
        """
        for cell in cells:
            if cell not in self.mines:
                self.mark_mine(cell)

    def add_safe_cells(self, cells):
        """
            Adds given cells to self.safes,
            if they were not already added.
            Takes as input set() or one element.
        """
        if isinstance(cells, set):
            for cell in cells:
                if cell not in self.safes:
                    self.mark_safe(cell)
        else:
            # treat cells as one element
            if cells not in self.safes:
                self.mark_safe(cells)

    def check_subsets(self):
        """
            Looks for inferred sentences from existing knowledge, by
            checking if in knowledge exists set that is subset of another set.
            If it does, it calls subset method and calls recurrently check_subsets.
        """
        for sentence_a in self.knowledge:
            set_a, count_a = sentence_a.get_cells_and_count()
            for sentence_b in self.knowledge:
                set_b, count_b = sentence_b.get_cells_and_count()
                if set_a < set_b:
                    self.subsets(set_b, count_b, set_a, count_a)
                    if sentence_b in self.knowledge:
                        self.knowledge.remove(sentence_b)
                    self.check_subsets()
                elif set_b < set_a:
                    self.subsets(set_a, count_a, set_b, count_b)
                    if sentence_a in self.knowledge:
                        self.knowledge.remove(sentence_a)
                    self.check_subsets()

    def subsets(self, set_a, count_a, subset_a, count_subset_a):
        """
            Checks new set and count, created by subsets.
            If new set has one element and count is equal to 1,
            it found new mine.
            If set has count equal to 0, it found safe cells.
            In other cases adds sentence to knowledge if it does not exist.
        """
        new_cells = set_a - subset_a
        new_count = count_a - count_subset_a
        if len(new_cells) == 1 and new_count == 1:
            self.mine_found(new_cells)
        elif new_count == 0:
            self.add_safe_cells(new_cells)
        else:
            sentence = Sentence(new_cells, new_count)
            if sentence not in self.knowledge:
                self.knowledge.append(sentence)

    def add_neighbors(self, cell, count):
        """
            Adds a new sentence to the AI's knowledge base
            based on the value of `cell` and `count`
        """
        i, j = cell

        # writes all surrounding cells
        neighbors = {(i, j-1), (i, j+1), (i-1, j-1), (i-1, j), (i-1, j+1),
                     (i+1, j-1), (i+1, j), (i+1, j+1)}

        # corrects that cells are not out of range
        correct_neighbors = set()
        for neighbor in neighbors:
            p, q = neighbor
            if 0 <= p < self.height and 0 <= q < self.width:
                correct_neighbors.add(neighbor)

        # if count is 0, then it adds cells to safe cells
        if count == 0:
            for correct_neighbor in correct_neighbors:
                self.safes.add(correct_neighbor)

        # if there are correct cells, it adds sentence to knowledge
        if len(correct_neighbors) != 0:
            sentence = Sentence(correct_neighbors, count)
            self.knowledge.append(sentence)

    def update_knowledge(self):
        """
            Removes empty sentence.
            For safe cells, marks according cells in knowledge.
            Same for mines.
        """
        empty_sentence = Sentence(set(), 0)
        for sentence in self.knowledge:
            for cell in self.safes:
                sentence.mark_safe(cell)
            for mine in self.mines:
                sentence.mark_mine(mine)
            if sentence == empty_sentence:
                self.knowledge.remove(sentence)

    def update_mines_safe_cells(self):
        """
            Updates new mines and new safe cells.
        """
        for sentence in self.knowledge:
            mines = sentence.known_mines()
            if len(mines) != 0:  # Checks if mines is None before iterating
                for mine in mines:
                    self.mines.add(mine)
            safe_cells = sentence.known_safes()
            if len(safe_cells) != 0:  # Checks if safe_cells is None before iterating
                for safe_cell in safe_cells:
                    self.safes.add(safe_cell)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for move in self.safes:
            if move not in self.moves_made:
                print('chosen move: ', move)
                return move

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        disallowed_moves = self.mines | self.moves_made
        board = set()

        for i in range(self.height):
            for j in range(self.width):
                cell = (i, j)
                board.add(cell)
        allowed_moves = board - disallowed_moves
        if len(allowed_moves) != 0:
            move = random.choice(list(allowed_moves))
            print(move)
            return move

        # if no such moves are possible, the function should return None
        return None
