import json


def convert_query_results_to_json(results):
    """
    Convert query results (list of dictionaries) to a JSON string.

    Args:
        results (list): Query results as a list of dictionaries.

    Returns:
        str: JSON string representation of the query results.
    """
    # Convert the list of dictionaries to a JSON string
    return json.dumps(results, ensure_ascii=False)
