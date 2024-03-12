"""
Tic Tac Toe Player
"""
import copy
from collections import Counter
import random


X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    count_x = 0
    count_o = 0
    whose_turn = X

    for row in board:
        for element in row:
            if element == X:
                count_x += 1
            if element == O:
                count_o += 1
    if count_x > count_o:
        whose_turn = O

    return whose_turn


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions_set = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                actions_set.add((i, j))

    return actions_set


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i = action[0]
    j = action[1]
    if board[i][j] != EMPTY:
        raise Exception

    memo = {}
    new_board = copy.deepcopy(board, memo)
    new_board[i][j] = player(board)

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # horizontal
    for i in range(3):
        who_wins = check_window([board[i][0], board[i][1], board[i][2]])
        if who_wins is not None:
            return who_wins

    # vertical
    for i in range(3):
        who_wins = check_window([board[0][i], board[1][i], board[2][i]])
        if who_wins is not None:
            return who_wins

    # positive diagonal
    who_wins = check_window([board[0][0], board[1][1], board[2][2]])
    if who_wins is not None:
        return who_wins

    # negative diagonal
    who_wins = check_window([board[0][2], board[1][1], board[2][0]])
    if who_wins is not None:
        return who_wins

    return who_wins


def check_window(my_list):
    """
        For given list of three board coordinates, checks if they have the same values.
        If the situation arises return its value, otherwise return None.
    """
    counts = Counter(my_list)
    for value, count in counts.items():
        if count == 3:
            return value
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    if actions(board):
        return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    value = winner(board)
    if value == X:
        return 1
    if value == O:
        return -1
    if value is None and not bool(actions(board)):
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    Uses helper function minimax_recurrent.
    """

    action_dict = {}
    for action in actions(board):
        action_dict[action] = minimax_recurrent(board, action, player(board))
    max_value = max(action_dict.values())
    max_keys = [key for key, value in action_dict.items() if value == max_value]
    return random.choice(max_keys)


def minimax_recurrent(board, action, sign):
    """
        Returns value (how good move is) for given action
    """
    new_board = result(board, action)
    action_score = 0
    if terminal(new_board):
        board_result = utility(new_board)
        if sign == O:
            board_result *= -1
        if board_result > 0:
            action_score += 1
        elif board_result < 0:
            action_score -= 100
        else:
            action_score = 0
        return action_score
    opponent_actions = actions(new_board)
    opponent_actions_score = {}
    for opponent_action in opponent_actions:
        opponent_actions_score[opponent_action] = action_score + minimax_recurrent(new_board, opponent_action, sign)
    if player(new_board) == sign:
        return max(opponent_actions_score.values())
    else:
        return min(opponent_actions_score.values())
