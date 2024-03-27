import json
from typing import List, Dict


def load_reports_to_rate(filepath: str) -> List[Dict[str, str]]:
    """Load reports to rate from a file.
    
    Args:
    - filepath: str, path to the jsonl file containing the reports to rate.
                each line contains a json object with "id", "reference" and "candidate" fields.
    
    Returns:
    - reports: list of dict, each dict contains "id", "reference" and "candidate" fields.
    """

    with open(filepath, 'r') as f:
        reports = [json.loads(line) for line in f]
    return reports


def save_ratings(ratings: List[Dict[str, str]], filepath: str) -> None:
    """Save ratings to a file.
    
    Args:
    - ratings: list of dict, each dict contains "id", "reference", "candidate" and "rating" fields.
    - filepath: str, path to the jsonl file to save the ratings.
    """

    with open(filepath, 'w') as f:
        for rating in ratings:
            json.dump(rating, f)
            f.write('\n')
    return