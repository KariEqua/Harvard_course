from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(Or(Not(AKnight), Not(AKnave)),
                 Or(AKnight, AKnave),
                 Biconditional(AKnight, And(AKnight, AKnave)),
                 Biconditional(AKnave, And(Or(Not(AKnight), Not(AKnave))))
                 )

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(Or(Not(AKnight), Not(AKnave)),
                 Or(AKnight, AKnave),
                 Or(Not(BKnight), Not(BKnave)),
                 Or(BKnight, BKnave),
                 Biconditional(AKnight, And(AKnave, BKnave)),
                 Biconditional(AKnave, Or(Not(AKnave), Not(BKnave))),
                 )

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    Or(Not(AKnight), Not(AKnave)),
    Or(AKnight, AKnave),
    Or(Not(BKnight), Not(BKnave)),
    Or(BKnight, BKnave),
    Biconditional(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))),
    Biconditional(AKnave, And(Or(Not(AKnight), Not(BKnight)), Or(Not(AKnave), Not(BKnave)))),
    Biconditional(BKnight, Or(And(AKnight, AKnave), And(AKnave, BKnight))),
    Biconditional(BKnave, Or(And(AKnight, BKnight), And(AKnave, BKnave)))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    Or(Not(AKnight), Not(AKnave)),
    Or(AKnight, AKnave),
    Or(Not(BKnight), Not(BKnave)),
    Or(BKnight, BKnave),
    Or(Not(CKnight), Not(CKnave)),
    Or(CKnight, CKnave),
    Biconditional(CKnight, AKnight), Biconditional(CKnave, AKnave),
    Biconditional(BKnight, CKnave), Biconditional(BKnave, CKnight),
    Biconditional(AKnight, Or(AKnight, AKnave)),
    Biconditional(AKnave, Not(Or(AKnight, AKnave))),
    Biconditional(BKnight, Or(Biconditional(AKnight, AKnave), Biconditional(AKnave, AKnight)))
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
