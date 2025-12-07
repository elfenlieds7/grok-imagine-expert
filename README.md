# Grok Imagine Expert

AI-driven long-form video creation system using MCTS (Monte Carlo Tree Search) algorithm to automatically explore optimal video generation paths.

## Project Background

Grok Imagine can only generate 15-second short videos. This project breaks through this limitation by using **tree-based exploration + MCTS intelligent selection** to create high-quality videos of any length.

## Core Technologies

- 🌲 **MCTS Tree Search**: Automatic balance between exploration and exploitation
- 🤖 **Multi-dimensional AI Scoring**: Quality, coherence, semantics, diversity
- ☁️ **Multi-device Sync**: Supabase database + Dropbox file storage
- 🎨 **Dash Visualization**: Real-time view of exploration tree and MCTS process

> **📖 Important**: See [DESIGN.md](./DESIGN.md) for detailed design decisions and rationale behind all technical choices. This is essential reading for understanding why we chose MCTS over simpler algorithms, Dash over Streamlit, and the Supabase + Dropbox architecture.

## System Architecture

```
┌─────────────────────────────────────────┐
│         Dash UI (localhost)             │
│  Launches on any dev box,               │
│  accesses same synchronized data        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│    LangGraph MCTS Agent (local process) │
│  - Full MCTS: Select/Expand/Simulate/   │
│               Backpropagate              │
└─────┬────────────────────────┬───────────┘
      │                        │
      │ SQL (via Supabase)     │ File I/O (via Dropbox)
      ▼                        ▼
┌─────────────────┐  ┌─────────────────────┐
│ Supabase        │  │ ~/Dropbox/          │
│ PostgreSQL      │  │ grok-imagine-expert/│
│ (Cloud,         │  │ (Auto-syncs to all  │
│  multi-device   │  │  dev boxes)         │
│  auto-sync)     │  │                     │
│                 │  │ - images/           │
│ - projects      │  │ - videos/           │
│ - passes        │  │ - exports/          │
│ - nodes (MCTS)  │  │                     │
│ - generations   │  │                     │
└─────────────────┘  └─────────────────────┘
```

## Core Concepts

### Pass (Exploration Pass)
A complete exploration process starting from an initial image, forming a tree.

### Node
- **Image node**: Image (initial or video end frame)
- **Video node**: Generated video segment

### Tree Structure
```
Initial Image
  ├─ Video1 → EndFrame1 (Image)
  │   ├─ Video1.1 → EndFrame1.1
  │   └─ Video1.2 → EndFrame1.2
  ├─ Video2 → EndFrame2 (Image)
  └─ Video3 → EndFrame3 (Image)
```

### MCTS Scoring
Each node maintains:
- `visit_count`: Number of times explored
- `avg_reward`: Average reward (quality + coherence + semantic + diversity)
- `ucb_score`: UCB score (used for selecting next step)
- `is_fully_expanded`: Whether all children have been generated

## Data Storage Solution

### Supabase PostgreSQL (Metadata)
- Project, Pass, Node information
- MCTS statistics
- Scoring records
- **Free plan is sufficient** (500MB space, we only need ~10MB for 10,000 nodes)

### Dropbox (Media Files)
- All images and videos
- Auto-syncs to all dev boxes
- File structure: `~/Dropbox/grok-imagine-expert/projects/`

**Why this design?**
- ✅ Multiple dev boxes can work seamlessly
- ✅ No manual sync needed
- ✅ Database ensures metadata consistency
- ✅ Dropbox handles large file sync

## Dropbox File Structure

```
~/Dropbox/grok-imagine-expert/
└── projects/
    └── {project-id}/
        ├── passes/
        │   └── {pass-id}/
        │       ├── images/
        │       │   ├── img-{node-id}.jpg
        │       │   └── ...
        │       └── videos/
        │           ├── vid-{node-id}.mp4
        │           └── ...
        └── exports/
            └── final-{path-id}.mp4
```

**Naming Convention**:
- Project ID: `{timestamp}-{slug}` (e.g., `20250107-landscape-video`)
- Pass ID: `pass-{counter}` (e.g., `pass-001`)
- Node ID: UUID (e.g., `a1b2c3d4-5678-...`)
- File naming: `{node-type}-{node-id}.{ext}`

## Quick Start

### 1. Environment Setup

```bash
# Clone project
cd /Users/songym/cursor-projects/grok-imagine-expert

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and fill in Supabase credentials
```

### 2. Initialize Database

```bash
python scripts/init_supabase.py
```

This will:
- Connect to your Supabase project
- Create all necessary tables
- Set up indexes

### 3. Verify Dropbox

Ensure Dropbox Desktop is installed and syncing on all your dev boxes:
```bash
ls ~/Dropbox/grok-imagine-expert/
```

The directory will be automatically created on first use.

### 4. Start UI

```bash
python src/ui/app.py
# Visit http://localhost:8050
```

## Usage Guide

### Manual Mode

1. **Create New Project**
   - Click "New Project"
   - Upload initial image
   - Enter project name and base prompt

2. **Generate Candidates**
   - System generates M video candidates (default: 5)
   - Uses Playwright to automate Grok Imagine web interface

3. **Select and Expand**
   - Manually select N candidates (N < M)
   - System extracts end frames
   - Creates new image nodes for next iteration

4. **Repeat and Explore**
   - Jump to any node in the tree
   - Continue exploring from that point
   - Build your exploration tree organically

### MCTS Auto Mode

1. **Create Project + Configure**
   - Upload initial image
   - Set MCTS parameters:
     - Iterations: Number of MCTS iterations (default: 100)
     - Exploration constant: UCB exploration weight (default: 1.414)
     - Max children per node: (default: 3)
     - Max depth: (default: 10)

2. **Start Auto Exploration**
   - Click "Start MCTS"
   - System automatically:
     - Selects nodes using UCB
     - Generates videos via Playwright
     - Scores videos using AI
     - Backpropagates rewards
     - Repeats for N iterations

3. **View Results**
   - Explore the generated tree
   - Check MCTS statistics
   - Find the best path (highest avg_reward)
   - Export final video

## Configuration

### Supabase Setup

1. Create a free Supabase project at https://supabase.com
2. Get your project URL and anon key from Project Settings → API
3. Add to `.env`:
   ```
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=eyJhbGc...
   ```

### Dropbox Setup

Install Dropbox Desktop on all dev boxes:
- macOS: https://www.dropbox.com/install
- The directory `~/Dropbox/grok-imagine-expert/` will auto-sync

### MCTS Parameters

Edit in UI or modify defaults in `config/mcts_config.py`:

```python
MCTS_CONFIG = {
    "iterations": 100,              # Number of MCTS iterations
    "exploration_constant": 1.414,  # UCB exploration constant (√2)
    "max_children": 3,              # Max children per node
    "max_depth": 10,                # Max tree depth
    "simulation_depth": 3,          # Rollout depth for simulation
}
```

**Parameter tuning tips**:
- Higher `exploration_constant` → More exploration (diversity)
- Lower `exploration_constant` → More exploitation (quality)
- More `iterations` → Better results, longer time
- Higher `max_children` → Wider tree, more options

### Scoring Weights

Customize reward calculation in `src/evaluation/reward_calculator.py`:

```python
REWARD_WEIGHTS = {
    "quality": 0.4,      # Video quality (clarity, aesthetics)
    "coherence": 0.3,    # Smooth transition from parent
    "semantic": 0.2,     # Matches original prompt intent
    "diversity": 0.1,    # Exploration value
}
```

## MCTS Algorithm Overview

### Four Phases

```
1. SELECTION
   Start from root, use UCB to select path to leaf node
   UCB = exploitation + exploration

2. EXPANSION
   If leaf not fully expanded, generate new child
   (Generate video via Playwright, extract end frame)

3. SIMULATION
   Evaluate new node with multi-dimensional scoring:
   - Quality (AI vision model)
   - Coherence (frame difference analysis)
   - Semantic (prompt matching)
   - Diversity (novelty score)

4. BACKPROPAGATION
   Update visit_count and avg_reward for all nodes
   in the path from leaf to root
```

### UCB Formula

```
UCB(node) = avg_reward + c * sqrt(log(parent_visits) / node_visits)
            ^^^^^^^^^^^   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            Exploitation  Exploration
```

- Unvisited nodes get infinite UCB (prioritized)
- Frequently visited nodes: exploitation term dominates
- Rarely visited nodes: exploration bonus increases

## Database Schema

See detailed schema in `src/database/schema.sql`

**Key tables**:
- `projects`: Project metadata
- `passes`: Exploration passes (each pass = one tree)
- `nodes`: Tree nodes with MCTS statistics
- `generations`: Async generation task queue

**Key fields in nodes table**:
```sql
-- MCTS core
visit_count INTEGER
total_reward REAL
avg_reward REAL
is_fully_expanded BOOLEAN
is_terminal BOOLEAN

-- Multi-dimensional scores
quality_score REAL
coherence_score REAL
semantic_score REAL
diversity_score REAL
```

## Project Structure

```
grok-imagine-expert/
├── README.md                    # This file
├── DESIGN.md                    # Design decisions
├── requirements.txt
├── .env.example                 # Environment template
├── .gitignore
├── .mcp.json                    # Optional: MCP integration
│
├── config/
│   ├── supabase.py              # Supabase connection
│   └── dropbox_paths.py         # Dropbox path config
│
├── src/
│   ├── database/
│   │   ├── schema.sql           # Database schema
│   │   ├── supabase_client.py   # Supabase client
│   │   └── tree_operations.py   # Tree CRUD
│   │
│   ├── storage/
│   │   ├── dropbox_manager.py   # Dropbox path management
│   │   └── file_utils.py        # File operations
│   │
│   ├── agent/
│   │   ├── state.py             # LangGraph state
│   │   ├── react_agent.py       # LangGraph agent
│   │   ├── tools.py             # Agent tools
│   │   └── mcts_engine.py       # MCTS implementation
│   │
│   ├── automation/
│   │   ├── playwright_grok.py   # Grok Imagine automation
│   │   └── video_processor.py   # Video processing
│   │
│   ├── evaluation/
│   │   ├── quality_scorer.py    # Video quality scoring
│   │   ├── coherence_scorer.py  # Coherence scoring
│   │   └── reward_calculator.py # Composite reward
│   │
│   ├── ui/
│   │   ├── app.py               # Dash main app
│   │   ├── components/          # UI components
│   │   └── callbacks/           # Dash callbacks
│   │
│   └── utils/
│       ├── file_manager.py
│       └── config.py
│
├── scripts/
│   ├── init_supabase.py         # Database initialization
│   └── analyze_mcts.py          # MCTS analysis tool
│
└── tests/
    ├── test_mcts.py
    ├── test_supabase.py
    └── test_dropbox.py
```

## Development Guide

### Adding New Scoring Dimension

1. Add column to `nodes` table:
   ```sql
   ALTER TABLE nodes ADD COLUMN my_score REAL;
   ```

2. Implement scorer in `src/evaluation/`:
   ```python
   def score_my_dimension(node):
       # Your scoring logic
       return score  # 0-1 range
   ```

3. Update reward calculator:
   ```python
   REWARD_WEIGHTS["my_dimension"] = 0.1
   ```

### Custom Generation Strategy

Override in `src/agent/mcts_engine.py`:
```python
def custom_selection_policy(self, node):
    # Your custom UCB or selection logic
    pass
```

### Debugging MCTS

```bash
# Analyze MCTS statistics
python scripts/analyze_mcts.py --pass-id <pass-uuid>

# Output:
# - Visit distribution
# - Reward distribution
# - Best paths
# - Exploration vs exploitation ratio
```

## Technology Stack

- **UI**: Dash + Plotly
- **Backend**: Python 3.11+, LangGraph
- **Database**: Supabase (PostgreSQL)
- **Storage**: Dropbox
- **Automation**: Playwright (Grok Imagine web)
- **Video Processing**: OpenCV, MoviePy, FFmpeg
- **AI Scoring**: Claude (via Anthropic API)
- **Image Generation** (optional): xAI API

## Design Decisions

See [DESIGN.md](./DESIGN.md) for detailed rationale on:
- Why MCTS over simpler algorithms
- Why Dash over Streamlit
- Why Supabase + Dropbox architecture
- Database schema design
- MCTS parameter tuning

## FAQ

**Q: Is Supabase free plan enough?**
A: Yes! We only store metadata. Estimated 10,000 nodes = ~10MB. Free plan gives 500MB.

**Q: Why not local SQLite?**
A: Multi-dev box scenario requires data sync. Supabase provides real-time sync for free.

**Q: Will Dropbox sync cause conflicts?**
A: No. Database guarantees atomic writes. Files use UUID naming to avoid conflicts.

**Q: MCTS vs simple UCB - what's the difference?**
A: MCTS has full Selection/Expansion/Simulation/Backpropagation. More intelligent than greedy UCB.

**Q: How long does auto mode take?**
A: Depends on iterations and Grok Imagine generation time (~30s per video). 100 iterations ≈ 50min.

**Q: Can I mix manual and auto modes?**
A: Yes! You can manually explore some branches, then let MCTS take over, or vice versa.

**Q: How do I export the final video?**
A: Select the best path in UI → Click "Export Path" → System concatenates all video nodes using FFmpeg.

## Roadmap

### Phase 1: Core Infrastructure (Current)
- ✅ Project setup
- ✅ Database schema
- ✅ Dropbox integration
- 🚧 Basic UI

### Phase 2: Manual Mode
- 🚧 Playwright automation
- 🚧 Video processing
- 🚧 Tree visualization

### Phase 3: Scoring System
- 📋 Quality scorer (Claude Vision)
- 📋 Coherence scorer
- 📋 Semantic scorer

### Phase 4: MCTS Auto Mode
- 📋 MCTS engine
- 📋 Auto exploration loop
- 📋 Real-time monitoring

### Phase 5: Advanced Features
- 📋 Video export/concatenation
- 📋 Batch project management
- 📋 MCP integration
- 📋 Advanced MCTS variants (AlphaGo-style)

## Contributing

This is a personal project for exploring AI-assisted video creation. However, suggestions and ideas are welcome!

## License

MIT

## Acknowledgments

- **Grok Imagine**: Video generation platform by xAI
- **MCTS Algorithm**: Inspired by AlphaGo and game tree search literature
- **LangGraph**: Workflow orchestration framework by LangChain
- **Supabase**: Open-source Firebase alternative
- **Dash/Plotly**: Python visualization framework

---

**Note**: This project is in active development. The README will be updated as features are implemented. For the latest status, check the commit history and issues.

**Context for new Claude Code sessions**: This README contains all necessary context to understand the project architecture, data structures, and implementation approach. When starting a new session in this repo, read this file first to pickup the full context.
