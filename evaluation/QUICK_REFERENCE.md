# Evaluation System - Quick Reference

## Common Commands

### Run Evaluations

```bash
# Test with 5 cases (quick test)
python evaluation/run_evaluation.py --dataset benchmark_v1 --max-cases 5

# Full benchmark (100 cases)
python evaluation/run_evaluation.py --dataset benchmark_v1

# Edge cases (20 cases)
python evaluation/run_evaluation.py --dataset edge_cases

# Multi-turn conversations (10 scenarios)
python evaluation/run_evaluation.py --dataset multi_turn_conversations

# With verbose logging
python evaluation/run_evaluation.py --dataset benchmark_v1 --verbose

# Use GPT-4 as judge
python evaluation/run_evaluation.py --dataset benchmark_v1 --model gpt-4
```

### Metrics & Monitoring

```bash
# Start metrics server
python evaluation/metrics_server.py

# Custom port
python evaluation/metrics_server.py --port 9092

# View metrics
curl http://localhost:9091/metrics
```

### Reports & Analysis

```bash
# Compare two datasets
python evaluation/run_evaluation.py --compare benchmark_v1 edge_cases

# List datasets
python evaluation/run_evaluation.py --list-datasets

# List results
python evaluation/run_evaluation.py --list-results

# View latest report
cat evaluation/results/report_benchmark_v1_*.md | head -100
```

## File Locations

```
evaluation/
├── datasets/               # Test datasets
│   ├── benchmark_v1.json
│   ├── edge_cases.json
│   └── multi_turn_conversations.json
├── results/                # Generated results
│   ├── results_*.json
│   ├── summary_*.json
│   ├── failures_*.json
│   └── report_*.md
├── config.py               # Configuration
├── run_evaluation.py       # Main CLI
└── README.md               # Full docs
```

## Configuration

### Environment Variables

```bash
# Judge model
export EVAL_JUDGE_MODEL="gpt-3.5-turbo"

# Pass threshold (0-10)
export EVAL_PASS_THRESHOLD="6.0"

# Metrics port
export EVAL_METRICS_PORT="9091"
```

### Config File

Edit `evaluation/config.py`:
- `JUDGE_MODEL`: Model for evaluation
- `PASS_THRESHOLD`: Minimum passing score
- `METRICS_PORT`: Prometheus metrics port

## Evaluation Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Relevance | 1.0 | Addresses query |
| Accuracy | 1.2 | Factually correct |
| Completeness | 0.9 | Covers all aspects |
| Coherence | 0.8 | Logical structure |
| Tool Selection | 1.0 | Right tool chosen |
| Hallucination Detection | 1.1 | No fabrication |

## Scoring

- **0-3**: Poor
- **4-5**: Below average
- **6-7**: Good (passing) ✓
- **8-9**: Excellent
- **10**: Perfect

## Datasets Summary

| Dataset | Cases | Duration | Focus |
|---------|-------|----------|-------|
| benchmark_v1 | 100 | 30-45min | All tools, comprehensive |
| edge_cases | 20 | 10-15min | Error handling, ambiguity |
| multi_turn | 10 | 10-15min | Conversation quality |

## Metrics Quick Reference

### View in Prometheus

```
# Pass rate by category
agent_evaluation_pass_rate{dataset="benchmark_v1", category="product_search"}

# Average quality score
avg(agent_evaluation_quality_score)

# Tool success rate
agent_tool_success_rate{tool_name="search_products"}
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Dataset not found | Use `--list-datasets` to check name |
| MongoDB error | Check MongoDB is running |
| API rate limit | Use `--max-cases 10` to limit |
| Import error | Run from project root directory |

### Quick Fixes

```bash
# Check MongoDB
ps aux | grep mongod

# Test with verbose
python evaluation/run_evaluation.py --dataset benchmark_v1 --max-cases 1 --verbose

# Verify environment
python -c "from evaluation.config import config; print(config.JUDGE_MODEL)"
```

## Expected Results (First Run)

### Benchmark
- Pass Rate: 70-85%
- Avg Score: 7.0-8.5
- Duration: 30-45 min

### Edge Cases
- Pass Rate: 60-75%
- Avg Score: 6.5-7.5
- Duration: 10-15 min

### Multi-Turn
- Pass Rate: 65-80%
- Avg Score: 7.0-8.0
- Duration: 10-15 min

## Best Practices

1. **Start Small**: Test with `--max-cases 5` first
2. **Establish Baseline**: Save first results
3. **Regular Runs**: Evaluate after changes
4. **Monitor Trends**: Use Prometheus + Grafana
5. **Review Failures**: Focus on failed cases

## Documentation Links

- Full Guide: `evaluation/README.md`
- Getting Started: `evaluation/GETTING_STARTED.md`
- Implementation: `evaluation/IMPLEMENTATION_SUMMARY.md`
- This Reference: `evaluation/QUICK_REFERENCE.md`

## Support Commands

```bash
# Help
python evaluation/run_evaluation.py --help

# Check version
python -c "import evaluation; print(evaluation.__version__)"

# List Python packages
pip list | grep -E "langchain|openai|prometheus"
```

---

**Quick Start**: `python evaluation/run_evaluation.py --dataset benchmark_v1 --max-cases 5`

