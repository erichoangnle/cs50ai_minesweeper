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
        # When the number of cells in a sentence is exactly 
        # equal to the sentence's count, then all the cells
        # in said sentence are mines
        mines = set()
        if self.cells and self.count == len(self.cells):
            for cell in self.cells:
                mines.add(cell)
            return mines 

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # A cell, or set of cells in sentence
        # is known to be safe when sentence count
        # is zero
        safes = set()
        if self.count == 0 and self.cells:
            for cell in self.cells:
                safes.add(cell)
            return safes

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # Check if cell is in sentence
        # If yes, remove cell
        if cell in self.cells:
            self.cells.remove(cell)

            # Decrease count by one
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # Check if cell is in sentence
        # If yes, remove cell
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
        # 1) Mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) Mark the cell as safe
        self.mark_safe(cell)

        # 3) Add new sentence to knowledge base
        # Get a set of all near by cells
        near_by = set()

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                
                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                # Add nearby cells to set if exist
                if 0 <= i < self.height and 0 <= j < self.width:
                    if (i, j) not in self.moves_made and (i, j) not in self.safes:

                        # If cell is known_mine, decrease count by one but do not add cell
                        if (i, j) in self.mines:
                            count -= 1
                        else:
                            near_by.add((i, j))

        # Create new sentence and add to knowledge base
        sentence = Sentence(near_by, count)
        self.knowledge.append(sentence)

        # Repeat until there is no change in KB
        while True:

            # Create a copy of KB to compare
            test = self.knowledge.copy()

            # 4) Mark additional cells as safe or mine if possible
            # Loop over all sentences in knowledge base
            for sentence in self.knowledge:
                
                # If there are safe cells
                if sentence.known_safes():
                    for cell in sentence.known_safes().copy():
                        self.mark_safe(cell)

                # If there are mine cells
                if sentence.known_mines():
                    for cell in sentence.known_mines().copy():
                        self.mark_mine(cell)

            # 5) Add inferred sentence to knowledge base if any
            # Loop over all sentences in knowledge base twice
            if len(self.knowledge) >= 2:

                for sentence1 in self.knowledge:
                    for sentence2 in self.knowledge:
                        
                        # Ignore the same sentence
                        if sentence1 == sentence2 or len(sentence1.cells) == 0 or len(sentence2.cells) == 0:
                            continue

                        # Check if subset but not equivalent
                        if sentence1.cells.issubset(sentence2.cells) and len(sentence1.cells) != len(sentence2.cells):

                            # Construct new sentence and add to knowledge base
                            new_sentence = Sentence(sentence2.cells - sentence1.cells, sentence2.count - sentence1.count)
                            self.knowledge.append(new_sentence)

                            # Remove sentence2 from knowledge base
                            self.knowledge.remove(sentence2)

            # Remove empty sentence
            for sentence in self.knowledge.copy():
                if len(sentence.cells) == 0:
                    self.knowledge.remove(sentence)

            # If there is no change to KB, break out of loop
            if self.knowledge == test:
                break

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # If there are cells known to be safe
        if self.safes:
            for cell in self.safes:
                if cell not in self.moves_made:
                    return cell

        # Otherwise return None
        else:
            return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Initialize a set of random move
        self.random = set()

        # Find possible random moves and add to set
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    self.random.add((i, j))

        # Return a random move
        if self.random:
            return random.choice(tuple(self.random))
        else:
            return None
