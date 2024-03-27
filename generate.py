import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable, words in self.domains.items():
            var_length = variable.length
            for word in list(words):
                if len(word) == var_length:
                    continue
                self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        if self.crossword.overlaps[(x, y)] is None:
            return False

        revision = False

        i, j = self.crossword.overlaps[x, y]
        x_words = list(self.domains[x])
        y_words = list(self.domains[y])
        for x_word in x_words:
            letter = x_word[i]
            inner_break = False
            for y_word in y_words:
                if letter == y_word[j]:
                    inner_break = True
                    break
            if inner_break:
                continue
            self.domains[x].remove(x_word)
            revision = True

        return revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        variables = list(self.domains.keys())
        if arcs is None:
            initial_queue = self.all_arcs()
        else:
            initial_queue = arcs
        change_made = False
        while len(initial_queue) != 0:
            arc_x, arc_y = initial_queue.pop(0)
            if self.revise(arc_x, arc_y):
                change_made = True
                # var_set_y = variables.copy()
                # var_set_y.remove(arc_x)
                # for y in list(var_set_y):
                #     initial_queue.append((arc_x, y))
        if change_made:
            self.ac3()

        var_list = list(self.crossword.variables)
        for variable in var_list:
            words = list(self.domains[variable])
            if len(words) == 0:
                return False

        return True

    def all_arcs(self):
        arc_list = []
        var_set_x = list(self.domains.keys())

        for x in list(var_set_x):
            var_set_y = var_set_x.copy()
            var_set_y.remove(x)
            for y in list(var_set_y):
                arc_list.append((x, y))

        return arc_list

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        variables = self.crossword.variables
        for variable in list(variables):
            if variable not in assignment.keys():
                return False
            word = assignment[variable]
            if len(list(word)) == 0:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # check if all values are distinct
        words = assignment.values()
        words_list = list(words)
        words_set = set(words)
        if len(words_list) != len(words_set):
            return False

        # check if every value is correct length
        for variable, word in assignment.items():
            length = variable.length
            if len(word) != length:
                return False

        # check conflicts between variables
        arcs = self.all_arcs()
        for arc_x, arc_y in arcs:
            if self.crossword.overlaps[(arc_x, arc_y)] is None:
                continue
            if arc_x not in assignment or arc_y not in assignment:
                continue
            i, j = self.crossword.overlaps[(arc_x, arc_y)]
            x_word = assignment[arc_x]
            y_word = assignment[arc_y]
            if x_word[i] != y_word[j]:
                return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        values_list = list(self.domains[var])
        if len(values_list) == 1:
            return values_list
        assigned_words = list(assignment.values())
        word_dict = {}

        for value in values_list:
            if value in assigned_words:
                continue
            word_dict[value] = 0
            for key in self.crossword.neighbors(var):
                if self.crossword.overlaps[var, key] is None:
                    continue
                i, j = self.crossword.overlaps[var, key]
                var_letter = value[i]
                for word in list(self.domains[key]):

                    if word[j] != var_letter:
                        word_dict[value] += 1

        sorted_word_dict = dict(sorted(word_dict.items(), key=lambda x: x[1]))

        return list(sorted_word_dict.keys())

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        chosen_value = []
        variables = list(self.crossword.variables)

        min_values = float('inf')
        # chosen_value = None
        for var in variables:
            if var in assignment:
                continue
            var_len = len(list(self.domains[var]))
            if var_len > min_values:
                continue
            elif var_len == min_values:
                chosen_value.append(var)
            else:
                chosen_value = [var]
                min_values = var_len
        if len(chosen_value) == 1:
            return chosen_value[0]

        # chose option with the highest degree
        degree_dict = {}
        for value in chosen_value:
            degree_dict[value] = self.crossword.neighbors(value)

        return max(degree_dict, key=degree_dict.get)

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        while self.consistent(assignment):
            if self.assignment_complete(assignment):
                return assignment
            var = self.select_unassigned_variable(assignment)
            words = self.domains[var]
            words_list = list(words)
            if len(words_list) == 1:
                assignment[var] = words_list[0]
                word_set = {words_list[0]}
                self.domains[var] = word_set
                self.ac3_assigned(assignment)
                continue
            words = self.order_domain_values(var, assignment)
            if len(words) == 0:
                return None
            assignment[var] = words[0]
            word_set = {words[0]}
            self.domains[var] = word_set
            self.ac3_assigned(assignment)
        return None

    def ac3_assigned(self, assignment):
        variables = self.crossword.variables
        for key, value in assignment.items():
            for var in variables:
                if key == var:
                    continue
                x = self.revise(var, key)


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
