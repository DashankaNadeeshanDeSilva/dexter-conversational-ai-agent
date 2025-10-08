"""Prometheus metrics definitions for agent evaluation."""

from prometheus_client import Counter, Histogram, Gauge, Info


# Evaluation Run Metrics
evaluation_runs_total = Counter(
    'agent_evaluation_runs_total',
    'Total number of evaluation runs',
    ['dataset_name', 'status']
)

evaluation_test_cases_total = Counter(
    'agent_evaluation_test_cases_total',
    'Total number of test cases evaluated',
    ['dataset_name', 'category', 'difficulty', 'result']
)

evaluation_duration_seconds = Histogram(
    'agent_evaluation_duration_seconds',
    'Duration of evaluation runs in seconds',
    ['dataset_name'],
    buckets=[10, 30, 60, 120, 300, 600, 1800, 3600]
)

# Quality Score Metrics
evaluation_quality_score = Histogram(
    'agent_evaluation_quality_score',
    'Quality scores from evaluations',
    ['dimension', 'category'],
    buckets=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
)

evaluation_overall_score = Gauge(
    'agent_evaluation_overall_score',
    'Current overall evaluation score',
    ['dataset_name']
)

evaluation_pass_rate = Gauge(
    'agent_evaluation_pass_rate',
    'Percentage of test cases that passed',
    ['dataset_name', 'category']
)

# Agent Performance Metrics
agent_tool_usage_total = Counter(
    'agent_tool_usage_total',
    'Total number of times each tool was used',
    ['tool_name', 'success']
)

agent_tool_success_rate = Gauge(
    'agent_tool_success_rate',
    'Success rate for each tool (0-1)',
    ['tool_name']
)

agent_tool_latency_seconds = Histogram(
    'agent_tool_latency_seconds',
    'Latency of tool execution in seconds',
    ['tool_name'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

agent_reasoning_steps = Histogram(
    'agent_reasoning_steps',
    'Number of reasoning steps taken by agent',
    ['test_case_id'],
    buckets=[1, 2, 3, 4, 5, 7, 10, 15, 20]
)

agent_memory_retrieval_time = Histogram(
    'agent_memory_retrieval_time_seconds',
    'Time taken to retrieve memories',
    ['memory_type'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

agent_memory_hits = Counter(
    'agent_memory_hits_total',
    'Number of successful memory retrievals',
    ['memory_type', 'relevant']
)

agent_token_usage = Counter(
    'agent_token_usage_total',
    'Total tokens used by the agent',
    ['model', 'operation']
)

agent_response_latency_seconds = Histogram(
    'agent_response_latency_seconds',
    'End-to-end response latency',
    ['category'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 60.0]
)

agent_response_quality_score = Gauge(
    'agent_response_quality_score',
    'Response quality scores by dimension',
    ['dimension', 'category']
)

# Error Metrics
agent_evaluation_errors_total = Counter(
    'agent_evaluation_errors_total',
    'Total number of errors during evaluation',
    ['error_type', 'test_case_id']
)

agent_tool_errors_total = Counter(
    'agent_tool_errors_total',
    'Total number of tool execution errors',
    ['tool_name', 'error_type']
)

# Evaluation Info
evaluation_info = Info(
    'agent_evaluation_info',
    'Information about the current evaluation configuration'
)


def initialize_evaluation_info(judge_model: str, dataset_version: str):
    """Initialize evaluation info metric."""
    evaluation_info.info({
        'judge_model': judge_model,
        'dataset_version': dataset_version,
        'evaluator_version': '0.1.0'
    })

