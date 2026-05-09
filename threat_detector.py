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


def detect_two_move_win(board, player, consec_to_win=4):
    """
    Detect if player can win within their next 2 consecutive moves.
    This is important for the 2-move rule where a player gets 2 moves per turn.

    Returns list of (col1, col2) tuples that lead to a win.
    """
    from board import Board

    winning_sequences = []

    for col1, _ in board.possible_moves():
        # Simulate first move
        test_board1 = Board(board)
        test_board1.play_move(col1, player)

        # Check if won after first move
        if test_board1.is_winner(player, consec_to_win):
            winning_sequences.append((col1, None))
            continue

        # Try all second moves
        for col2, _ in test_board1.possible_moves():
            # Simulate second move
            test_board2 = Board(test_board1)
            test_board2.play_move(col2, player)

            if test_board2.is_winner(player, consec_to_win):
                winning_sequences.append((col1, col2))

    return winning_sequences


def detect_must_block_moves(board, current_player, consec_to_win=4, check_two_moves=True):
    """
    Detect moves that MUST be made to block opponent's immediate win.

    Returns:
    - If opponent can win in their turn: ('block', list of blocking columns) - MUST BLOCK!
    - If we can win in our turn: ('win', list of winning columns)
    - Otherwise: ('none', [])

    NOTE: With check_two_moves=True, also checks if opponent can win within 2 consecutive
    moves (important for 2-move rule). This adds ~50ms but catches critical threats.
    """
    opponent = 'X' if current_player == 'O' else 'O'

    # Priority 1: Check if opponent can win on their immediate next move
    opponent_winning_moves = detect_immediate_win(board, opponent, consec_to_win)
    if opponent_winning_moves:
        return ('block', opponent_winning_moves)

    # Priority 2: Check if opponent can win within 2 moves (for 2-move rule)
    if check_two_moves:
        opponent_two_move_wins = detect_two_move_win(board, opponent, consec_to_win)
        if opponent_two_move_wins:
            # Opponent can win in 2 moves! We need to block their setup
            # Count which moves appear in winning sequences and prioritize blocking those
            from collections import Counter
            move_counter = Counter()

            for seq in opponent_two_move_wins:
                # Count both first and second moves (if second exists)
                move_counter[seq[0]] += 1
                if seq[1] is not None:
                    move_counter[seq[1]] += 1

            # Return moves sorted by how many threats they block (most important first)
            blocking_moves = [move for move, count in move_counter.most_common()]
            return ('block_2move', blocking_moves)

    # Priority 3: Check if WE can win immediately
    our_winning_moves = detect_immediate_win(board, current_player, consec_to_win)
    if our_winning_moves:
        return ('win', our_winning_moves)

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
