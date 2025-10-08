"""Evaluation criteria and scoring dimensions for agent evaluation."""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class EvaluationDimension:
    """Represents a single evaluation dimension."""
    
    name: str
    description: str
    weight: float
    min_score: int = 0
    max_score: int = 10


class EvaluationCriteria:
    """Defines evaluation criteria and scoring dimensions."""
    
    # Response Quality Dimensions
    RELEVANCE = EvaluationDimension(
        name="relevance",
        description="How well does the response address the user's query?",
        weight=1.0
    )
    
    ACCURACY = EvaluationDimension(
        name="accuracy",
        description="Is the information provided factually correct?",
        weight=1.2
    )
    
    COMPLETENESS = EvaluationDimension(
        name="completeness",
        description="Does the response cover all aspects of the query?",
        weight=0.9
    )
    
    COHERENCE = EvaluationDimension(
        name="coherence",
        description="Is the response logically structured and easy to understand?",
        weight=0.8
    )
    
    # Tool Usage Dimensions
    TOOL_SELECTION = EvaluationDimension(
        name="tool_selection",
        description="Did the agent select the appropriate tool(s)?",
        weight=1.0
    )
    
    PARAMETER_EXTRACTION = EvaluationDimension(
        name="parameter_extraction",
        description="Were tool parameters extracted correctly from the user input?",
        weight=0.9
    )
    
    TOOL_SUCCESS = EvaluationDimension(
        name="tool_success",
        description="Did the tool execution complete successfully?",
        weight=0.8
    )
    
    # Memory Utilization Dimensions
    MEMORY_RETRIEVAL = EvaluationDimension(
        name="memory_retrieval",
        description="Did the agent retrieve relevant memories?",
        weight=0.7
    )
    
    MEMORY_USAGE = EvaluationDimension(
        name="memory_usage",
        description="Did the agent effectively use retrieved memories in the response?",
        weight=0.7
    )
    
    # Conversation Quality Dimensions
    CONTEXT_MAINTENANCE = EvaluationDimension(
        name="context_maintenance",
        description="Does the response maintain context from previous turns?",
        weight=0.8
    )
    
    CLARITY = EvaluationDimension(
        name="clarity",
        description="Is the response clear and unambiguous?",
        weight=0.8
    )
    
    # Safety Dimensions
    HALLUCINATION_DETECTION = EvaluationDimension(
        name="hallucination_detection",
        description="Does the response avoid making up information?",
        weight=1.1
    )
    
    UNCERTAINTY_EXPRESSION = EvaluationDimension(
        name="uncertainty_expression",
        description="Does the agent appropriately express uncertainty when needed?",
        weight=0.7
    )
    
    @classmethod
    def get_all_dimensions(cls) -> List[EvaluationDimension]:
        """Get all evaluation dimensions."""
        return [
            cls.RELEVANCE,
            cls.ACCURACY,
            cls.COMPLETENESS,
            cls.COHERENCE,
            cls.TOOL_SELECTION,
            cls.PARAMETER_EXTRACTION,
            cls.TOOL_SUCCESS,
            cls.MEMORY_RETRIEVAL,
            cls.MEMORY_USAGE,
            cls.CONTEXT_MAINTENANCE,
            cls.CLARITY,
            cls.HALLUCINATION_DETECTION,
            cls.UNCERTAINTY_EXPRESSION
        ]
    
    @classmethod
    def get_dimension_by_name(cls, name: str) -> EvaluationDimension:
        """Get a specific evaluation dimension by name."""
        dimensions = {dim.name: dim for dim in cls.get_all_dimensions()}
        return dimensions.get(name)
    
    @classmethod
    def get_primary_dimensions(cls) -> List[EvaluationDimension]:
        """Get primary evaluation dimensions (most important)."""
        return [
            cls.RELEVANCE,
            cls.ACCURACY,
            cls.COMPLETENESS,
            cls.COHERENCE,
            cls.TOOL_SELECTION
        ]
    
    @classmethod
    def calculate_weighted_score(cls, scores: Dict[str, float]) -> float:
        """
        Calculate weighted average score across dimensions.
        
        Args:
            scores: Dictionary mapping dimension names to scores
            
        Returns:
            Weighted average score (0-10)
        """
        total_weight = 0.0
        weighted_sum = 0.0
        
        for dimension in cls.get_all_dimensions():
            if dimension.name in scores:
                score = scores[dimension.name]
                weighted_sum += score * dimension.weight
                total_weight += dimension.weight
        
        if total_weight == 0:
            return 0.0
        
        return weighted_sum / total_weight


class TestCaseCategory:
    """Categories for test cases."""
    
    PRODUCT_SEARCH = "product_search"
    APPOINTMENT = "appointment"
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"
    WEB_SEARCH = "web_search"
    MULTI_TOOL = "multi_tool"
    CONVERSATION = "conversation"
    
    @classmethod
    def all_categories(cls) -> List[str]:
        """Get all test case categories."""
        return [
            cls.PRODUCT_SEARCH,
            cls.APPOINTMENT,
            cls.KNOWLEDGE_RETRIEVAL,
            cls.WEB_SEARCH,
            cls.MULTI_TOOL,
            cls.CONVERSATION
        ]


class DifficultyLevel:
    """Difficulty levels for test cases."""
    
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    
    @classmethod
    def all_levels(cls) -> List[str]:
        """Get all difficulty levels."""
        return [cls.EASY, cls.MEDIUM, cls.HARD]

