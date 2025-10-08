"""CLI tool to run agent evaluations."""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from evaluation.config import config
from evaluation.evaluator import AgentEvaluator
from evaluation.report_generator import ReportGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def run_evaluation(
    dataset: str,
    output_dir: str = None,
    judge_model: str = None,
    max_cases: int = None,
    generate_report: bool = True
):
    """
    Run evaluation on a dataset.
    
    Args:
        dataset: Dataset name or path
        output_dir: Output directory for results
        judge_model: Model to use for LLM-as-judge
        max_cases: Maximum number of cases to evaluate
        generate_report: Whether to generate markdown report
    """
    logger.info("=" * 60)
    logger.info("Starting Agent Evaluation")
    logger.info("=" * 60)
    
    # Resolve dataset path
    dataset_path = dataset
    if not dataset.endswith('.json'):
        dataset_path = f"{dataset}.json"
    
    # Initialize evaluator
    logger.info(f"Initializing evaluator with judge model: {judge_model or config.JUDGE_MODEL}")
    evaluator = AgentEvaluator(judge_model=judge_model)
    
    try:
        # Run evaluation
        logger.info(f"Evaluating dataset: {dataset_path}")
        summary = await evaluator.evaluate_dataset(
            dataset_path=dataset_path,
            output_dir=output_dir,
            max_cases=max_cases
        )
        
        # Display summary
        logger.info("\n" + "=" * 60)
        logger.info("EVALUATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Dataset: {summary['dataset']}")
        logger.info(f"Total Cases: {summary['total_cases']}")
        logger.info(f"Passed: {summary['passed']} ({summary['pass_rate']*100:.1f}%)")
        logger.info(f"Failed: {summary['failed']}")
        logger.info(f"Errors: {summary['errors']}")
        logger.info(f"Average Overall Score: {summary['avg_overall_score']:.2f}/10")
        logger.info("=" * 60)
        
        # Generate markdown report
        if generate_report:
            # Load detailed results
            output_dir_path = Path(output_dir) if output_dir else config.RESULTS_DIR
            dataset_name = summary['dataset']
            
            summary_obj, results = ReportGenerator.load_latest_results(dataset_name)
            
            if summary_obj and results:
                timestamp = summary['timestamp'].replace(':', '-').replace('.', '-')
                report_file = output_dir_path / f"report_{dataset_name}_{timestamp}.md"
                
                report = ReportGenerator.generate_markdown_report(
                    summary=summary_obj,
                    results=results,
                    output_file=str(report_file)
                )
                
                logger.info(f"Markdown report generated: {report_file}")
        
        logger.info("\nEvaluation completed successfully!")
        return summary
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}", exc_info=True)
        sys.exit(1)


def run_comparison(
    datasets: list,
    output_file: str = None
):
    """
    Generate comparison report across multiple datasets.
    
    Args:
        datasets: List of dataset names
        output_file: Output file for comparison report
    """
    logger.info("Generating comparison report...")
    
    summaries = []
    for dataset in datasets:
        summary, _ = ReportGenerator.load_latest_results(dataset)
        if summary:
            summaries.append(summary)
        else:
            logger.warning(f"No results found for dataset: {dataset}")
    
    if not summaries:
        logger.error("No evaluation results found for comparison")
        sys.exit(1)
    
    output_file = output_file or str(config.RESULTS_DIR / "comparison_report.md")
    report = ReportGenerator.generate_comparison_report(summaries, output_file)
    
    logger.info(f"Comparison report generated: {output_file}")
    print(report)


def list_datasets():
    """List available datasets."""
    logger.info("Available datasets:")
    
    datasets_dir = config.DATASETS_DIR
    if not datasets_dir.exists():
        logger.warning(f"Datasets directory not found: {datasets_dir}")
        return
    
    json_files = list(datasets_dir.glob("*.json"))
    
    if not json_files:
        logger.info("No datasets found")
        return
    
    for dataset_file in sorted(json_files):
        logger.info(f"  - {dataset_file.stem}")


def list_results():
    """List available evaluation results."""
    logger.info("Recent evaluation results:")
    
    results_dir = config.RESULTS_DIR
    if not results_dir.exists():
        logger.warning(f"Results directory not found: {results_dir}")
        return
    
    summary_files = sorted(results_dir.glob("summary_*.json"), reverse=True)
    
    if not summary_files:
        logger.info("No results found")
        return
    
    for summary_file in summary_files[:10]:  # Show last 10
        logger.info(f"  - {summary_file.name}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run agent evaluations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run evaluation on benchmark dataset
  python evaluation/run_evaluation.py --dataset benchmark_v1
  
  # Run with specific judge model
  python evaluation/run_evaluation.py --dataset edge_cases --model gpt-4
  
  # Evaluate first 10 cases only
  python evaluation/run_evaluation.py --dataset benchmark_v1 --max-cases 10
  
  # Compare multiple evaluation runs
  python evaluation/run_evaluation.py --compare benchmark_v1 edge_cases
  
  # List available datasets
  python evaluation/run_evaluation.py --list-datasets
        """
    )
    
    parser.add_argument(
        "--dataset",
        type=str,
        help="Dataset name or path to evaluate"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Output directory for results (default: evaluation/results/)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        help=f"LLM judge model to use (default: {config.JUDGE_MODEL})"
    )
    
    parser.add_argument(
        "--max-cases",
        type=int,
        help="Maximum number of test cases to evaluate"
    )
    
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip generating markdown report"
    )
    
    parser.add_argument(
        "--compare",
        nargs="+",
        help="Compare multiple datasets (provide dataset names)"
    )
    
    parser.add_argument(
        "--list-datasets",
        action="store_true",
        help="List available datasets"
    )
    
    parser.add_argument(
        "--list-results",
        action="store_true",
        help="List recent evaluation results"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Handle list commands
    if args.list_datasets:
        list_datasets()
        return
    
    if args.list_results:
        list_results()
        return
    
    # Handle comparison
    if args.compare:
        run_comparison(args.compare, args.output)
        return
    
    # Require dataset for evaluation
    if not args.dataset:
        parser.print_help()
        sys.exit(1)
    
    # Run evaluation
    asyncio.run(
        run_evaluation(
            dataset=args.dataset,
            output_dir=args.output,
            judge_model=args.model,
            max_cases=args.max_cases,
            generate_report=not args.no_report
        )
    )


if __name__ == "__main__":
    main()

