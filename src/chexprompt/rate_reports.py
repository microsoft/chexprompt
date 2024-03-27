import argparse
import os
import logging

import openai

from chexprompt.evaluator import ReportEvaluator
from chexprompt.io import load_reports_to_rate, save_ratings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rate a batch of reports using chexprompt.")
    parser.add_argument(
        "--rating_name",
        type=str,
        help="Name of rating to be saved to output directory.",
        required=True,
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        help="Path to directory to save output reports",
        required=True,
    )
    parser.add_argument(
        "--input_fpath",
        type=str,
        help="Path to file containing reports to rate",
        required=True,
    )
    parser.add_argument(
        "--engine",
        type=str,
        default="gpt-4t",
        help="The model to use for scoring the reports",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.4,
        help="The sampling temperature",
    )
    parser.add_argument(
        "--max_tokens",
        type=int,
        default=128,
        help="The maximum number of tokens to generate",
    )
    parser.add_argument(
        "--top_p",
        type=float,
        default=0.95,
        help="The nucleus sampling probability",
    )
    parser.add_argument(
        "--max_request_per_min",
        type=int,
        default=30,
        help="The maximum number of requests per minute",
    )
    parser.add_argument(
        "--use_async",
        type=bool,
        default=True,
        help="Use async API for faster processing",
    )
    args = parser.parse_args()
    if args.rating_name == "":
        raise ValueError("Rating name cannot be empty.")

    return args

def main():
    args = parse_args()

    evaluator = ReportEvaluator(
        engine=args.engine,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        top_p=args.top_p,
        requests_per_minute=args.max_request_per_min,
        use_async=args.use_async,
    )

    references_candidates_dicts = load_reports_to_rate(args.input_fpath)

    output_path = os.path.join(args.output_dir, f"{args.rating_name}.jsonl")

    if os.path.exists(output_path):
        logging.warning(f"Output file {output_path} already exists. Overwriting.")

    ids = [d["id"] for d in references_candidates_dicts]
    references = [d["reference"] for d in references_candidates_dicts]
    candidates = [d["candidate"] for d in references_candidates_dicts]
    
    results = evaluator.evaluate(references, candidates)

    results_as_dicts = [{"id": ids[i],
                         "reference": references[i],
                         "candidate": candidates[i],
                         "rating": r} for i, r in enumerate(results)]


    
    save_ratings(results_as_dicts, output_path)

if __name__ == '__main__':
    main()