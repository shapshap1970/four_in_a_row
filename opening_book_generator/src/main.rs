use flate2::write::GzEncoder;
use flate2::Compression;
use rayon::prelude::*;
use serde_json::json;
use std::collections::{HashMap, HashSet, VecDeque};
use std::fs::File;
use std::io::Write;
use std::time::Instant;

const ROWS: usize = 6;
const COLS: usize = 7;
const WIN_LENGTH: usize = 4;

#[derive(Clone, Debug)]
struct Board {
    grid: [[u8; COLS]; ROWS], // 0=empty, 1=X, 2=O
    heights: [i8; COLS],       // Current height of each column (-1 = full)
}

impl Board {
    fn new() -> Self {
        Board {
            grid: [[0; COLS]; ROWS],
            heights: [5; COLS], // Start at bottom row (row 5)
        }
    }

    fn from_grid(grid: [[u8; COLS]; ROWS]) -> Self {
        let mut heights = [5i8; COLS];
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

    fn to_hash(&self) -> u128 {
        let mut hash: u128 = 0;
        for row in 0..ROWS {
            for col in 0..COLS {
                hash = hash << 2;
                hash |= self.grid[row][col] as u128;
            }
        }
        hash
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

    // Diagonal (down-right)
    for row in 0..=(ROWS - WIN_LENGTH) {
        for col in 0..=(COLS - WIN_LENGTH) {
            let window: Vec<u8> = (0..WIN_LENGTH)
                .map(|i| board.grid[row + i][col + i])
                .collect();
            let player_count = window.iter().filter(|&&x| x == player).count();
            let opponent_count = window.iter().filter(|&&x| x == opponent).count();
            if player_count == length && opponent_count == 0 {
                count += 1;
            }
        }
    }

    // Diagonal (up-right)
    for row in (WIN_LENGTH - 1)..ROWS {
        for col in 0..=(COLS - WIN_LENGTH) {
            let window: Vec<u8> = (0..WIN_LENGTH)
                .map(|i| board.grid[row - i][col + i])
                .collect();
            let player_count = window.iter().filter(|&&x| x == player).count();
            let opponent_count = window.iter().filter(|&&x| x == opponent).count();
            if player_count == length && opponent_count == 0 {
                count += 1;
            }
        }
    }

    count
}

fn evaluate_heuristic(board: &Board) -> i32 {
    // Check terminal states
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

    // Threat evaluation
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

    // Center control bonus
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
    let mut scored_moves: Vec<(usize, i32)> = moves
        .iter()
        .map(|&col| {
            let center_distance = (col as i32 - (COLS / 2) as i32).abs();
            let score = -center_distance * 10;
            (col, score)
        })
        .collect();

    scored_moves.sort_by(|a, b| b.1.cmp(&a.1));
    scored_moves.iter().map(|(col, _)| *col).collect()
}

fn minimax_alpha_beta(
    board: &Board,
    depth: i32,
    mut alpha: i32,
    mut beta: i32,
    current_player: u8,
    number_of_play: u8,
    last_column: Option<usize>,
    first_play: bool,
) -> (i32, Option<usize>) {
    // Check depth limit
    if depth == 0 {
        return (evaluate_heuristic(board), last_column);
    }

    // Check terminal states
    if board.is_winner(1) {
        return (10000, last_column);
    }
    if board.is_winner(2) {
        return (-10000, last_column);
    }

    let moves = board.possible_moves();
    if moves.is_empty() {
        return (0, last_column);
    }

    let ordered_moves = order_moves(board, &moves);

    // Determine next player and number_of_play
    let (next_player, next_num_play) = if number_of_play == 1 || first_play {
        (if current_player == 1 { 2 } else { 1 }, 2)
    } else {
        (current_player, number_of_play - 1)
    };

    if current_player == 1 {
        // Maximizing player (X)
        let mut max_eval = i32::MIN;
        let mut best_move = ordered_moves[0];

        for &col in &ordered_moves {
            let mut new_board = board.clone();
            new_board.play_move(col, current_player);

            let is_first = depth == 8; // first_play for recursive call
            let (eval, _) = minimax_alpha_beta(
                &new_board,
                depth - 1,
                alpha,
                beta,
                next_player,
                next_num_play,
                Some(col),
                is_first && first_play,
            );

            if eval > max_eval {
                max_eval = eval;
                best_move = col;
            }

            alpha = alpha.max(eval);
            if beta <= alpha {
                break; // Beta cutoff
            }
        }

        (max_eval, Some(best_move))
    } else {
        // Minimizing player (O)
        let mut min_eval = i32::MAX;
        let mut best_move = ordered_moves[0];

        for &col in &ordered_moves {
            let mut new_board = board.clone();
            new_board.play_move(col, current_player);

            let (eval, _) = minimax_alpha_beta(
                &new_board,
                depth - 1,
                alpha,
                beta,
                next_player,
                next_num_play,
                Some(col),
                false,
            );

            if eval < min_eval {
                min_eval = eval;
                best_move = col;
            }

            beta = beta.min(eval);
            if beta <= alpha {
                break; // Alpha cutoff
            }
        }

        (min_eval, Some(best_move))
    }
}

#[derive(Clone)]
struct Position {
    board: Board,
    current_player: u8,
    number_of_play: u8,
    last_column: Option<usize>,
    depth: usize,
    first_play: bool,
}

fn generate_all_positions(book_depth: usize) -> Vec<Position> {
    let mut positions = Vec::new();
    let mut queue = VecDeque::new();
    let mut visited = HashSet::new();

    // Start with empty board - player X to move
    let initial_board = Board::new();
    queue.push_back(Position {
        board: initial_board,
        current_player: 1, // X
        number_of_play: 2,
        last_column: None,
        depth: 0,
        first_play: false,
    });

    while let Some(pos) = queue.pop_front() {
        if pos.depth >= book_depth {
            continue;
        }

        let board_hash = pos.board.to_hash();
        if visited.contains(&board_hash) {
            continue;
        }
        visited.insert(board_hash);

        positions.push(pos.clone());

        // Generate all next positions
        for col in pos.board.possible_moves() {
            let mut next_board = pos.board.clone();
            next_board.play_move(col, pos.current_player);

            // Skip if game ended
            if next_board.is_winner(pos.current_player) || next_board.is_full() {
                continue;
            }

            // Determine next player
            let is_first = pos.depth == 0;
            let (next_player, next_num) = if pos.number_of_play == 1 || is_first {
                (if pos.current_player == 1 { 2 } else { 1 }, 2)
            } else {
                (pos.current_player, pos.number_of_play - 1)
            };

            queue.push_back(Position {
                board: next_board,
                current_player: next_player,
                number_of_play: next_num,
                last_column: Some(col),
                depth: pos.depth + 1,
                first_play: is_first,
            });
        }
    }

    positions
}

fn main() {
    println!("\n{}", "=".repeat(70));
    println!("🚀 RUST ULTRA-FAST OPENING BOOK GENERATOR");
    println!("{}", "=".repeat(70));

    let book_depth = 8;
    let search_depth = 8;
    let filename = "../opening_book_7x6.json.gz";

    println!("\nConfiguration:");
    println!("  Board: {}x{}", COLS, ROWS);
    println!("  Book depth: First {} moves", book_depth);
    println!("  Search depth: {} plies", search_depth);
    println!("  Parallelism: All CPU cores");
    println!("  Strategy: BFS + parallel minimax");
    println!("\n⏱️  Estimated time: 5-15 minutes");
    println!("📁 Output: {}", filename);
    println!("{}", "=".repeat(70));
    println!("\n🚀 Starting generation...\n");

    // Phase 1: Generate positions
    println!("📋 Phase 1: Generating position list (BFS)...");
    let start_time = Instant::now();
    let positions = generate_all_positions(book_depth);
    let gen_time = start_time.elapsed();
    println!(
        "   ✓ Generated {} positions to evaluate ({:.1}s)",
        positions.len(),
        gen_time.as_secs_f64()
    );

    // Phase 2: Parallel evaluation
    println!(
        "\n🚀 Phase 2: Parallel evaluation using all cores..."
    );
    let eval_start = Instant::now();

    let results: Vec<(u128, (i32, usize))> = positions
        .par_iter()
        .enumerate()
        .map(|(idx, pos)| {
            let (eval_score, best_move) = minimax_alpha_beta(
                &pos.board,
                search_depth as i32,
                i32::MIN,
                i32::MAX,
                pos.current_player,
                pos.number_of_play,
                pos.last_column,
                pos.first_play,
            );

            if idx % 1000 == 0 {
                let elapsed = eval_start.elapsed().as_secs_f64();
                let rate = (idx + 1) as f64 / elapsed;
                let remaining = (positions.len() - idx) as f64 / rate;
                println!(
                    "   Progress: {}/{} ({:.1}%) - {:.1} pos/s - ETA: {:.1}m",
                    idx + 1,
                    positions.len(),
                    (idx + 1) as f64 * 100.0 / positions.len() as f64,
                    rate,
                    remaining / 60.0
                );
            }

            let board_hash = pos.board.to_hash();
            (board_hash, (eval_score, best_move.unwrap_or(0)))
        })
        .collect();

    let eval_time = eval_start.elapsed();
    let total_time = start_time.elapsed();

    println!("\n✅ Evaluation complete!");
    println!("   Positions evaluated: {}", results.len());
    println!("   Evaluation time: {:.1} minutes", eval_time.as_secs_f64() / 60.0);
    println!("   Total time: {:.1} minutes", total_time.as_secs_f64() / 60.0);
    println!(
        "   Speed: {:.1} positions/second",
        results.len() as f64 / eval_time.as_secs_f64()
    );

    // Phase 3: Save to file
    println!("\n💾 Saving to {}...", filename);
    let mut book = HashMap::new();
    for (hash, (score, mv)) in results {
        book.insert(hash.to_string(), json!([score, mv]));
    }

    let json_str = serde_json::to_string(&book).expect("Failed to serialize");
    let file = File::create(filename).expect("Failed to create file");
    let mut encoder = GzEncoder::new(file, Compression::default());
    encoder
        .write_all(json_str.as_bytes())
        .expect("Failed to write");
    encoder.finish().expect("Failed to finish compression");

    let file_size = std::fs::metadata(filename)
        .expect("Failed to get file size")
        .len() as f64
        / (1024.0 * 1024.0);
    println!("   ✓ Saved {} positions ({:.2} MB)", book.len(), file_size);

    println!("\n{}", "=".repeat(70));
    println!("✅ OPENING BOOK READY!");
    println!("{}", "=".repeat(70));
    println!(
        "\nThe web server will now use instant moves for first {} moves!",
        book_depth
    );
    println!("{}", "=".repeat(70));
}
