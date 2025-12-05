# GitHistoryPlugin - Real-time Git Repository Analysis

> "Git history is the memory of the system" - Srimad DevOps Purana

## Overview

**GitHistoryPlugin** is a kernel plugin that automatically analyzes your git repository and generates a live **GIT.md** dashboard.

## Features

### 📊 Automatic Analysis
- Runs on kernel boot and every N ticks (configurable)
- Analyzes commit history (default: 7 days, configurable up to 14)
- Zero manual intervention required

### 📈 Metrics Tracked
- **Commit Statistics**: Total commits, velocity (per day/hour), files changed
- **Line Changes**: Insertions, deletions, net change
- **Commit Patterns**: Refactoring, features, fixes, docs, tests
- **Contributors**: Author statistics with percentages
- **File Heatmap**: Most frequently changed files
- **Velocity Trend**: Increasing, stable, or decreasing

### ⚠️ Health Alerts
The plugin automatically flags:
- 🔴 **High Velocity**: >2 commits/hour (scope creep risk)
- 🔴 **Large Commits**: >30% of commits with >500 lines changed
- 🔴 **Low Test Coverage**: <10% test commits
- 🟡 **Refactoring Heavy**: More refactoring than features

## Usage

### Installation

The plugin auto-loads if present in `vibe_core/plugins/`:

```python
# vibe_core/plugins/git_history.py exists
# Kernel automatically discovers and loads it
```

### Configuration

Edit the plugin initialization in your kernel boot sequence:

```python
# Default: 7 days, update every 10 ticks
plugin = GitHistoryPlugin(analysis_days=7, update_interval_ticks=10)

# Extended analysis: 14 days, update every 20 ticks
plugin = GitHistoryPlugin(analysis_days=14, update_interval_ticks=20)

# Frequent updates: 7 days, update every tick
plugin = GitHistoryPlugin(analysis_days=7, update_interval_ticks=1)
```

### Reading GIT.md

The plugin generates **GIT.md** in your repository root:

```bash
# View in terminal
cat GIT.md

# View in browser (if using markdown viewer)
open GIT.md

# Track changes
git diff GIT.md
```

## Architecture

### Plugin Hooks

- **on_boot**: Initial analysis when kernel starts
- **on_tick_post**: Periodic updates (every N ticks)

### Components

1. **GitAnalyzer**: Pure functions for git analysis
   - `is_git_repo()`: Check if directory is a git repo
   - `get_commit_history(days)`: Fetch commits with stats
   - `analyze_commits()`: Generate insights

2. **GitMarkdownRenderer**: Renders GIT.md
   - Markdown tables with statistics
   - Visual bars for file heatmap
   - Health alerts with emojis
   - Recent activity timeline

3. **GitHistoryPlugin**: Kernel integration
   - Lifecycle management (boot, tick)
   - Configuration storage
   - Error handling

### Data Flow

```
┌─────────────────────────────────────────────────────────┐
│ KERNEL BOOT                                             │
│   ↓                                                     │
│ GitHistoryPlugin.on_boot()                              │
│   ↓                                                     │
│ GitAnalyzer.get_commit_history(days=7)                  │
│   ↓                                                     │
│ [Git CLI] → Parse commits → List[CommitInfo]            │
│   ↓                                                     │
│ GitAnalyzer.analyze_commits() → GitAnalysis             │
│   ↓                                                     │
│ GitMarkdownRenderer.render() → GIT.md                   │
│   ↓                                                     │
│ [Filesystem] GIT.md updated ✅                          │
│                                                         │
│ EVERY N TICKS:                                          │
│   Repeat analysis → Update GIT.md                       │
└─────────────────────────────────────────────────────────┘
```

## Example Output

### GIT.md Structure

```markdown
# Git Repository Analysis

## 📊 Commit Statistics
| Metric | Value |
|--------|-------|
| Total Commits | 619 |
| Commits/Day | 88.4 |
| Commits/Hour | 3.68 |
| Files Changed | 1047 |
| Lines Added | +214,464 |
| Lines Removed | -61,811 |
| Net Change | +152,653 |

## 🎯 Commit Patterns
| Pattern | Count | % of Total |
|---------|-------|-----------|
| 🐛 Fixes | 231 | 37.3% |
| ✨ Features | 222 | 35.9% |
| 📝 Documentation | 99 | 16.0% |

## ⚠️ Health Alerts
- 🔴 **HIGH VELOCITY**: Averaging >2 commits/hour
```

## Integration with Other Systems

### Settings Plugin

Future enhancement: Control via SETTINGS.md

```markdown
# SETTINGS.md

## Git History
- Analysis Days: 14
- Update Interval: 20
```

### Help Plugin

Future enhancement: Add `/git` command

```markdown
# HELP.md

## Git Commands
- `/git status` - Show current analysis
- `/git refresh` - Force update GIT.md
- `/git config days=14` - Change time window
```

## Performance

- **Git CLI Overhead**: ~100-300ms for 7 days of history
- **Analysis**: ~50-100ms for pattern detection
- **Rendering**: ~10-20ms for markdown generation
- **Total**: ~200-500ms per update

**Recommendation**: Update interval ≥10 ticks to avoid performance impact.

## Limitations

1. **Git Repo Required**: Plugin disabled if not in git repository
2. **CLI Dependency**: Requires `git` command available in PATH
3. **No Submodule Support**: Only analyzes main repository
4. **Text-based Parsing**: May break with unusual git output formats

## Future Enhancements

### P1 (High Priority)
- [ ] Settings.md integration for configuration
- [ ] Trend analysis (week-over-week comparison)
- [ ] Branch comparison (main vs. feature branches)

### P2 (Medium Priority)
- [ ] Pull request statistics
- [ ] Code review metrics
- [ ] CI/CD integration (test pass rates)

### P3 (Nice to Have)
- [ ] Visual graphs (ASCII art charts)
- [ ] Export to JSON/CSV
- [ ] Slack/Discord notifications for alerts

## Testing

```bash
# Run plugin standalone
python -c "
from vibe_core.plugins.git_history import GitHistoryPlugin
plugin = GitHistoryPlugin(analysis_days=7)
class MockKernel: pass
kernel = MockKernel()
plugin.on_boot(kernel)
"

# Check GIT.md was created
ls -la GIT.md
cat GIT.md

# Verify system integration
python scripts/verify_system.py --fast
```

## Contributing

When modifying this plugin:
1. Keep analysis logic pure (no side effects in GitAnalyzer)
2. Add unit tests for pattern detection
3. Document new metrics in this file
4. Update GIT.md template if adding sections

## Credits

- **Author**: Claude (Sonnet 4.5)
- **Created**: 2025-12-05
- **Pattern**: Inspired by SettingsUIPlugin and EnvoyUIPlugin
- **Philosophy**: Fractal architecture - "as above, so below"

---

*Part of the Steward Protocol Plugin Ecosystem*
