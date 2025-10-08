"""Metrics collector for agent evaluation."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import time

from evaluation.metrics import (
    evaluation_runs_total,
    evaluation_test_cases_total,
    evaluation_duration_seconds,
    evaluation_quality_score,
    evaluation_overall_score,
    evaluation_pass_rate,
    agent_tool_usage_total,
    agent_tool_success_rate,
    agent_tool_latency_seconds,
    agent_reasoning_steps,
    agent_memory_retrieval_time,
    agent_memory_hits,
    agent_token_usage,
    agent_response_latency_seconds,
    agent_response_quality_score,
    agent_evaluation_errors_total,
    agent_tool_errors_total,
    initialize_evaluation_info
)

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and exposes metrics during evaluation."""
    
    def __init__(self, judge_model: str = "gpt-3.5-turbo", dataset_version: str = "v1"):
        """Initialize metrics collector."""
        self.judge_model = judge_model
        self.dataset_version = dataset_version
        self.current_run_start = None
        
        # Initialize evaluation info
        initialize_evaluation_info(judge_model, dataset_version)
        
        # Track tool success rates
        self.tool_stats = {}
        
        logger.info("MetricsCollector initialized")
    
    def start_evaluation_run(self, dataset_name: str):
        """Mark the start of an evaluation run."""
        self.current_run_start = time.time()
        logger.info(f"Started evaluation run for dataset: {dataset_name}")
    
    def end_evaluation_run(self, dataset_name: str, status: str = "completed"):
        """Mark the end of an evaluation run."""
        if self.current_run_start:
            duration = time.time() - self.current_run_start
            evaluation_duration_seconds.labels(dataset_name=dataset_name).observe(duration)
            self.current_run_start = None
        
        evaluation_runs_total.labels(
            dataset_name=dataset_name,
            status=status
        ).inc()
        
        logger.info(f"Completed evaluation run for dataset: {dataset_name}, status: {status}")
    
    def record_test_case_result(
        self,
        dataset_name: str,
        category: str,
        difficulty: str,
        result: str
    ):
        """Record a test case result."""
        evaluation_test_cases_total.labels(
            dataset_name=dataset_name,
            category=category,
            difficulty=difficulty,
            result=result
        ).inc()
    
    def record_quality_scores(
        self,
        scores: Dict[str, float],
        category: str = "general"
    ):
        """Record quality dimension scores."""
        for dimension, score in scores.items():
            evaluation_quality_score.labels(
                dimension=dimension,
                category=category
            ).observe(score)
            
            agent_response_quality_score.labels(
                dimension=dimension,
                category=category
            ).set(score)
    
    def record_overall_score(self, dataset_name: str, score: float):
        """Record overall evaluation score."""
        evaluation_overall_score.labels(dataset_name=dataset_name).set(score)
    
    def record_pass_rate(self, dataset_name: str, category: str, pass_rate: float):
        """Record pass rate for a category."""
        evaluation_pass_rate.labels(
            dataset_name=dataset_name,
            category=category
        ).set(pass_rate)
    
    def record_tool_usage(
        self,
        tool_name: str,
        success: bool,
        latency: float
    ):
        """Record tool usage metrics."""
        # Increment usage counter
        agent_tool_usage_total.labels(
            tool_name=tool_name,
            success=str(success).lower()
        ).inc()
        
        # Record latency
        agent_tool_latency_seconds.labels(tool_name=tool_name).observe(latency)
        
        # Update success rate tracking
        if tool_name not in self.tool_stats:
            self.tool_stats[tool_name] = {"successes": 0, "total": 0}
        
        self.tool_stats[tool_name]["total"] += 1
        if success:
            self.tool_stats[tool_name]["successes"] += 1
        
        # Update success rate gauge
        success_rate = self.tool_stats[tool_name]["successes"] / self.tool_stats[tool_name]["total"]
        agent_tool_success_rate.labels(tool_name=tool_name).set(success_rate)
    
    def record_tool_error(self, tool_name: str, error_type: str):
        """Record tool execution error."""
        agent_tool_errors_total.labels(
            tool_name=tool_name,
            error_type=error_type
        ).inc()
    
    def record_reasoning_steps(self, test_case_id: str, num_steps: int):
        """Record number of reasoning steps."""
        agent_reasoning_steps.labels(test_case_id=test_case_id).observe(num_steps)
    
    def record_memory_retrieval(
        self,
        memory_type: str,
        retrieval_time: float,
        relevant: bool = True
    ):
        """Record memory retrieval metrics."""
        agent_memory_retrieval_time.labels(memory_type=memory_type).observe(retrieval_time)
        agent_memory_hits.labels(
            memory_type=memory_type,
            relevant=str(relevant).lower()
        ).inc()
    
    def record_token_usage(self, model: str, operation: str, num_tokens: int):
        """Record token usage."""
        agent_token_usage.labels(model=model, operation=operation).inc(num_tokens)
    
    def record_response_latency(self, category: str, latency: float):
        """Record end-to-end response latency."""
        agent_response_latency_seconds.labels(category=category).observe(latency)
    
    def record_evaluation_error(self, error_type: str, test_case_id: str):
        """Record evaluation error."""
        agent_evaluation_errors_total.labels(
            error_type=error_type,
            test_case_id=test_case_id
        ).inc()
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics from collected metrics."""
        return {
            "tool_success_rates": {
                tool: stats["successes"] / stats["total"]
                for tool, stats in self.tool_stats.items()
                if stats["total"] > 0
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def reset(self):
        """Reset collector state (not metrics themselves)."""
        self.tool_stats = {}
        self.current_run_start = None
        logger.info("MetricsCollector reset")

