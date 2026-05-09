#!/usr/bin/env python3
"""Immediate threat detection - find moves that must be blocked"""

def detect_immediate_win(board, player, consec_to_win=4):
    """
    Detect if player can win in their next move.
    Returns list of columns that would result in immediate win.
    """
    winning_moves = []

    for col, _ in board.possible_moves():
        # Simulate the move
        from board import Board
        test_board = Board(board)
        test_board.play_move(col, player)

        if test_board.is_winner(player, consec_to_win):
            winning_moves.append(col)

    return winning_moves


def detect_must_block_moves(board, current_player, consec_to_win=4):
    """
    Detect moves that MUST be made to block opponent's immediate win.

    Returns:
    - If opponent can win next move: list of blocking columns (must play one!)
    - If we can win next move: list of winning columns (should play one!)
    - Otherwise: empty list
    """
    opponent = 'X' if current_player == 'O' else 'O'

    # Priority 1: Check if WE can win immediately
    our_winning_moves = detect_immediate_win(board, current_player, consec_to_win)
    if our_winning_moves:
        return ('win', our_winning_moves)

    # Priority 2: Check if opponent can win on their next turn - MUST BLOCK!
    opponent_winning_moves = detect_immediate_win(board, opponent, consec_to_win)
    if opponent_winning_moves:
        return ('block', opponent_winning_moves)

    return ('none', [])


def choose_best_forced_move(board, forced_type, forced_moves, search_func, depth, player, num_play):
    """
    When we have multiple forced moves (e.g., opponent has multiple winning threats),
    use minimax to pick the best one.
    """
    if len(forced_moves) == 1:
        return forced_moves[0]

    # Evaluate each forced move
    best_move = forced_moves[0]
    best_score = float('-inf') if player == 'X' else float('inf')

    for col in forced_moves:
        from board import Board
        test_board = Board(board)
        test_board.play_move(col, player)

        # Quick evaluation at reduced depth
        score, _ = search_func(test_board, min(depth, 6), player, num_play, col)

        if player == 'X':  # Maximizing
            if score > best_score:
                best_score = score
                best_move = col
        else:  # Minimizing
            if score < best_score:
                best_score = score
                best_move = col

    return best_move


# Example usage in AI engine:
# Before running full minimax:
#
# forced_type, forced_moves = detect_must_block_moves(board, current_player)
# if forced_type == 'win':
#     # We can win! Pick the best winning move
#     return choose_best_forced_move(...)
# elif forced_type == 'block':
#     # MUST block! Pick the best blocking move
#     return choose_best_forced_move(...)
# else:
#     # Normal minimax search
#     return minimax_alpha_beta(...)
