# Agent Evaluation System

Comprehensive evaluation framework for the Dexter AI Agent, featuring automated quality assessment, benchmark datasets, and Prometheus metrics integration.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Datasets](#datasets)
- [Running Evaluations](#running-evaluations)
- [Metrics and Monitoring](#metrics-and-monitoring)
- [Evaluation Criteria](#evaluation-criteria)
- [Reports](#reports)
- [Extending the Framework](#extending-the-framework)
- [Troubleshooting](#troubleshooting)

## Overview

The evaluation system provides:

- **Benchmark Datasets**: 100+ test cases covering all agent capabilities
- **LLM-as-Judge**: Automated quality assessment using GPT-3.5-turbo
- **Prometheus Metrics**: Real-time monitoring of agent performance
- **Comprehensive Reports**: Detailed analysis of evaluation results
- **Multi-dimensional Scoring**: Quality, tool usage, safety, and conversation metrics

## Quick Start

### 1. Install Dependencies

All required dependencies are in the main `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Run Your First Evaluation

```bash
# Run the benchmark dataset
python evaluation/run_evaluation.py --dataset benchmark_v1

# Run with first 10 cases only (for testing)
python evaluation/run_evaluation.py --dataset benchmark_v1 --max-cases 10
```

### 3. View Results

Results are saved in `evaluation/results/`:

```bash
# View latest results
ls -lt evaluation/results/

# Generate a report from latest run
python evaluation/run_evaluation.py --dataset benchmark_v1 --generate-report
```

### 4. Start Metrics Server (Optional)

```bash
# Start Prometheus metrics endpoint
python evaluation/metrics_server.py

# Metrics available at http://localhost:9091/metrics
```

## Architecture

### Components

```
evaluation/
├── config.py                  # Configuration settings
├── evaluator.py               # Core evaluation engine
├── criteria.py                # Evaluation dimensions and scoring
├── judge_prompts.py           # LLM-as-judge prompts
├── metrics.py                 # Prometheus metrics definitions
├── metrics_collector.py       # Metrics collection logic
├── metrics_server.py          # Metrics HTTP server
├── report_generator.py        # Report generation
├── run_evaluation.py          # CLI tool
├── datasets/                  # Test case datasets
│   ├── benchmark_v1.json
│   ├── edge_cases.json
│   └── multi_turn_conversations.json
└── results/                   # Evaluation results
```

### Evaluation Flow

```
Test Case → Agent Execution → Collect Metadata → LLM Judge → Scoring → Metrics & Reports
```

## Datasets

### Benchmark Dataset (`benchmark_v1.json`)

100 test cases covering all agent capabilities:

- **Product Search** (25 cases): Price ranges, categories, features, complex queries
- **Appointments** (25 cases): Booking, cancellation, rescheduling, complex scheduling
- **Knowledge Retrieval** (25 cases): Policy queries, FAQs, troubleshooting
- **Web Search** (25 cases): Current events, comparisons, information lookup

**Difficulty Levels**:
- Easy: 40 cases - Basic single-intent queries
- Medium: 40 cases - Multi-parameter or contextual queries
- Hard: 20 cases - Complex, ambiguous, or multi-step queries

### Edge Cases Dataset (`edge_cases.json`)

20 challenging scenarios:

- **Ambiguous Queries**: Unclear intent, missing context
- **Contradictory Requests**: Conflicting requirements
- **Out-of-Scope**: Requests beyond agent capabilities
- **Error Handling**: Invalid inputs, impossible requests
- **Safety**: Privacy, security, ethical boundaries

### Multi-Turn Conversations (`multi_turn_conversations.json`)

10 conversation scenarios (3-5 turns each):

- Progressive refinement
- Context switching
- Information correction
- Multi-intent conversations
- Complex negotiations

## Running Evaluations

### Basic Usage

```bash
# Evaluate all test cases in a dataset
python evaluation/run_evaluation.py --dataset benchmark_v1

# Evaluate specific dataset
python evaluation/run_evaluation.py --dataset edge_cases

# Limit number of cases
python evaluation/run_evaluation.py --dataset benchmark_v1 --max-cases 25
```

### Advanced Options

```bash
# Use different judge model
python evaluation/run_evaluation.py --dataset benchmark_v1 --model gpt-4

# Custom output directory
python evaluation/run_evaluation.py --dataset benchmark_v1 --output custom_results/

# Skip report generation
python evaluation/run_evaluation.py --dataset benchmark_v1 --no-report

# Verbose logging
python evaluation/run_evaluation.py --dataset benchmark_v1 --verbose
```

### Compare Evaluations

```bash
# Compare multiple evaluation runs
python evaluation/run_evaluation.py --compare benchmark_v1 edge_cases

# Save comparison report
python evaluation/run_evaluation.py --compare benchmark_v1 edge_cases --output comparison.md
```

### List Available Datasets

```bash
# List all datasets
python evaluation/run_evaluation.py --list-datasets

# List recent results
python evaluation/run_evaluation.py --list-results
```

## Metrics and Monitoring

### Prometheus Integration

The evaluation system exposes metrics on port 9091 by default.

#### Start Metrics Server

```bash
python evaluation/metrics_server.py

# Custom port
python evaluation/metrics_server.py --port 9092
```

#### Update Prometheus Config

The `monitoring/prometheus.yml` is already configured to scrape evaluation metrics:

```yaml
scrape_configs:
  - job_name: 'ai_agent_evaluation'
    static_configs:
      - targets: ['localhost:9091']
```

#### Available Metrics

**Evaluation Metrics**:
- `agent_evaluation_runs_total` - Total evaluation runs
- `agent_evaluation_test_cases_total` - Test cases by result
- `agent_evaluation_duration_seconds` - Evaluation run duration
- `agent_evaluation_quality_score` - Quality scores by dimension
- `agent_evaluation_pass_rate` - Pass rate by category

**Agent Performance Metrics**:
- `agent_tool_usage_total` - Tool usage counts
- `agent_tool_success_rate` - Success rate per tool
- `agent_tool_latency_seconds` - Tool execution latency
- `agent_response_latency_seconds` - End-to-end response time
- `agent_response_quality_score` - Quality scores
- `agent_memory_retrieval_time_seconds` - Memory operation timing

**Error Metrics**:
- `agent_evaluation_errors_total` - Evaluation errors
- `agent_tool_errors_total` - Tool execution errors

### Grafana Dashboards

Create custom dashboards in Grafana to visualize:

- Pass rate trends over time
- Quality score distributions
- Tool usage patterns
- Latency percentiles
- Error rates

## Evaluation Criteria

### Primary Dimensions

#### Response Quality (Weight: 1.0-1.2)
- **Relevance** (1.0): Addresses user's query
- **Accuracy** (1.2): Factually correct information
- **Completeness** (0.9): Covers all aspects
- **Coherence** (0.8): Logically structured
- **Clarity** (0.8): Easy to understand

#### Tool Usage (Weight: 0.8-1.0)
- **Tool Selection** (1.0): Right tool chosen
- **Parameter Extraction** (0.9): Correct parameters
- **Tool Success** (0.8): Successful execution

#### Safety (Weight: 0.7-1.1)
- **Hallucination Detection** (1.1): No fabricated info
- **Uncertainty Expression** (0.7): Admits uncertainty

#### Conversation (Weight: 0.8)
- **Context Maintenance** (0.8): Maintains conversation context
- **Coherence** (0.8): Natural flow

#### Memory (Weight: 0.7)
- **Memory Retrieval** (0.7): Retrieves relevant memories
- **Memory Usage** (0.7): Uses memories effectively

### Scoring Scale

- **0-3**: Poor/Unacceptable
- **4-5**: Below Average
- **6-7**: Good/Acceptable ✓
- **8-9**: Excellent
- **10**: Perfect

**Pass Threshold**: 6.0 (configurable in `config.py`)

### Weighted Overall Score

The overall score is calculated as a weighted average across all applicable dimensions, with higher weights for critical dimensions like accuracy and hallucination detection.

## Reports

### Markdown Reports

Automatically generated after each evaluation:

```
evaluation/results/
├── results_benchmark_v1_20240108_143052.json      # Detailed results
├── summary_benchmark_v1_20240108_143052.json      # Summary statistics
├── failures_benchmark_v1_20240108_143052.json     # Failed cases only
└── report_benchmark_v1_20240108_143052.md         # Human-readable report
```

### Report Contents

- **Summary Statistics**: Pass rate, average scores, counts
- **Dimension Scores**: Visual bars showing scores by dimension
- **Category Performance**: Breakdown by tool/category
- **Failed Cases**: Details of failures with scores and errors
- **Top Performers**: Best-scoring test cases

### Comparison Reports

Generate comparison reports across multiple runs:

```bash
python evaluation/run_evaluation.py --compare benchmark_v1 edge_cases
```

Comparison reports include:
- Side-by-side metrics
- Score trends across runs
- Dimension-by-dimension comparison
- Category performance comparison

## Extending the Framework

### Adding New Test Cases

Edit dataset JSON files:

```json
{
  "id": "unique_id",
  "category": "product_search",
  "difficulty": "medium",
  "user_message": "Your test query",
  "expected_behavior": "What should happen",
  "expected_tool": "tool_name",
  "expected_parameters": {
    "param": "value"
  },
  "evaluation_criteria": ["criteria1", "criteria2"],
  "multi_turn": false,
  "context_messages": []
}
```

### Creating Custom Datasets

1. Create a new JSON file in `evaluation/datasets/`
2. Follow the schema from existing datasets
3. Run evaluation: `python evaluation/run_evaluation.py --dataset your_dataset`

### Adding Evaluation Dimensions

Edit `evaluation/criteria.py`:

```python
NEW_DIMENSION = EvaluationDimension(
    name="your_dimension",
    description="What it measures",
    weight=1.0
)
```

### Custom Judge Prompts

Edit `evaluation/judge_prompts.py` to customize evaluation prompts.

### Custom Metrics

Add new metrics in `evaluation/metrics.py`:

```python
from prometheus_client import Counter, Gauge, Histogram

your_metric = Counter(
    'your_metric_name',
    'Description',
    ['label1', 'label2']
)
```

## Configuration

Edit `evaluation/config.py` to customize:

```python
class EvaluationConfig:
    # LLM Judge
    JUDGE_MODEL = "gpt-3.5-turbo"  # or "gpt-4"
    JUDGE_TEMPERATURE = 0.1
    
    # Evaluation
    MAX_RETRIES = 3
    TIMEOUT_SECONDS = 60
    PASS_THRESHOLD = 6.0
    
    # Metrics
    ENABLE_METRICS = True
    METRICS_PORT = 9091
```

## Troubleshooting

### Common Issues

#### 1. "Dataset not found"

```bash
# Check available datasets
python evaluation/run_evaluation.py --list-datasets

# Use correct path
python evaluation/run_evaluation.py --dataset evaluation/datasets/benchmark_v1.json
```

#### 2. API Rate Limits

The evaluation system includes delays between test cases. If you hit rate limits:

- Use `--max-cases` to limit evaluation size
- Increase delays in `evaluator.py` (line with `asyncio.sleep`)
- Use GPT-3.5-turbo instead of GPT-4

#### 3. Metrics Server Port Already in Use

```bash
# Use different port
python evaluation/metrics_server.py --port 9092

# Update prometheus.yml accordingly
```

#### 4. Low Quality Scores

If all scores are low:
- Check judge model is working (`--model gpt-4` for better judgments)
- Verify agent is properly initialized
- Review judge prompts in `judge_prompts.py`
- Check agent logs for errors

#### 5. Evaluation Takes Too Long

```bash
# Test with subset first
python evaluation/run_evaluation.py --dataset benchmark_v1 --max-cases 10

# Use faster judge model
python evaluation/run_evaluation.py --dataset benchmark_v1 --model gpt-3.5-turbo
```

### Debug Mode

Enable verbose logging:

```bash
python evaluation/run_evaluation.py --dataset benchmark_v1 --verbose
```

### Validation

Validate your dataset structure:

```python
import json
with open('evaluation/datasets/your_dataset.json') as f:
    data = json.load(f)
    print(f"Loaded {len(data)} test cases")
```

## Best Practices

### Running Evaluations

1. **Start Small**: Test with `--max-cases 10` first
2. **Baseline**: Run evaluations before making changes to establish baseline
3. **Regular Runs**: Evaluate after significant code changes
4. **Version Control**: Commit evaluation results for comparison
5. **Monitor Metrics**: Watch Prometheus metrics during evaluation

### Creating Test Cases

1. **Cover Edge Cases**: Include ambiguous, contradictory, and error scenarios
2. **Realistic Queries**: Use natural language users would actually use
3. **Diverse Difficulty**: Mix easy, medium, and hard cases
4. **Clear Expectations**: Specify expected behavior precisely
5. **Meaningful Criteria**: Choose relevant evaluation criteria

### Interpreting Results

1. **Look at Trends**: Compare across multiple runs
2. **Category Analysis**: Identify which tools/categories need improvement
3. **Failed Cases**: Focus on understanding why cases fail
4. **Dimension Scores**: Identify specific weaknesses (e.g., tool selection)
5. **Context Matters**: Consider test difficulty when evaluating scores

## Support and Contribution

### Getting Help

- Check this README first
- Review example datasets for reference
- Check logs with `--verbose` flag
- Review code comments in evaluation modules

### Contributing

To contribute new test cases or improvements:

1. Create test cases following existing schema
2. Test locally with `--max-cases` first
3. Document any new evaluation criteria
4. Update this README if adding major features

## Appendix

### File Structure

```
evaluation/
├── __init__.py                # Package initialization
├── README.md                  # This file
├── config.py                  # Configuration
├── criteria.py                # Evaluation dimensions
├── evaluator.py               # Core evaluation engine
├── judge_prompts.py           # LLM judge prompts
├── metrics.py                 # Prometheus metrics
├── metrics_collector.py       # Metrics collection
├── metrics_server.py          # Metrics HTTP server
├── report_generator.py        # Report generation
├── run_evaluation.py          # CLI entry point
├── datasets/                  # Test datasets
│   ├── benchmark_v1.json      # Main benchmark (100 cases)
│   ├── edge_cases.json        # Edge cases (20 cases)
│   └── multi_turn_conversations.json  # Conversations (10 scenarios)
└── results/                   # Evaluation results
    └── .gitkeep
```

### Environment Variables

```bash
# Judge model configuration
export EVAL_JUDGE_MODEL="gpt-3.5-turbo"
export EVAL_JUDGE_TEMPERATURE="0.1"

# Evaluation settings
export EVAL_MAX_RETRIES="3"
export EVAL_TIMEOUT_SECONDS="60"

# Metrics
export EVAL_ENABLE_METRICS="true"
export EVAL_METRICS_PORT="9091"
```

### Example Output

```
============================================================
Starting Agent Evaluation
============================================================
Initializing evaluator with judge model: gpt-3.5-turbo
Evaluating dataset: benchmark_v1.json
Progress: 1/100
Progress: 2/100
...
============================================================
EVALUATION SUMMARY
============================================================
Dataset: benchmark_v1
Total Cases: 100
Passed: 85 (85.0%)
Failed: 15
Errors: 0
Average Overall Score: 7.82/10
============================================================
Markdown report generated: evaluation/results/report_benchmark_v1_20240108_143052.md
```

---

**Version**: 0.1.0  
**Last Updated**: 2024  
**Maintainer**: Dexter AI Team

