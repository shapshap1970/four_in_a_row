"""
Interactive game with move analysis.
User plays against AI, with commentary on AI's decision quality.
"""

from board import Board
from four_in_a_row_optimized import FourInARowOptimized
import time


class GameAnalyzer:
    """Analyzes game moves and provides commentary"""

    def __init__(self, game):
        self.game = game
        self.move_history = []

    def analyze_position(self, board, player):
        """Analyze current position"""
        eval_score = self.game.evaluate_heuristic(board)

        # Count threats for both players
        x_three = self.game.count_threats(board, 'X', 3)
        o_three = self.game.count_threats(board, 'O', 3)
        x_two = self.game.count_threats(board, 'X', 2)
        o_two = self.game.count_threats(board, 'O', 2)

        analysis = {
            'eval': eval_score,
            'x_three': x_three,
            'o_three': o_three,
            'x_two': x_two,
            'o_two': o_two
        }

        return analysis

    def get_all_move_evaluations(self, board, player, num_play):
        """Evaluate all possible moves"""
        moves = board.possible_moves()
        evaluations = []

        for move in moves:
            test_board = Board(board)
            test_board.play_move(move[0], player)
            eval_score = self.game.evaluate_heuristic(test_board)
            evaluations.append((move[0], eval_score))

        return sorted(evaluations, key=lambda x: x[1] if player == 'X' else -x[1], reverse=True)

    def comment_on_move(self, board_before, move, player, eval_before, eval_after, is_best):
        """Provide commentary on a move"""
        comments = []

        # Check if it was the best move
        if is_best:
            comments.append("✓ Optimal move")
        else:
            comments.append("⚠ Not the best available move")

        # Check threats created or blocked
        board_after = Board(board_before)
        board_after.play_move(move, player)

        x_three_before = self.game.count_threats(board_before, 'X', 3)
        x_three_after = self.game.count_threats(board_after, 'X', 3)
        o_three_before = self.game.count_threats(board_before, 'O', 3)
        o_three_after = self.game.count_threats(board_after, 'O', 3)

        if player == 'X':
            if x_three_after > x_three_before:
                comments.append(f"🎯 Created {x_three_after - x_three_before} winning threat(s)")
            if o_three_before > 0:
                comments.append(f"🛡️ Blocking opponent's threat")
        else:
            if o_three_after > o_three_before:
                comments.append(f"🎯 Created {o_three_after - o_three_before} winning threat(s)")
            if x_three_before > 0:
                comments.append(f"🛡️ Blocking opponent's threat")

        # Eval change
        eval_change = eval_after - eval_before
        if player == 'X':
            if eval_change > 50:
                comments.append(f"📈 Strong tactical gain (+{eval_change})")
            elif eval_change < -50:
                comments.append(f"📉 Position worsened ({eval_change})")
        else:
            if eval_change < -50:
                comments.append(f"📈 Strong tactical gain ({eval_change})")
            elif eval_change > 50:
                comments.append(f"📉 Position worsened (+{eval_change})")

        return " | ".join(comments) if comments else "Standard move"


def print_board_with_numbers(board):
    """Print board with column numbers"""
    print("\n" + "="*50)
    print("   ", end="")
    for i in range(board.cols):
        print(f" {i} ", end="")
    print()
    print("   " + "---" * board.cols)

    for row in range(board.rows):
        print(f"{board.rows - row} |", end="")
        for col in range(board.cols):
            cell = board.board[row][col]
            if cell == 'X':
                print(" X", end=" ")
            elif cell == 'O':
                print(" O", end=" ")
            else:
                print(" .", end=" ")
        print("|")
    print("   " + "---" * board.cols)
    print()


def play_interactive_game():
    """Main interactive game loop"""
    print("="*60)
    print("🎮 FOUR-IN-A-ROW: HUMAN vs AI")
    print("="*60)

    # Get game configuration
    print("\nGame Configuration:")
    print("1. Quick game (5x5 board, 2 moves/turn)")
    print("2. Standard game (7x6 board, 2 moves/turn) ⭐ Recommended")
    print("3. Custom")

    choice = input("\nSelect (1-3): ").strip()

    if choice == "1":
        rows, cols = 5, 5
    elif choice == "3":
        cols = int(input("Columns (4-7): "))
        rows = int(input("Rows (4-6): "))
    else:  # Default to standard
        rows, cols = 6, 7

    consec_to_win = 4
    consec_moves = 2

    print(f"\n📊 Board: {cols}x{rows}, Win: {consec_to_win} in a row, Moves/turn: {consec_moves}")

    # Choose who goes first
    print("\nWho plays first?")
    print("1. Human (you drop 1 coin first)")
    print("2. AI (AI drops 1 coin first)")

    first_choice = input("Select (1-2): ").strip()
    human_first = first_choice == "1"

    # Choose AI thinking time
    print("\nAI thinking time:")
    print("1. Fast (2 seconds)")
    print("2. Normal (5 seconds) ⭐")
    print("3. Strong (10 seconds)")

    time_choice = input("Select (1-3): ").strip()
    if time_choice == "1":
        ai_time = 2.0
    elif time_choice == "3":
        ai_time = 10.0
    else:
        ai_time = 5.0

    # Initialize game
    game = FourInARowOptimized(rows=rows, cols=cols, consec_to_win=consec_to_win, consec_moves=consec_moves)
    board = Board(cols, rows)
    analyzer = GameAnalyzer(game)

    # Assign players
    if human_first:
        human_player = 'X'
        ai_player = 'O'
        print("\n🎮 You are X (play first with 1 coin)")
        print("🤖 AI is O (plays with 2 coins)")
    else:
        human_player = 'O'
        ai_player = 'X'
        print("\n🤖 AI is X (plays first with 1 coin)")
        print("🎮 You are O (play with 2 coins)")

    print("\n" + "="*60)
    print("GAME START!")
    print("="*60)

    move_count = 0
    current_player = 'X'
    first_turn = True

    # Game loop
    while True:
        move_count += 1
        num_moves = 1 if first_turn else consec_moves

        print(f"\n{'='*60}")
        print(f"Move #{move_count}: {current_player}'s turn ({num_moves} coin{'s' if num_moves > 1 else ''})")
        print(f"{'='*60}")

        print_board_with_numbers(board)

        # Analyze position before move
        pre_analysis = analyzer.analyze_position(board, current_player)
        print(f"Position eval: {pre_analysis['eval']:+.0f}")
        if pre_analysis['x_three'] > 0:
            print(f"⚠️  X has {pre_analysis['x_three']} winning threat(s)!")
        if pre_analysis['o_three'] > 0:
            print(f"⚠️  O has {pre_analysis['o_three']} winning threat(s)!")

        for i in range(num_moves):
            if i > 0:
                print(f"\nCoin {i+1} of {num_moves}:")
                print_board_with_numbers(board)

            if current_player == human_player:
                # Human move
                while True:
                    try:
                        col = int(input(f"\n🎮 Your move (column 0-{cols-1}): "))
                        if board.is_possible_move(col):
                            # Show what AI thinks of all moves
                            move_evals = analyzer.get_all_move_evaluations(board, current_player, num_moves - i)
                            print("\n📊 Move evaluations (your perspective):")
                            for col_opt, eval_opt in move_evals[:5]:  # Show top 5
                                marker = "👉" if col_opt == col else "  "
                                print(f"{marker} Column {col_opt}: {eval_opt:+.0f}")

                            board.play_move(col, current_player)
                            analyzer.move_history.append(('Human', current_player, col, move_count))
                            break
                        else:
                            print("❌ Invalid move, try again")
                    except ValueError:
                        print("❌ Please enter a number")
            else:
                # AI move
                print(f"\n🤖 AI thinking (max {ai_time}s)...")
                start_time = time.time()

                # Get all moves for comparison
                move_evals = analyzer.get_all_move_evaluations(board, current_player, num_moves - i)
                best_simple = move_evals[0][0]

                eval_score, col = game.get_best_move(
                    board, current_player, num_moves - i, None, max_time=ai_time
                )

                think_time = time.time() - start_time

                print(f"\n🤖 AI chose column {col} (thought for {think_time:.2f}s)")
                print(f"   Evaluation: {eval_score:+.0f}")

                # Show top alternatives
                print("\n📊 AI considered:")
                for col_opt, eval_opt in move_evals[:5]:
                    marker = "👉" if col_opt == col else "  "
                    print(f"{marker} Column {col_opt}: {eval_opt:+.0f}")

                # Commentary
                is_best = (col == best_simple)
                post_board = Board(board)
                post_board.play_move(col, current_player)
                post_eval = analyzer.analyze_position(post_board, current_player)['eval']

                comment = analyzer.comment_on_move(
                    board, col, current_player,
                    pre_analysis['eval'], post_eval, is_best
                )
                print(f"\n💭 Analysis: {comment}")

                board.play_move(col, current_player)
                analyzer.move_history.append(('AI', current_player, col, move_count))

            # Check for win
            if board.is_winner(current_player, consec_to_win):
                print("\n" + "="*60)
                print_board_with_numbers(board)
                print("="*60)
                print(f"🎉 {current_player} WINS!")
                print("="*60)

                # Game summary
                print("\n📜 Move History:")
                for who, player, col, move_num in analyzer.move_history:
                    print(f"  Move {move_num}: {who} ({player}) → Column {col}")

                return

            # Check for draw
            if board.is_end_of_game():
                print("\n" + "="*60)
                print_board_with_numbers(board)
                print("="*60)
                print("🤝 DRAW - Board is full!")
                print("="*60)
                return

        # Switch player
        current_player = 'O' if current_player == 'X' else 'X'
        first_turn = False


if __name__ == "__main__":
    try:
        play_interactive_game()
    except KeyboardInterrupt:
        print("\n\n👋 Game interrupted. Thanks for playing!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
