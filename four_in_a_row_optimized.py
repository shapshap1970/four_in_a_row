import math
import time
from board import Board
from collections import defaultdict


class FourInARowOptimized:
    """
    Optimized Four-in-a-Row with:
    1. Heuristic evaluation for non-terminal states
    2. Iterative deepening with time limits
    3. Better alpha-beta pruning
    4. Move ordering
    5. Killer moves heuristic
    """

    def __init__(self, rows=6, cols=7, consec_to_win=4, consec_moves=2):
        self.rows = rows
        self.cols = cols
        self.consec_to_win = consec_to_win
        self.consec_moves = consec_moves
        self.memoization = {}
        self.killer_moves = defaultdict(list)  # Killer move heuristic
        self.history_heuristic = defaultdict(int)  # History heuristic for move ordering

    def switch_player(self, current_player):
        return 'O' if current_player == 'X' else 'X'

    def next_player(self, current_player, number_of_play, first_play=False):
        if number_of_play == 1 or first_play:
            return self.switch_player(current_player)
        else:
            return current_player

    def next_number_of_play(self, number_of_play, first_play=False):
        if number_of_play == 1 or first_play:
            return self.consec_moves
        else:
            return number_of_play - 1

    def evaluate_terminal(self, board):
        """Check for terminal states (win/loss/draw)"""
        if board.is_winner('X', self.consec_to_win):
            return 10000
        elif board.is_winner('O', self.consec_to_win):
            return -10000
        elif board.is_end_of_game():
            return 0  # Draw
        return None

    def count_threats(self, board, player, length):
        """
        Count potential winning sequences of given length for player.
        A threat is a sequence of 'length' pieces with empty spaces that could lead to a win.
        """
        count = 0
        opponent = self.switch_player(player)

        # Horizontal threats
        for row in range(self.rows):
            for col in range(self.cols - self.consec_to_win + 1):
                window = [board.board[row][col + i] for i in range(self.consec_to_win)]
                player_count = window.count(player)
                empty_count = window.count(' ')
                opponent_count = window.count(opponent)

                if player_count == length and opponent_count == 0:
                    count += 1

        # Vertical threats
        for col in range(self.cols):
            for row in range(self.rows - self.consec_to_win + 1):
                window = [board.board[row + i][col] for i in range(self.consec_to_win)]
                player_count = window.count(player)
                empty_count = window.count(' ')
                opponent_count = window.count(opponent)

                if player_count == length and opponent_count == 0:
                    count += 1

        # Diagonal (down-right) threats
        for row in range(self.rows - self.consec_to_win + 1):
            for col in range(self.cols - self.consec_to_win + 1):
                window = [board.board[row + i][col + i] for i in range(self.consec_to_win)]
                player_count = window.count(player)
                empty_count = window.count(' ')
                opponent_count = window.count(opponent)

                if player_count == length and opponent_count == 0:
                    count += 1

        # Diagonal (up-right) threats
        for row in range(self.consec_to_win - 1, self.rows):
            for col in range(self.cols - self.consec_to_win + 1):
                window = [board.board[row - i][col + i] for i in range(self.consec_to_win)]
                player_count = window.count(player)
                empty_count = window.count(' ')
                opponent_count = window.count(opponent)

                if player_count == length and opponent_count == 0:
                    count += 1

        return count

    def evaluate_heuristic(self, board):
        """
        Heuristic evaluation for non-terminal positions.
        Positive values favor X, negative favor O.
        """
        # First check terminal states
        terminal = self.evaluate_terminal(board)
        if terminal is not None:
            return terminal

        score = 0

        # Weight different threat levels
        # 3-in-a-row with space for 4th is very valuable
        x_three = self.count_threats(board, 'X', 3)
        o_three = self.count_threats(board, 'O', 3)
        score += x_three * 100
        score -= o_three * 100

        # 2-in-a-row with space for 4 is moderately valuable
        x_two = self.count_threats(board, 'X', 2)
        o_two = self.count_threats(board, 'O', 2)
        score += x_two * 10
        score -= o_two * 10

        # Single pieces in good positions
        x_one = self.count_threats(board, 'X', 1)
        o_one = self.count_threats(board, 'O', 1)
        score += x_one * 1
        score -= o_one * 1

        # Bonus for center control (center columns are more valuable)
        center_col = self.cols // 2
        for row in range(self.rows):
            if board.board[row][center_col] == 'X':
                score += 3
            elif board.board[row][center_col] == 'O':
                score -= 3

        return score

    def order_moves(self, board, moves, depth):
        """
        Order moves to improve alpha-beta pruning efficiency.
        Better moves first = more pruning.
        """
        def move_score(move):
            col = move[0]
            score = 0

            # Prefer center columns
            center_distance = abs(col - self.cols // 2)
            score -= center_distance * 10

            # Check history heuristic
            score += self.history_heuristic.get(col, 0)

            # Check killer moves
            if col in self.killer_moves.get(depth, []):
                score += 1000

            return score

        return sorted(moves, key=move_score, reverse=True)

    def minimax_alpha_beta(self, board, depth, alpha, beta, current_player,
                           number_of_play, last_column, first_play=False):
        """
        Minimax with alpha-beta pruning and heuristic evaluation.
        """
        # Check transposition table
        board_hash = board.to_hash()
        if board_hash in self.memoization:
            cached_depth, cached_eval, cached_move = self.memoization[board_hash]
            if cached_depth >= depth:
                return cached_eval, cached_move

        # Check terminal or depth limit
        if depth == 0:
            eval_score = self.evaluate_heuristic(board)
            return eval_score, last_column

        terminal_eval = self.evaluate_terminal(board)
        if terminal_eval is not None:
            return terminal_eval, last_column

        moves = board.possible_moves()
        if not moves:
            return 0, last_column  # Draw

        # Order moves for better pruning
        moves = self.order_moves(board, moves, depth)

        if current_player == 'X':  # Maximizing player
            max_eval = -math.inf
            best_move = moves[0][0] if moves else None

            for move in moves:
                move_board = Board(board)
                move_board.play_move(move[0], current_player)

                eval_score, _ = self.minimax_alpha_beta(
                    move_board, depth - 1, alpha, beta,
                    self.next_player(current_player, number_of_play, first_play),
                    self.next_number_of_play(number_of_play, first_play),
                    move[0]
                )

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move[0]

                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    # Beta cutoff - record killer move
                    if move[0] not in self.killer_moves[depth]:
                        self.killer_moves[depth].insert(0, move[0])
                        if len(self.killer_moves[depth]) > 2:
                            self.killer_moves[depth].pop()
                    break

            # Update history heuristic for good moves
            if best_move is not None:
                self.history_heuristic[best_move] += depth * depth

            # Store in transposition table
            self.memoization[board_hash] = (depth, max_eval, best_move)
            return max_eval, best_move

        else:  # Minimizing player (O)
            min_eval = math.inf
            best_move = moves[0][0] if moves else None

            for move in moves:
                move_board = Board(board)
                move_board.play_move(move[0], current_player)

                eval_score, _ = self.minimax_alpha_beta(
                    move_board, depth - 1, alpha, beta,
                    self.next_player(current_player, number_of_play),
                    self.next_number_of_play(number_of_play),
                    move[0]
                )

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move[0]

                beta = min(beta, eval_score)
                if beta <= alpha:
                    # Alpha cutoff - record killer move
                    if move[0] not in self.killer_moves[depth]:
                        self.killer_moves[depth].insert(0, move[0])
                        if len(self.killer_moves[depth]) > 2:
                            self.killer_moves[depth].pop()
                    break

            # Update history heuristic
            if best_move is not None:
                self.history_heuristic[best_move] += depth * depth

            # Store in transposition table
            self.memoization[board_hash] = (depth, min_eval, best_move)
            return min_eval, best_move

    def iterative_deepening_search(self, board, max_time_seconds, current_player,
                                    number_of_play, last_column):
        """
        Iterative deepening with time limit.
        Searches progressively deeper until time runs out.
        """
        start_time = time.time()
        best_move = None
        best_eval = None
        depth = 1

        # Always search at least depth 1
        while True:
            elapsed = time.time() - start_time
            if elapsed >= max_time_seconds and depth > 1:
                break

            try:
                eval_score, move = self.minimax_alpha_beta(
                    board, depth, -math.inf, math.inf,
                    current_player, number_of_play, last_column
                )

                best_eval = eval_score
                best_move = move

                print(f"Depth {depth}: eval={eval_score}, move={move}, "
                      f"time={time.time()-start_time:.2f}s, "
                      f"cache_size={len(self.memoization)}")

                # If we found a definite win/loss, no need to search deeper
                if abs(eval_score) >= 10000:
                    print(f"Found definite outcome at depth {depth}")
                    break

                depth += 1

                # Safety limit on depth
                if depth > 20:
                    break

            except KeyboardInterrupt:
                print("Search interrupted by user")
                break

        print(f"\nFinal decision: move={best_move}, eval={best_eval}, "
              f"searched to depth {depth-1}")
        return best_eval, best_move

    def get_best_move(self, board, current_player, number_of_play,
                      last_column=None, max_time=5.0):
        """
        Public interface to get best move with time limit.
        """
        return self.iterative_deepening_search(
            board, max_time, current_player, number_of_play, last_column
        )
