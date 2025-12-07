# Design Decisions

This document records all major design decisions made during the project planning phase, including the rationale and trade-offs considered.

## Table of Contents

1. [UI Framework Selection](#ui-framework-selection)
2. [Algorithm Choice: MCTS](#algorithm-choice-mcts)
3. [Architecture: Supabase + Dropbox](#architecture-supabase--dropbox)
4. [Data Structure Design](#data-structure-design)
5. [Workflow Design](#workflow-design)
6. [Technology Stack](#technology-stack)

---

## UI Framework Selection

### Decision: Dash (Plotly)

**Considered Options**:
1. **Streamlit** - Python-native, simple
2. **Dash** - Plotly-based, production-grade
3. **Gradio** - ML demo focused
4. **Reflex** - Modern, React-like
5. **Open WebUI** - Full-featured AI chat platform

### Comparison Matrix

| Feature | Streamlit | Dash | Gradio | Reflex | Open WebUI |
|---------|-----------|------|--------|--------|------------|
| Tree Visualization | ✅ Plotly | ✅✅ Plotly native | ❌ Limited | ⚠️ Needs integration | ❌ Custom required |
| Code Complexity | ⭐ Low | ⭐⭐⭐ Medium | ⭐ Low | ⭐⭐⭐ Medium | ⭐⭐⭐⭐⭐ High |
| Performance | ⚠️ Reruns | ✅✅ Callbacks | ⚠️ Reruns | ✅✅ WebSocket | ✅ WebSocket |
| Suitability | ✅ Good | ✅✅✅ Best | ❌ Poor | ✅ Good | ❌ Not designed for this |

### Rationale for Dash

**Key insight**: In AI-assisted development, traditional concerns change:

| Traditional Concern | Human Development | AI-Assisted Development |
|---------------------|-------------------|------------------------|
| Learning curve | ❌ Important | ✅ Not a concern (AI knows it) |
| Code complexity | ❌ Important | ✅ Not a concern (AI generates) |
| Boilerplate code | ❌ Annoying | ✅ Not a concern (AI writes) |
| Final performance | ✅ Important | ✅✅ Still important |
| Flexibility | ✅ Important | ✅✅ Still important |
| Scalability | ✅ Important | ✅✅ Still important |

**Dash wins because**:
1. ✅ Best performance (fine-grained callbacks, no full page reruns)
2. ✅ Best tree visualization (Plotly native support)
3. ✅ Production-grade maturity (used by Fortune 500)
4. ✅ Maximum flexibility for complex interactions
5. ✅ AI can generate Dash code as easily as Streamlit

**Why not Streamlit?**
- Originally considered for "AI-era simplicity"
- But in AI-assisted development, code simplicity doesn't matter
- Performance and flexibility matter more
- Streamlit's full-page reruns would hurt UX with large trees

**Why not others?**
- Gradio: Too constrained, no tree visualization
- Reflex: Too new, risky for production
- Open WebUI: Designed for chat, not tree exploration

---

## Algorithm Choice: MCTS

### Decision: Full MCTS (Monte Carlo Tree Search)

**Considered Options**:
1. **UCB1** (Upper Confidence Bound) - Simpler, stateless
2. **MCTS** - Full tree search with simulation
3. **Beam Search** - Keep top-K at each level
4. **Random Exploration** - Baseline

### Why MCTS?

**MCTS is the gold standard for tree exploration**:
- ✅ Used in AlphaGo, game AI, decision trees
- ✅ Automatically balances exploration vs exploitation
- ✅ Handles uncertainty well (video generation is stochastic)
- ✅ Proven theoretical foundations

**UCB1 vs Full MCTS**:
| Feature | UCB1 | Full MCTS |
|---------|------|-----------|
| Complexity | Low | Medium |
| Memory | O(nodes) | O(nodes) + simulation cache |
| Quality | Good | Better |
| Theoretical backing | Strong | Stronger |

**Decision**: Start with full MCTS, not simplified UCB
- User requested MCTS explicitly
- Performance difference is worth it for video quality
- Can always simplify later if needed

### MCTS Four Phases

```
1. SELECTION
   Use UCB to traverse from root to leaf
   Balances visiting promising nodes vs exploring new ones

2. EXPANSION
   Generate new child node (video) if not fully expanded
   Calls Playwright to generate video via Grok Imagine

3. SIMULATION (Evaluation)
   Score the new node across multiple dimensions:
   - Quality: AI vision model assessment
   - Coherence: Smooth transition from parent
   - Semantic: Matches original prompt
   - Diversity: Exploration value

4. BACKPROPAGATION
   Update statistics for all ancestors:
   - visit_count++
   - total_reward += reward
   - avg_reward = total_reward / visit_count
```

### UCB Formula

```
UCB(node) = avg_reward + c * sqrt(ln(parent_visits) / node_visits)
```

- **c = 1.414 (√2)**: Standard exploration constant
- Higher c → more exploration
- Lower c → more exploitation

**Tuning strategy**:
- Start with c=1.414 (theory-backed default)
- Increase if stuck in local optima
- Decrease if quality is already good

---

## Architecture: Supabase + Dropbox

### Decision: Supabase for metadata, Dropbox for files

**Requirement**: Multi-device development
- User has multiple dev boxes
- Needs seamless sync without manual effort
- Database and files must stay consistent

**Considered Options**:

| Option | Pros | Cons |
|--------|------|------|
| Local SQLite + Dropbox sync | Simple | ❌ DB conflicts, corruption risk |
| Cloud DB + Cloud Storage | Professional | ⚠️ Cost, complexity |
| **Supabase + Dropbox** | Free, auto-sync | ✅ Winner |

### Why Supabase?

**Supabase PostgreSQL** (free tier):
- ✅ 500MB database space (we need ~10MB)
- ✅ Real-time sync across devices
- ✅ No conflict resolution needed (ACID guarantees)
- ✅ Powerful queries (PostgreSQL full power)
- ✅ Free API access, no rate limits for our usage

**Why not local SQLite?**
- ❌ Dropbox syncing SQLite → corruption risk
- ❌ Write conflicts between devices
- ❌ No ACID guarantees across sync

### Why Dropbox?

**Dropbox for media files**:
- ✅ User already has Plus plan (2TB)
- ✅ Desktop app already installed on all dev boxes
- ✅ Auto-sync, no configuration needed
- ✅ File versioning (safety net)
- ✅ Direct file access (no API needed)

**Why not cloud storage?**
- AWS S3: ⚠️ Need API, credentials, costs
- Google Drive: ⚠️ API rate limits
- Supabase Storage: ⚠️ Free tier only 1GB

### File Structure Design

```
~/Dropbox/grok-imagine-expert/
└── projects/
    └── {project-id}/
        ├── passes/
        │   └── {pass-id}/
        │       ├── images/
        │       └── videos/
        └── exports/
```

**Design principles**:
1. **UUID-based filenames** → No conflicts across devices
2. **Hierarchical organization** → Easy navigation
3. **Separate from existing grok/ folder** → No interference with grok-organizer project
4. **Project isolation** → Easy to archive/delete entire projects

---

## Data Structure Design

### Node-centric Tree Model

**Core insight**: The tree is dynamic and grows at runtime.
- ❌ LangGraph nodes ≠ our tree nodes
- ✅ LangGraph = execution engine (fixed workflow)
- ✅ Our tree = data structure (stored in DB)

### Database Schema Highlights

**nodes table** - Heart of the system:
```sql
CREATE TABLE nodes (
    id UUID PRIMARY KEY,
    parent_id UUID REFERENCES nodes(id),
    node_type TEXT,  -- 'image' or 'video'
    file_path TEXT,  -- Dropbox relative path

    -- MCTS core
    visit_count INTEGER,
    total_reward REAL,
    avg_reward REAL,
    is_fully_expanded BOOLEAN,

    -- Multi-dimensional scores
    quality_score REAL,
    coherence_score REAL,
    semantic_score REAL,
    diversity_score REAL,

    -- Metadata
    metadata JSONB
);
```

**Design decisions**:

1. **UUID primary keys**
   - Device-agnostic (no auto-increment conflicts)
   - Unpredictable (security)
   - Globally unique

2. **Separate node_type for images and videos**
   - Could have used single "media" type
   - Explicit types make queries clearer
   - Different processing logic for each

3. **JSONB metadata column**
   - Flexibility for future extensions
   - Don't need to alter schema for new fields
   - Can store prompt variations, generation params, etc.

4. **Multi-dimensional scores as columns**
   - Could have used JSONB for all scores
   - Separate columns → easier queries, indexes
   - Type safety (REAL with CHECK constraints)

5. **is_fully_expanded flag**
   - Needed for MCTS expansion phase
   - Could compute dynamically (count children)
   - Stored flag → faster queries, clearer logic

### Supporting Tables

**passes table**:
- Groups nodes into exploration sessions
- Each pass = one initial image → one tree
- Allows multiple attempts with same/different initial images

**projects table**:
- Groups multiple passes
- Project-level settings
- Easier batch operations

**generations table**:
- Async task queue
- Tracks Playwright automation status
- Decouples generation from tree structure

---

## Workflow Design

### Two Modes: Manual and Auto

**Manual Mode** - Human-in-the-loop:
```
1. User uploads initial image
2. System generates M candidates (e.g., M=5)
3. User selects N candidates (e.g., N=2)
4. System creates N branches
5. User can jump to any node and repeat
```

**Auto Mode** - MCTS-driven:
```
1. User uploads initial image + sets parameters
2. System runs MCTS iterations:
   For i in range(iterations):
       - Selection: UCB chooses leaf
       - Expansion: Generate 1 new video
       - Simulation: Score the video
       - Backpropagation: Update ancestors
3. User views tree + best path
4. User can export or manually continue
```

### Hybrid Mode (Future)

- User manually explores some branches
- Flags certain nodes as "promising"
- MCTS focuses on those subtrees
- Best of both worlds: human intuition + algorithmic thoroughness

### Tree Navigation

**Jump to any node**:
- Not a linear workflow
- User can revisit any historical node
- Generate new candidates from anywhere
- Creates true tree exploration

**Implementation**:
- Store `current_node_id` in UI state
- LangGraph agent loads node context from DB
- No dependency on execution history

---

## Technology Stack

### Core Stack

| Layer | Technology | Why |
|-------|------------|-----|
| UI | Dash + Plotly | Best tree viz, production-grade |
| Backend | Python 3.11+ | AI ecosystem, LangGraph support |
| Workflow | LangGraph | Agent orchestration, checkpointing |
| Database | Supabase PostgreSQL | Free, real-time sync |
| Storage | Dropbox | Already available, auto-sync |
| Automation | Playwright | Grok Imagine has no API |
| Video | OpenCV, MoviePy, FFmpeg | Industry standard |
| AI Scoring | Claude (Anthropic API) | Vision model for quality |

### Why LangGraph?

**LangGraph for orchestration**:
- ✅ Built for agentic workflows
- ✅ Checkpointing (resume after failures)
- ✅ Human-in-the-loop primitives
- ✅ Tools/actions framework
- ✅ State management

**Not for the tree structure**:
- ❌ LangGraph nodes ≠ tree nodes
- ✅ LangGraph = execution engine
- ✅ Tree = data in Supabase

### Why Playwright?

**Grok Imagine has no official API**:
- xAI API only supports images, not videos
- Must use web interface
- Playwright is the best web automation tool

**Why Playwright over Selenium?**
- ✅ Modern, async-first
- ✅ Better reliability
- ✅ Auto-waiting mechanisms
- ✅ Multi-browser support

---

## Future Considerations

### Potential Enhancements

1. **Advanced MCTS Variants**
   - AlphaGo-style policy networks
   - RAVE (Rapid Action Value Estimation)
   - Progressive widening

2. **Parallel Generation**
   - Multiple Playwright instances
   - Faster tree growth
   - Distributed across dev boxes

3. **Learned Scoring**
   - Train ML model on user preferences
   - Replace hand-crafted reward weights
   - Personalized video quality

4. **Video Understanding**
   - Scene detection
   - Object tracking across frames
   - Semantic segmentation for coherence

5. **MCP Integration**
   - Expose as MCP tools
   - Claude Code can trigger explorations
   - Natural language control

### Open Questions

1. **How to handle very deep trees (depth > 20)?**
   - May need tree pruning
   - Progressive summarization
   - Focus on promising branches only

2. **How to compare paths of different lengths?**
   - Normalize rewards by path length?
   - Discount factor for depth?
   - User preference for short vs long videos?

3. **Optimal MCTS parameters?**
   - Depends on use case (quality vs diversity)
   - May need adaptive tuning
   - A/B testing framework?

---

## Lessons from Planning

### What Went Well

1. **Iterative refinement**
   - Started with simple ideas
   - User questions revealed complexity
   - Converged on robust design

2. **AI-assisted development mindset**
   - Recognized that code complexity ≠ problem
   - Chose best tech, not easiest tech
   - Let AI handle boilerplate

3. **Separation of concerns**
   - Tree data ≠ workflow graph
   - Metadata (Supabase) ≠ files (Dropbox)
   - Manual mode ≠ auto mode (but share infrastructure)

### What We Learned

1. **Don't confuse LangGraph graph with data tree**
   - Initial designs mixed these up
   - Clear separation made everything easier

2. **Multi-device sync is non-trivial**
   - Local SQLite sync → corruption
   - Cloud database is essential
   - File storage must handle conflicts

3. **MCTS needs careful schema design**
   - is_fully_expanded flag is crucial
   - visit_count must be accurate
   - Indexes matter for UCB queries

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-07 | Use Dash over Streamlit | AI-assisted dev changes cost calculus |
| 2025-12-07 | Full MCTS over simple UCB | User request + better results worth complexity |
| 2025-12-07 | Supabase + Dropbox | Multi-device sync, free tier sufficient |
| 2025-12-07 | UUID filenames | Avoid conflicts across devices |
| 2025-12-07 | Multi-dimensional scoring | Richer feedback than single score |
| 2025-12-07 | LangGraph as engine, not tree | Separation of concerns |

---

**Note**: This is a living document. As implementation progresses, we may discover new insights and update these decisions accordingly. The goal is to maintain clarity on *why* we made each choice, not just *what* we chose.
