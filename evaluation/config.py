"""Configuration for the evaluation system."""

import os
from pathlib import Path
from typing import Optional


class EvaluationConfig:
    """Configuration settings for agent evaluation."""
    
    # LLM Judge Settings
    JUDGE_MODEL: str = os.getenv("EVAL_JUDGE_MODEL", "gpt-3.5-turbo")
    JUDGE_TEMPERATURE: float = float(os.getenv("EVAL_JUDGE_TEMPERATURE", "0.1"))
    JUDGE_MAX_TOKENS: int = int(os.getenv("EVAL_JUDGE_MAX_TOKENS", "1000"))
    
    # Evaluation Settings
    MAX_RETRIES: int = int(os.getenv("EVAL_MAX_RETRIES", "3"))
    TIMEOUT_SECONDS: int = int(os.getenv("EVAL_TIMEOUT_SECONDS", "60"))
    CONCURRENT_EVALUATIONS: int = int(os.getenv("EVAL_CONCURRENT", "5"))
    
    # Metrics Settings
    ENABLE_METRICS: bool = os.getenv("EVAL_ENABLE_METRICS", "true").lower() == "true"
    METRICS_PORT: int = int(os.getenv("EVAL_METRICS_PORT", "9091"))
    METRICS_HOST: str = os.getenv("EVAL_METRICS_HOST", "0.0.0.0")
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent
    DATASETS_DIR: Path = BASE_DIR / "datasets"
    RESULTS_DIR: Path = BASE_DIR / "results"
    
    # Scoring thresholds
    PASS_THRESHOLD: float = 6.0  # Minimum score to consider a test case passed
    QUALITY_DIMENSIONS: list = [
        "relevance",
        "accuracy", 
        "completeness",
        "coherence",
        "tool_usage"
    ]
    
    # Dataset names
    BENCHMARK_DATASET: str = "benchmark_v1"
    EDGE_CASES_DATASET: str = "edge_cases"
    MULTI_TURN_DATASET: str = "multi_turn_conversations"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        cls.DATASETS_DIR.mkdir(parents=True, exist_ok=True)
        cls.RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# Initialize configuration
config = EvaluationConfig()
config.ensure_directories()

