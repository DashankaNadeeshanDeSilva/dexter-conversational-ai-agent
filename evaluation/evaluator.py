"""Core agent evaluator service."""

import json
import logging
import time
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import asyncio

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.agent.agent import ReActAgent
from app.memory.memory_manager import MemoryManager
from evaluation.config import config
from evaluation.criteria import EvaluationCriteria, TestCaseCategory
from evaluation.judge_prompts import JudgePrompts
from evaluation.metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)


class AgentEvaluator:
    """Main evaluation service that wraps the agent."""
    
    def __init__(
        self,
        agent: ReActAgent = None,
        memory_manager: MemoryManager = None,
        judge_model: str = None
    ):
        """
        Initialize the evaluator.
        
        Args:
            agent: ReAct agent instance (will create if not provided)
            memory_manager: Memory manager instance (will create if not provided)
            judge_model: Model to use for LLM-as-judge evaluation
        """
        self.judge_model = judge_model or config.JUDGE_MODEL
        
        # Initialize memory manager and agent if not provided
        if memory_manager is None:
            memory_manager = MemoryManager()
        
        if agent is None:
            agent = ReActAgent(memory_manager=memory_manager)
        
        self.agent = agent
        self.memory_manager = memory_manager
        
        # Initialize LLM judge
        self.judge_llm = ChatOpenAI(
            model=self.judge_model,
            temperature=config.JUDGE_TEMPERATURE,
            max_tokens=config.JUDGE_MAX_TOKENS
        )
        
        # Initialize metrics collector
        self.metrics_collector = MetricsCollector(
            judge_model=self.judge_model,
            dataset_version="v1"
        )
        
        logger.info(f"AgentEvaluator initialized with judge model: {self.judge_model}")
    
    async def evaluate_single_case(
        self,
        test_case: Dict[str, Any],
        user_id: str = None,
        session_id: str = None,
        conversation_id: str = None
    ) -> Dict[str, Any]:
        """
        Run single test case and evaluate response.
        
        Args:
            test_case: Test case dictionary
            user_id: User ID for the test
            session_id: Session ID for the test
            conversation_id: Conversation ID for the test
            
        Returns:
            Evaluation result dictionary
        """
        test_case_id = test_case.get("id", str(uuid.uuid4()))
        category = test_case.get("category", "unknown")
        difficulty = test_case.get("difficulty", "unknown")
        
        logger.info(f"Evaluating test case {test_case_id}: {category}/{difficulty}")
        
        # Generate IDs if not provided
        user_id = user_id or f"eval_user_{test_case_id}"
        session_id = session_id or f"eval_session_{test_case_id}"
        conversation_id = conversation_id or f"eval_conv_{test_case_id}"
        
        result = {
            "test_case_id": test_case_id,
            "category": category,
            "difficulty": difficulty,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed",
            "error": None
        }
        
        try:
            # Extract test case details
            user_message = test_case.get("user_message", "")
            expected_behavior = test_case.get("expected_behavior", "")
            expected_tool = test_case.get("expected_tool", "")
            expected_parameters = test_case.get("expected_parameters", {})
            context_messages = test_case.get("context_messages", [])
            multi_turn = test_case.get("multi_turn", False)
            
            # Handle multi-turn conversations
            if multi_turn and context_messages:
                for ctx_msg in context_messages:
                    if ctx_msg.get("role") == "user":
                        await self.agent.process_message(
                            user_id=user_id,
                            session_id=session_id,
                            conversation_id=conversation_id,
                            message=ctx_msg.get("content", "")
                        )
            
            # Execute agent with timing
            start_time = time.time()
            agent_response = await self.agent.process_message(
                user_id=user_id,
                session_id=session_id,
                conversation_id=conversation_id,
                message=user_message
            )
            execution_time = time.time() - start_time
            
            # Record response latency
            self.metrics_collector.record_response_latency(category, execution_time)
            
            # Extract execution metadata
            # (In a real implementation, we'd instrument the agent to capture this)
            tools_used = self._extract_tools_used(agent_response)
            tool_parameters = {}
            tool_results = []
            
            # Evaluate response quality
            quality_scores = await self._evaluate_response_quality(
                user_query=user_message,
                agent_response=agent_response,
                expected_behavior=expected_behavior,
                context_messages=context_messages
            )
            
            # Evaluate tool usage if tools were expected
            tool_scores = {}
            if expected_tool:
                tool_scores = await self._evaluate_tool_usage(
                    user_query=user_message,
                    expected_tool=expected_tool,
                    actual_tools_used=tools_used,
                    tool_parameters=tool_parameters,
                    expected_parameters=expected_parameters,
                    tool_results=tool_results
                )
            
            # Evaluate safety
            safety_scores = await self._evaluate_safety(
                user_query=user_message,
                agent_response=agent_response
            )
            
            # Combine all scores
            all_scores = {**quality_scores, **tool_scores, **safety_scores}
            
            # Calculate overall score
            overall_score = EvaluationCriteria.calculate_weighted_score(all_scores)
            
            # Determine pass/fail
            passed = overall_score >= config.PASS_THRESHOLD
            
            # Update result
            result.update({
                "status": "completed",
                "passed": passed,
                "agent_response": agent_response,
                "execution_time_seconds": execution_time,
                "tools_used": tools_used,
                "scores": all_scores,
                "overall_score": overall_score
            })
            
            # Record metrics
            self.metrics_collector.record_test_case_result(
                dataset_name=test_case.get("dataset", "unknown"),
                category=category,
                difficulty=difficulty,
                result="passed" if passed else "failed"
            )
            
            self.metrics_collector.record_quality_scores(all_scores, category)
            
            # Record tool usage metrics
            for tool in tools_used:
                self.metrics_collector.record_tool_usage(
                    tool_name=tool,
                    success=True,
                    latency=execution_time / len(tools_used) if tools_used else execution_time
                )
            
            logger.info(f"Test case {test_case_id} completed: {'PASSED' if passed else 'FAILED'} (score: {overall_score:.2f})")
            
        except Exception as e:
            logger.error(f"Error evaluating test case {test_case_id}: {e}", exc_info=True)
            result["error"] = str(e)
            result["status"] = "error"
            
            self.metrics_collector.record_evaluation_error(
                error_type=type(e).__name__,
                test_case_id=test_case_id
            )
        
        return result
    
    async def _evaluate_response_quality(
        self,
        user_query: str,
        agent_response: str,
        expected_behavior: str,
        context_messages: List[Dict[str, str]] = None
    ) -> Dict[str, float]:
        """Evaluate response quality using LLM-as-judge."""
        
        prompt = JudgePrompts.create_general_evaluation_prompt(
            user_query=user_query,
            agent_response=agent_response,
            expected_behavior=expected_behavior,
            context_messages=context_messages
        )
        
        try:
            messages = [
                SystemMessage(content=JudgePrompts.SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = await self.judge_llm.ainvoke(messages)
            
            # Parse JSON response
            evaluation = json.loads(response.content)
            
            # Extract scores
            scores = {}
            for dimension in ["relevance", "accuracy", "completeness", "coherence", "clarity"]:
                if dimension in evaluation and isinstance(evaluation[dimension], dict):
                    scores[dimension] = float(evaluation[dimension].get("score", 0))
            
            return scores
            
        except Exception as e:
            logger.error(f"Error in quality evaluation: {e}")
            # Return default scores on error
            return {
                "relevance": 0.0,
                "accuracy": 0.0,
                "completeness": 0.0,
                "coherence": 0.0,
                "clarity": 0.0
            }
    
    async def _evaluate_tool_usage(
        self,
        user_query: str,
        expected_tool: str,
        actual_tools_used: List[str],
        tool_parameters: Dict[str, Any],
        expected_parameters: Dict[str, Any],
        tool_results: List[str]
    ) -> Dict[str, float]:
        """Evaluate tool usage using LLM-as-judge."""
        
        prompt = JudgePrompts.create_tool_usage_evaluation_prompt(
            user_query=user_query,
            expected_tool=expected_tool,
            actual_tools_used=actual_tools_used,
            tool_parameters=tool_parameters,
            expected_parameters=expected_parameters,
            tool_results=tool_results
        )
        
        try:
            messages = [
                SystemMessage(content=JudgePrompts.SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = await self.judge_llm.ainvoke(messages)
            evaluation = json.loads(response.content)
            
            scores = {}
            for dimension in ["tool_selection", "parameter_extraction", "tool_success"]:
                if dimension in evaluation and isinstance(evaluation[dimension], dict):
                    scores[dimension] = float(evaluation[dimension].get("score", 0))
            
            return scores
            
        except Exception as e:
            logger.error(f"Error in tool usage evaluation: {e}")
            return {
                "tool_selection": 0.0,
                "parameter_extraction": 0.0,
                "tool_success": 0.0
            }
    
    async def _evaluate_safety(
        self,
        user_query: str,
        agent_response: str,
        ground_truth: str = None
    ) -> Dict[str, float]:
        """Evaluate safety aspects using LLM-as-judge."""
        
        prompt = JudgePrompts.create_safety_evaluation_prompt(
            user_query=user_query,
            agent_response=agent_response,
            ground_truth=ground_truth
        )
        
        try:
            messages = [
                SystemMessage(content=JudgePrompts.SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = await self.judge_llm.ainvoke(messages)
            evaluation = json.loads(response.content)
            
            scores = {}
            for dimension in ["hallucination_detection", "uncertainty_expression"]:
                if dimension in evaluation and isinstance(evaluation[dimension], dict):
                    scores[dimension] = float(evaluation[dimension].get("score", 0))
            
            return scores
            
        except Exception as e:
            logger.error(f"Error in safety evaluation: {e}")
            return {
                "hallucination_detection": 0.0,
                "uncertainty_expression": 0.0
            }
    
    def _extract_tools_used(self, agent_response: str) -> List[str]:
        """
        Extract tools used from agent response.
        
        This is a simplified version. In practice, we'd instrument the agent
        to track tool usage directly.
        """
        tools = []
        tool_keywords = {
            "search_products": "product",
            "book_appointment": "appointment",
            "retrieve_knowledge": "knowledge",
            "web_search": "search"
        }
        
        response_lower = agent_response.lower()
        for tool, keyword in tool_keywords.items():
            if keyword in response_lower:
                tools.append(tool)
        
        return tools
    
    async def evaluate_dataset(
        self,
        dataset_path: str,
        output_dir: str = None,
        max_cases: int = None
    ) -> Dict[str, Any]:
        """
        Run full dataset evaluation.
        
        Args:
            dataset_path: Path to dataset JSON file
            output_dir: Directory to save results (default: config.RESULTS_DIR)
            max_cases: Maximum number of cases to evaluate (None for all)
            
        Returns:
            Summary results dictionary
        """
        dataset_file = Path(dataset_path)
        if not dataset_file.exists():
            # Try relative to datasets directory
            dataset_file = config.DATASETS_DIR / dataset_path
            if not dataset_file.exists():
                raise FileNotFoundError(f"Dataset not found: {dataset_path}")
        
        dataset_name = dataset_file.stem
        output_dir = Path(output_dir) if output_dir else config.RESULTS_DIR
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Starting evaluation of dataset: {dataset_name}")
        
        # Load dataset
        with open(dataset_file, "r") as f:
            test_cases = json.load(f)
        
        if max_cases:
            test_cases = test_cases[:max_cases]
        
        # Start metrics collection
        self.metrics_collector.start_evaluation_run(dataset_name)
        
        # Evaluate all test cases
        results = []
        for i, test_case in enumerate(test_cases):
            logger.info(f"Progress: {i+1}/{len(test_cases)}")
            
            # Add dataset name to test case
            test_case["dataset"] = dataset_name
            
            result = await self.evaluate_single_case(test_case)
            results.append(result)
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
        
        # Calculate aggregate metrics
        summary = self._calculate_summary(results, dataset_name)
        
        # End metrics collection
        self.metrics_collector.end_evaluation_run(dataset_name, "completed")
        
        # Record overall metrics
        self.metrics_collector.record_overall_score(dataset_name, summary["avg_overall_score"])
        
        # Save results
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        results_file = output_dir / f"results_{dataset_name}_{timestamp}.json"
        summary_file = output_dir / f"summary_{dataset_name}_{timestamp}.json"
        failures_file = output_dir / f"failures_{dataset_name}_{timestamp}.json"
        
        # Save detailed results
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        
        # Save summary
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        # Save failures only
        failures = [r for r in results if not r.get("passed", False)]
        with open(failures_file, "w") as f:
            json.dump(failures, f, indent=2)
        
        logger.info(f"Evaluation complete. Results saved to {output_dir}")
        logger.info(f"Summary: {summary['total_cases']} cases, {summary['passed']} passed, {summary['failed']} failed")
        logger.info(f"Average score: {summary['avg_overall_score']:.2f}")
        
        return summary
    
    def _calculate_summary(self, results: List[Dict[str, Any]], dataset_name: str) -> Dict[str, Any]:
        """Calculate aggregate metrics from evaluation results."""
        
        total = len(results)
        passed = sum(1 for r in results if r.get("passed", False))
        failed = sum(1 for r in results if not r.get("passed", False))
        errors = sum(1 for r in results if r.get("status") == "error")
        
        # Calculate average scores
        scores_by_dimension = {}
        all_overall_scores = []
        
        for result in results:
            if result.get("scores"):
                for dim, score in result["scores"].items():
                    if dim not in scores_by_dimension:
                        scores_by_dimension[dim] = []
                    scores_by_dimension[dim].append(score)
            
            if result.get("overall_score"):
                all_overall_scores.append(result["overall_score"])
        
        avg_scores = {
            dim: sum(scores) / len(scores) if scores else 0.0
            for dim, scores in scores_by_dimension.items()
        }
        
        avg_overall = sum(all_overall_scores) / len(all_overall_scores) if all_overall_scores else 0.0
        
        # Calculate per-category metrics
        by_category = {}
        for result in results:
            category = result.get("category", "unknown")
            if category not in by_category:
                by_category[category] = {"total": 0, "passed": 0, "failed": 0}
            
            by_category[category]["total"] += 1
            if result.get("passed", False):
                by_category[category]["passed"] += 1
            else:
                by_category[category]["failed"] += 1
        
        # Calculate pass rates
        for category, stats in by_category.items():
            pass_rate = stats["passed"] / stats["total"] if stats["total"] > 0 else 0.0
            self.metrics_collector.record_pass_rate(dataset_name, category, pass_rate)
        
        return {
            "dataset": dataset_name,
            "timestamp": datetime.utcnow().isoformat(),
            "total_cases": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "pass_rate": passed / total if total > 0 else 0.0,
            "avg_overall_score": avg_overall,
            "avg_scores_by_dimension": avg_scores,
            "by_category": by_category
        }

