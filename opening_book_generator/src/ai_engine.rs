// Standalone Rust AI engine - can be called from Python
// Takes board state as input, returns best move

use std::io::{self, BufRead};

const ROWS: usize = 6;
const COLS: usize = 7;
const WIN_LENGTH: usize = 4;

#[derive(Clone, Debug)]
struct Board {
    grid: [[u8; COLS]; ROWS],
    heights: [i8; COLS],
}

impl Board {
    fn from_string(s: &str) -> Self {
        let mut grid = [[0u8; COLS]; ROWS];
        let mut heights = [5i8; COLS];

        // DO NOT use trim() - it removes spaces that are part of the board!
        let lines: Vec<&str> = s.split('\n').collect();
        for (row_idx, line) in lines.iter().enumerate() {
            if row_idx >= ROWS {
                break;
            }
            let chars: Vec<char> = line.chars().collect();
            for (col_idx, &ch) in chars.iter().enumerate() {
                if col_idx >= COLS {
                    continue;
                }
                grid[row_idx][col_idx] = match ch {
                    'X' => 1,
                    'O' => 2,
                    _ => 0,
                };
            }
        }

        // Calculate heights
        for col in 0..COLS {
            for row in 0..ROWS {
                if grid[row][col] != 0 {
                    heights[col] = row as i8 - 1;
                    break;
                }
            }
        }

        Board { grid, heights }
    }

    fn possible_moves(&self) -> Vec<usize> {
        (0..COLS)
            .filter(|&col| self.heights[col] >= 0)
            .collect()
    }

    fn play_move(&mut self, col: usize, player: u8) {
        let row = self.heights[col] as usize;
        self.grid[row][col] = player;
        self.heights[col] -= 1;
    }

    fn is_winner(&self, player: u8) -> bool {
        // Horizontal
        for row in 0..ROWS {
            for col in 0..=(COLS - WIN_LENGTH) {
                if (0..WIN_LENGTH).all(|i| self.grid[row][col + i] == player) {
                    return true;
                }
            }
        }

        // Vertical
        for col in 0..COLS {
            for row in 0..=(ROWS - WIN_LENGTH) {
                if (0..WIN_LENGTH).all(|i| self.grid[row + i][col] == player) {
                    return true;
                }
            }
        }

        // Diagonal (down-right)
        for row in 0..=(ROWS - WIN_LENGTH) {
            for col in 0..=(COLS - WIN_LENGTH) {
                if (0..WIN_LENGTH).all(|i| self.grid[row + i][col + i] == player) {
                    return true;
                }
            }
        }

        // Diagonal (up-right)
        for row in (WIN_LENGTH - 1)..ROWS {
            for col in 0..=(COLS - WIN_LENGTH) {
                if (0..WIN_LENGTH).all(|i| self.grid[row - i][col + i] == player) {
                    return true;
                }
            }
        }

        false
    }

    fn is_full(&self) -> bool {
        self.possible_moves().is_empty()
    }
}

fn count_threats(board: &Board, player: u8, length: usize) -> i32 {
    let mut count = 0;
    let opponent = if player == 1 { 2 } else { 1 };

    // Horizontal
    for row in 0..ROWS {
        for col in 0..=(COLS - WIN_LENGTH) {
            let window: Vec<u8> = (0..WIN_LENGTH).map(|i| board.grid[row][col + i]).collect();
            let player_count = window.iter().filter(|&&x| x == player).count();
            let opponent_count = window.iter().filter(|&&x| x == opponent).count();
            if player_count == length && opponent_count == 0 {
                count += 1;
            }
        }
    }

    // Vertical
    for col in 0..COLS {
        for row in 0..=(ROWS - WIN_LENGTH) {
            let window: Vec<u8> = (0..WIN_LENGTH).map(|i| board.grid[row + i][col]).collect();
            let player_count = window.iter().filter(|&&x| x == player).count();
            let opponent_count = window.iter().filter(|&&x| x == opponent).count();
            if player_count == length && opponent_count == 0 {
                count += 1;
            }
        }
    }

    // Diagonals
    for row in 0..=(ROWS - WIN_LENGTH) {
        for col in 0..=(COLS - WIN_LENGTH) {
            let window: Vec<u8> = (0..WIN_LENGTH).map(|i| board.grid[row + i][col + i]).collect();
            let player_count = window.iter().filter(|&&x| x == player).count();
            let opponent_count = window.iter().filter(|&&x| x == opponent).count();
            if player_count == length && opponent_count == 0 {
                count += 1;
            }
        }
    }

    for row in (WIN_LENGTH - 1)..ROWS {
        for col in 0..=(COLS - WIN_LENGTH) {
            let window: Vec<u8> = (0..WIN_LENGTH).map(|i| board.grid[row - i][col + i]).collect();
            let player_count = window.iter().filter(|&&x| x == player).count();
            let opponent_count = window.iter().filter(|&&x| x == opponent).count();
            if player_count == length && opponent_count == 0 {
                count += 1;
            }
        }
    }

    count
}

fn evaluate(board: &Board) -> i32 {
    if board.is_winner(1) {
        return 10000;
    }
    if board.is_winner(2) {
        return -10000;
    }
    if board.is_full() {
        return 0;
    }

    let mut score = 0;

    let x_three = count_threats(board, 1, 3);
    let o_three = count_threats(board, 2, 3);
    score += x_three * 100;
    score -= o_three * 100;

    let x_two = count_threats(board, 1, 2);
    let o_two = count_threats(board, 2, 2);
    score += x_two * 10;
    score -= o_two * 10;

    let x_one = count_threats(board, 1, 1);
    let o_one = count_threats(board, 2, 1);
    score += x_one;
    score -= o_one;

    let center_col = COLS / 2;
    for row in 0..ROWS {
        if board.grid[row][center_col] == 1 {
            score += 3;
        } else if board.grid[row][center_col] == 2 {
            score -= 3;
        }
    }

    score
}

fn order_moves(board: &Board, moves: &[usize]) -> Vec<usize> {
    let mut scored: Vec<(usize, i32)> = moves
        .iter()
        .map(|&col| {
            let distance = (col as i32 - (COLS / 2) as i32).abs();
            (col, -distance * 10)
        })
        .collect();
    scored.sort_by(|a, b| b.1.cmp(&a.1));
    scored.iter().map(|(col, _)| *col).collect()
}

fn minimax(
    board: &Board,
    depth: i32,
    mut alpha: i32,
    mut beta: i32,
    player: u8,
    num_play: u8,
    _last_col: Option<usize>,
    _first_play: bool,  // Not used in recursive calls, only for initial game state
) -> (i32, Option<usize>) {
    if depth == 0 {
        return (evaluate(board), None);
    }

    if board.is_winner(1) {
        return (10000, None);
    }
    if board.is_winner(2) {
        return (-10000, None);
    }

    let moves = board.possible_moves();
    if moves.is_empty() {
        return (0, None);
    }

    let ordered = order_moves(board, &moves);

    // 2-move rule: switch player when num_play reaches 1
    let (next_player, next_num) = if num_play == 1 {
        (if player == 1 { 2 } else { 1 }, 2)
    } else {
        (player, num_play - 1)
    };

    if player == 1 {
        let mut max_eval = i32::MIN;
        let mut best = ordered[0];

        for &col in &ordered {
            let mut new_board = board.clone();
            new_board.play_move(col, player);

            // Never pass first_play=true in recursive calls
            let (eval, _) = minimax(&new_board, depth - 1, alpha, beta, next_player, next_num, Some(col), false);

            if eval > max_eval {
                max_eval = eval;
                best = col;
            }

            alpha = alpha.max(eval);
            if beta <= alpha {
                break;
            }
        }

        (max_eval, Some(best))
    } else {
        let mut min_eval = i32::MAX;
        let mut best = ordered[0];

        for &col in &ordered {
            let mut new_board = board.clone();
            new_board.play_move(col, player);

            // Never pass first_play=true in recursive calls
            let (eval, _) = minimax(&new_board, depth - 1, alpha, beta, next_player, next_num, Some(col), false);

            if eval < min_eval {
                min_eval = eval;
                best = col;
            }

            beta = beta.min(eval);
            if beta <= alpha {
                break;
            }
        }

        (min_eval, Some(best))
    }
}

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();

    // Read depth
    let depth: i32 = lines.next().unwrap().unwrap().parse().unwrap();

    // Read player (1=X, 2=O)
    let player: u8 = lines.next().unwrap().unwrap().parse().unwrap();

    // Read number_of_play
    let num_play: u8 = lines.next().unwrap().unwrap().parse().unwrap();

    // Read board (6 lines)
    let mut board_str = String::new();
    for _ in 0..6 {
        if let Some(Ok(line)) = lines.next() {
            eprintln!("DEBUG: Read line: {:?} (len={})", line, line.len());
            board_str.push_str(&line);
            board_str.push('\n');
        }
    }

    eprintln!("DEBUG: Full board string: {:?}", board_str);

    let board = Board::from_string(&board_str);

    // DEBUG: Print parsed board
    eprintln!("DEBUG: Parsed board:");
    for row in 0..ROWS {
        eprintln!("Row {}: {:?}", row, board.grid[row]);
    }

    let (score, best_move) = minimax(&board, depth, i32::MIN, i32::MAX, player, num_play, None, false);

    // Output: score and best_move
    println!("{}", score);
    println!("{}", best_move.unwrap_or(999));
}
