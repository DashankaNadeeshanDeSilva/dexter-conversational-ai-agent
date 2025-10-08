"""Generate human-readable evaluation reports."""

import json
import logging
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from evaluation.config import config

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate evaluation reports in various formats."""
    
    @staticmethod
    def generate_markdown_report(
        summary: Dict[str, Any],
        results: List[Dict[str, Any]],
        output_file: str = None
    ) -> str:
        """
        Generate a markdown summary report.
        
        Args:
            summary: Summary statistics
            results: Detailed test results
            output_file: Optional file path to save report
            
        Returns:
            Markdown report string
        """
        report_lines = []
        
        # Header
        report_lines.append(f"# Evaluation Report: {summary['dataset']}")
        report_lines.append(f"\n**Generated:** {summary['timestamp']}")
        report_lines.append(f"\n## Summary\n")
        
        # Overall metrics
        report_lines.append(f"- **Total Test Cases:** {summary['total_cases']}")
        report_lines.append(f"- **Passed:** {summary['passed']} ({summary['pass_rate']*100:.1f}%)")
        report_lines.append(f"- **Failed:** {summary['failed']}")
        report_lines.append(f"- **Errors:** {summary['errors']}")
        report_lines.append(f"- **Average Overall Score:** {summary['avg_overall_score']:.2f}/10")
        
        # Scores by dimension
        report_lines.append(f"\n## Scores by Dimension\n")
        for dimension, score in sorted(summary['avg_scores_by_dimension'].items()):
            bar = "█" * int(score) + "░" * (10 - int(score))
            report_lines.append(f"- **{dimension.replace('_', ' ').title()}:** {score:.2f}/10 [{bar}]")
        
        # Performance by category
        report_lines.append(f"\n## Performance by Category\n")
        for category, stats in summary['by_category'].items():
            pass_rate = stats['passed'] / stats['total'] if stats['total'] > 0 else 0.0
            report_lines.append(f"\n### {category.replace('_', ' ').title()}")
            report_lines.append(f"- Total: {stats['total']}")
            report_lines.append(f"- Passed: {stats['passed']}")
            report_lines.append(f"- Failed: {stats['failed']}")
            report_lines.append(f"- Pass Rate: {pass_rate*100:.1f}%")
        
        # Failed cases details
        failed_cases = [r for r in results if not r.get("passed", False)]
        if failed_cases:
            report_lines.append(f"\n## Failed Test Cases ({len(failed_cases)})\n")
            for case in failed_cases[:10]:  # Limit to first 10
                report_lines.append(f"\n### Test Case: {case.get('test_case_id', 'unknown')}")
                report_lines.append(f"- **Category:** {case.get('category', 'unknown')}")
                report_lines.append(f"- **Difficulty:** {case.get('difficulty', 'unknown')}")
                report_lines.append(f"- **Score:** {case.get('overall_score', 0):.2f}/10")
                if case.get('error'):
                    report_lines.append(f"- **Error:** {case['error']}")
            
            if len(failed_cases) > 10:
                report_lines.append(f"\n*({len(failed_cases) - 10} more failed cases not shown)*")
        
        # Top performing cases
        passed_cases = [r for r in results if r.get("passed", False)]
        if passed_cases:
            top_cases = sorted(passed_cases, key=lambda x: x.get("overall_score", 0), reverse=True)[:5]
            report_lines.append(f"\n## Top Performing Cases\n")
            for i, case in enumerate(top_cases, 1):
                report_lines.append(f"{i}. **{case.get('test_case_id', 'unknown')}** - Score: {case.get('overall_score', 0):.2f}/10")
        
        report_content = "\n".join(report_lines)
        
        # Save to file if requested
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(report_content)
            logger.info(f"Markdown report saved to {output_path}")
        
        return report_content
    
    @staticmethod
    def generate_comparison_report(
        summaries: List[Dict[str, Any]],
        output_file: str = None
    ) -> str:
        """
        Generate a comparison report across multiple evaluation runs.
        
        Args:
            summaries: List of summary dictionaries from different runs
            output_file: Optional file path to save report
            
        Returns:
            Markdown comparison report string
        """
        if not summaries:
            return "No evaluation summaries provided for comparison."
        
        report_lines = []
        
        # Header
        report_lines.append("# Evaluation Comparison Report")
        report_lines.append(f"\n**Generated:** {datetime.utcnow().isoformat()}")
        report_lines.append(f"\n**Comparing {len(summaries)} evaluation runs**\n")
        
        # Overall comparison table
        report_lines.append("## Overall Metrics Comparison\n")
        report_lines.append("| Run | Dataset | Total Cases | Pass Rate | Avg Score |")
        report_lines.append("|-----|---------|-------------|-----------|-----------|")
        
        for i, summary in enumerate(summaries, 1):
            report_lines.append(
                f"| Run {i} | {summary.get('dataset', 'N/A')} | "
                f"{summary.get('total_cases', 0)} | "
                f"{summary.get('pass_rate', 0)*100:.1f}% | "
                f"{summary.get('avg_overall_score', 0):.2f}/10 |"
            )
        
        # Dimension comparison
        report_lines.append("\n## Score Comparison by Dimension\n")
        
        # Collect all dimensions
        all_dimensions = set()
        for summary in summaries:
            all_dimensions.update(summary.get('avg_scores_by_dimension', {}).keys())
        
        for dimension in sorted(all_dimensions):
            report_lines.append(f"\n### {dimension.replace('_', ' ').title()}")
            report_lines.append("| Run | Score | Change |")
            report_lines.append("|-----|-------|--------|")
            
            prev_score = None
            for i, summary in enumerate(summaries, 1):
                score = summary.get('avg_scores_by_dimension', {}).get(dimension, 0.0)
                change = ""
                if prev_score is not None:
                    diff = score - prev_score
                    arrow = "↑" if diff > 0 else "↓" if diff < 0 else "→"
                    change = f"{arrow} {abs(diff):.2f}"
                report_lines.append(f"| Run {i} | {score:.2f} | {change} |")
                prev_score = score
        
        # Category comparison
        report_lines.append("\n## Category Performance Comparison\n")
        
        # Collect all categories
        all_categories = set()
        for summary in summaries:
            all_categories.update(summary.get('by_category', {}).keys())
        
        for category in sorted(all_categories):
            report_lines.append(f"\n### {category.replace('_', ' ').title()}")
            report_lines.append("| Run | Pass Rate | Passed/Total |")
            report_lines.append("|-----|-----------|--------------|")
            
            for i, summary in enumerate(summaries, 1):
                cat_stats = summary.get('by_category', {}).get(category, {})
                total = cat_stats.get('total', 0)
                passed = cat_stats.get('passed', 0)
                pass_rate = (passed / total * 100) if total > 0 else 0.0
                report_lines.append(f"| Run {i} | {pass_rate:.1f}% | {passed}/{total} |")
        
        report_content = "\n".join(report_lines)
        
        # Save to file if requested
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(report_content)
            logger.info(f"Comparison report saved to {output_path}")
        
        return report_content
    
    @staticmethod
    def load_latest_results(dataset_name: str = None) -> tuple:
        """
        Load the most recent results and summary for a dataset.
        
        Args:
            dataset_name: Name of dataset (None for most recent overall)
            
        Returns:
            Tuple of (summary, results) or (None, None) if not found
        """
        results_dir = config.RESULTS_DIR
        
        # Find matching files
        pattern = f"summary_{dataset_name}_*.json" if dataset_name else "summary_*.json"
        summary_files = sorted(results_dir.glob(pattern), reverse=True)
        
        if not summary_files:
            logger.warning(f"No summary files found for pattern: {pattern}")
            return None, None
        
        # Load most recent
        summary_file = summary_files[0]
        with open(summary_file, "r") as f:
            summary = json.load(f)
        
        # Load corresponding results file
        results_file = summary_file.parent / summary_file.name.replace("summary_", "results_")
        if results_file.exists():
            with open(results_file, "r") as f:
                results = json.load(f)
        else:
            results = []
        
        return summary, results
    
    @staticmethod
    def generate_report_for_latest(dataset_name: str = None, output_file: str = None) -> str:
        """
        Generate a markdown report for the most recent evaluation run.
        
        Args:
            dataset_name: Name of dataset (None for most recent overall)
            output_file: Optional file path to save report
            
        Returns:
            Markdown report string
        """
        summary, results = ReportGenerator.load_latest_results(dataset_name)
        
        if summary is None:
            return "No evaluation results found."
        
        return ReportGenerator.generate_markdown_report(summary, results, output_file)

