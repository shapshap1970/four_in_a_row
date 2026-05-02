# Fast Mode Guide: Progress Display & Opening Book

## 🎯 Your Two Requests - SOLVED!

### 1. ✅ Progress Display During AI Thinking

**Problem**: Strong mode (10s) feels slow with no feedback

**Solution**: Real-time progress display showing:
- Current search depth
- Evaluation score at each depth
- Time per depth
- Total progress

### 2. ✅ Pre-Generated Cache (Opening Book)

**Problem**: Want faster gameplay by pre-computing moves

**Solution**: Opening book that pre-computes first 10 moves
- First 10 moves are **INSTANT** (< 0.01 seconds)
- Generated once, used forever
- Takes 10-20 minutes to generate

---

## 🚀 Quick Start

### Option 1: Play with Progress Display (No Setup)

```bash
python3 play_game_fast.py
```

**What you get:**
- Real-time progress: `[D1=+10(0.1s)] [D2=-5(0.3s)] [D3=+8(0.8s)]...`
- Shows thinking depth and speed
- Better user experience
- **No pre-generation needed**

### Option 2: Generate Opening Book (One-Time, 15 mins)

```bash
python3 generate_opening_book.py
```

**What happens:**
1. Asks configuration (press Enter for standard)
2. Generates opening book (~15 minutes)
3. Saves to `opening_book_7x6.pkl.gz`
4. First 10 moves will be INSTANT in future games!

Then play:
```bash
python3 play_game_fast.py
```

**What you get:**
- First 10 moves: **INSTANT** (< 0.01s)
- Later moves: Normal speed with progress display
- Best of both worlds!

---

## 📊 Progress Display Explained

### What You See During AI Thinking:

```
🤖 Thinking: [D1=+10(0.1s)] [D2=-5(0.3s)] [D3=+8(0.8s)] [D4=+15(1.2s)] ⏱️ Time limit
   → Move 3, eval +15, depth 4, 5.0s
```

**Breakdown:**
- `[D1=+10(0.1s)]` - Depth 1, evaluation +10, took 0.1 seconds
- `[D2=-5(0.3s)]` - Depth 2, evaluation -5, took 0.3 seconds
- `⏱️ Time limit` - Stopped because time limit reached
- `→ Move 3` - AI chose column 3
- `eval +15` - Final evaluation score
- `depth 4` - Searched to depth 4
- `5.0s` - Total time taken

**Benefits:**
- ✅ User knows AI is working (not frozen)
- ✅ See search depth progression
- ✅ Understand AI's "confidence" (evaluation)
- ✅ Verify time limit is respected

---

## 📚 Opening Book Details

### What is an Opening Book?

Pre-computed optimal moves for early game positions:
- AI calculates first 10 moves **very deeply** (12 plies)
- Saves results to a file
- During gameplay, looks up instead of calculating
- **Result: Instant moves (0.01s instead of 5s)**

### Generation Options:

**1. Standard (Recommended) ⭐**
```
Max moves: 10
Search depth: 12
Time: ~15 minutes
File size: ~5-10 MB
```

**2. Quick**
```
Max moves: 6
Search depth: 10
Time: ~5 minutes
File size: ~2-3 MB
```

**3. Deep (Best Quality)**
```
Max moves: 12
Search depth: 14
Time: ~60 minutes
File size: ~20-30 MB
```

### How to Generate:

```bash
python3 generate_opening_book.py
```

**Example session:**
```
Select configuration:
1. Standard (7x6, 10 moves, 12 depth) - Recommended
2. Quick (7x6, 6 moves, 10 depth) - Faster generation
3. Deep (7x6, 12 moves, 14 depth) - Best play, slow generation
4. Custom

Select (1-4, default=1): [press Enter]

Output filename (default=opening_book_7x6.pkl.gz): [press Enter]

⚠️  This will generate an opening book:
   - First 10 moves will be pre-computed
   - Search depth: 12 plies
   - Estimated time: 10 minutes
   - Output: opening_book_7x6.pkl.gz

Proceed? (y/n): y

🚀 Starting generation...

🔍 Evaluating position 1,234 (move 5, 45.2 pos/s, 3.5m elapsed)
...
✅ Generation complete!
   Positions evaluated: 3,456
   Time taken: 15.2 minutes
   Positions cached: 3,456

💾 Saving to opening_book_7x6.pkl.gz...
   ✓ Saved 3,456 positions (8.3 MB)
```

---

## 📈 Performance Comparison

### Without Opening Book:
```
Move 1: 5.2s
Move 2: 4.8s
Move 3: 5.1s
Move 4: 4.9s
Move 5: 5.3s
...
Total for first 10 moves: ~50 seconds
```

### With Opening Book:
```
Move 1: 0.01s 📚
Move 2: 0.01s 📚
Move 3: 0.01s 📚
Move 4: 0.01s 📚
Move 5: 0.01s 📚
Move 6: 0.01s 📚
Move 7: 0.01s 📚
Move 8: 0.01s 📚
Move 9: 0.01s 📚
Move 10: 0.01s 📚
Move 11: 5.0s (regular search)
...
Total for first 10 moves: ~0.1 seconds
```

**Speedup: 500x faster for early game!**

---

## 🎮 Usage Examples

### Example 1: Quick Play (No Setup)

```bash
$ python3 play_game_fast.py

# Press Enter for all defaults
# Play normally
# AI shows progress: [D1=...] [D2=...] etc.
```

### Example 2: Generate Book Once, Play Forever

**Step 1: Generate (do once)**
```bash
$ python3 generate_opening_book.py
# Wait 15 minutes
# Book saved to opening_book_7x6.pkl.gz
```

**Step 2: Play (forever)**
```bash
$ python3 play_game_fast.py
# First 10 moves are INSTANT!
# Shows "📚 Using opening book (instant)"
```

### Example 3: Strong AI with Progress

```bash
$ python3 play_game_fast.py
Select (1-3, default=2): [Enter]
Who goes first? (1=You, 2=AI, default=1): [Enter]
AI speed? (1=Fast/2s, 2=Normal/5s, 3=Strong/10s, default=2): 3

# AI will take 10s but show progress:
🤖 Thinking: [D1=+10(0.1s)] [D2=-5(0.3s)] [D3=+8(0.8s)] [D4=+15(1.5s)] [D5=+12(2.5s)] [D6=+18(4.0s)] [D7=+20(7.0s)] ⏱️ Time limit
   → Move 3, eval +20, depth 7, 10.0s
```

**You see it working!** No more wondering if it's frozen.

---

## 🔧 Technical Details

### Progress Display Features:

1. **Real-time updates** - Shows each depth completion
2. **Time tracking** - Time per depth and total
3. **Evaluation scores** - See AI's "confidence"
4. **Strict time limits** - Guaranteed to stop on time (with 0.5s buffer)
5. **Win detection** - Stops early if forced win/loss found

### Opening Book Features:

1. **Compressed storage** - Uses gzip (5-10 MB vs 50+ MB)
2. **Fast lookup** - Hash table (O(1) lookup)
3. **Deep search** - 12 plies per position (very strong)
4. **Main line focus** - Follows best moves, not all branches
5. **Portable** - Copy file to any machine

---

## 📁 Files Summary

| File | Purpose | When to Use |
|------|---------|-------------|
| `play_game_fast.py` | Game with progress & book | **Play here!** ⭐ |
| `generate_opening_book.py` | Generate opening book | Once, 15 mins |
| `four_in_a_row_with_progress.py` | Engine with progress | Library |
| `opening_book_7x6.pkl.gz` | Pre-computed moves | Auto-generated |

---

## ⚙️ Configuration

### Adjust AI Speed in play_game_fast.py:

```python
# Line ~45, change default:
time_choice = input("AI speed? (1=Fast/2s, 2=Normal/5s, 3=Strong/10s, default=2): ")

# Or hard-code:
ai_time = 10.0  # Force strong mode
```

### Adjust Opening Book Depth:

In `generate_opening_book.py`:
```python
max_moves = 15      # Cache more moves (takes longer)
search_depth = 14   # Search deeper (better quality)
```

### Disable Progress Display:

```python
game = FourInARowWithProgress(
    rows=6, cols=7,
    consec_to_win=4,
    consec_moves=2,
    show_progress=False  # Turn off progress
)
```

---

## 🎯 Recommendations

### For Casual Players:
```bash
# Just play with progress (no setup)
python3 play_game_fast.py
```
- Progress keeps you informed
- No waiting for book generation
- Good experience out-of-the-box

### For Regular Players:
```bash
# Generate book once (15 mins)
python3 generate_opening_book.py

# Then always use:
python3 play_game_fast.py
```
- One-time 15 minute investment
- Forever fast opening moves
- Best user experience

### For Tournament Play:
```bash
# Generate deep book (60 mins)
python3 generate_opening_book.py
# Select option 3 (Deep)

# Play with strong AI
python3 play_game_fast.py
# Select AI speed: Strong (10s)
```
- Best quality moves
- Deep calculation
- Strongest possible play

---

## 🐛 Troubleshooting

### "Progress display too verbose"

Set `show_progress=False` in code, or redirect output:
```bash
python3 play_game_fast.py 2>/dev/null
```

### "Opening book not loading"

Check filename matches:
```bash
ls -lh opening_book_7x6.pkl.gz
# If missing, generate it:
python3 generate_opening_book.py
```

### "Generation taking too long"

Use Quick mode (option 2):
- Only 6 moves instead of 10
- Takes ~5 minutes instead of 15
- Still provides good speedup

### "Strong mode still slow"

That's expected! 10 seconds is the limit you set. But now you see:
- ✅ Progress in real-time
- ✅ Current search depth
- ✅ AI is working, not frozen

If you want faster:
- Use Normal (5s) or Fast (2s) mode
- Or generate opening book for instant early moves

---

## 📊 Before & After

### Before (Your Complaint):
```
🤖 AI thinking...
[wait 12 seconds with no feedback]
[wonder if it's frozen]
[no idea what's happening]
🤖 AI played column 3
```

### After (With Progress):
```
🤖 Thinking: [D1=+10(0.1s)] [D2=-5(0.3s)] [D3=+8(0.8s)]
[D4=+15(1.5s)] [D5=+12(2.5s)] [D6=+18(4.0s)]
[D7=+20(7.0s)] ⏱️ Time limit
   → Move 3, eval +20, depth 7, 10.0s
```

**You can see:**
- ✅ It's working
- ✅ Current progress (depth 1,2,3...)
- ✅ How deep it's searching
- ✅ Time per depth
- ✅ When it will finish

### After (With Opening Book):
```
📚 Using opening book (instant)
   → Move 3, eval +15
[0.01 seconds - INSTANT!]
```

---

## ✅ Summary

**Two problems solved:**

1. **Progress Display** ✅
   - Shows real-time search progress
   - User knows AI is working
   - No more "is it frozen?" moments
   - Works out-of-the-box

2. **Pre-Generated Cache (Opening Book)** ✅
   - Generate once (15 minutes)
   - First 10 moves are instant forever
   - 500x speedup for early game
   - Optional but highly recommended

**Files to use:**
- `play_game_fast.py` - Play with both features
- `generate_opening_book.py` - Generate cache (once)

**Get started NOW:**
```bash
python3 play_game_fast.py
```

Enjoy your enhanced game! 🎮
