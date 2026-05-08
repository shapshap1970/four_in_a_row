# Redis Setup for Four-in-a-Row

## What Redis Does

Redis enables **progressive AI learning** by caching AI calculations:
- **First time** AI sees a position → Calculate (5-15 sec) → Save to Redis
- **Next time** anyone sees that position → Instant retrieval!
- **Over time** → Common positions become instant

## Installation

### macOS (Homebrew)
```bash
brew install redis
brew services start redis
```

### Ubuntu/Debian
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

### Docker
```bash
docker run -d -p 6379:6379 redis:latest
```

## Configuration

Set environment variables (optional):

```bash
export REDIS_HOST=localhost      # Default: localhost
export REDIS_PORT=6379            # Default: 6379
export REDIS_PASSWORD=            # Default: none
export REDIS_DB=0                 # Default: 0
```

## Verify Redis is Running

```bash
redis-cli ping
# Should return: PONG
```

## Check Cache Statistics

```bash
# Total cached positions
redis-cli DBSIZE

# View sample cached positions
redis-cli KEYS "4row:*" | head -5

# Get cache info
redis-cli INFO stats
```

## How Caching Works

### Redis Key Format
```
4row:d{depth}:np{number_of_play}:{board_hash}
```

Example: `4row:d8:np2:123456789`
- `d8` = depth 8 search
- `np2` = 2 moves remaining for current player
- `123456789` = unique board position hash

### Cached Data
```json
{
  "score": 12,
  "move": 3,
  "depth": 8
}
```

### Expiration
- Cached positions expire after **30 days**
- Automatically cleaned up by Redis

## Performance Impact

**Without Redis:**
- Every position calculated from scratch
- 5-15 seconds per move

**With Redis (after 100 games):**
- First 6-8 moves: **Instant** (cached)
- Common patterns: **Instant**
- New positions: 5-15 sec (then cached)

**With Redis (after 1000 games):**
- Most early/mid game: **Instant**
- Effective opening book built organically

## Running Without Redis

If Redis is not available:
- Server will start normally
- Display warning: "⚠ Redis not available"
- AI works fine, just no caching
- Calculations won't be saved

## Deployment

### Vercel/Serverless
Redis not available on Vercel serverless. Use:
- **Upstash Redis** (serverless Redis)
- **Redis Cloud** (managed Redis)

Set environment variables in Vercel dashboard.

### Traditional Server
Install Redis on same server or use managed Redis service.

## Clearing Cache

```bash
# Clear all Four-in-a-Row cache
redis-cli KEYS "4row:*" | xargs redis-cli DEL

# Clear entire Redis database (careful!)
redis-cli FLUSHDB
```

## Monitoring

```bash
# Watch Redis commands in real-time
redis-cli MONITOR

# Get memory usage
redis-cli INFO memory
```

## Estimated Storage

- Each position: ~50-100 bytes
- After 100 games: ~50-100 KB
- After 1000 games: ~500 KB - 1 MB
- After 10,000 games: ~5-10 MB

Very lightweight!
