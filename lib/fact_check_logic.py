"""Main fact check logic"""
import requests
from . import gpt
from . import utils


# WikipediaAPIWrapper!!!!!
def initial_fact_checking(claim, cost_info):
    """
    Fact-checking by querying an external API.
    """
    api_url = f"https://nli.wmflabs.org/fact_checking_aggregated/?claim={
        requests.utils.quote(claim)}"
    headers = {"accept": "application/json"}

    try:
        response = requests.get(api_url, headers=headers, timeout=20)
        if response.status_code == 200:
            cost_info.append(utils.calculate_cost(utils.RequestType.FREE))
            return response.json()
        else:
            return f"Failed to fetch initial fact-checking data {response.status_code}"
    except Exception as e:
        return f"Exception occurred on initial fact-checking: {e}"


def fact_check(message, cost_info):
    """
    Process a fact-check request through initial fact-checking and deep analysis.
    """
    # Step 1: Initial Fact-Checking with Datasets/APIs
    # TODO: improve focusing on wikipedia AND https://toolbox.google.com/factcheck/apis
    fact_check_result = initial_fact_checking(message, cost_info)

    # Step 2: Advanced Analysis with PerplexityAPI OR CHATGPT WITH URLs
    deep_analysis_result = gpt.analyse_claim(
        message, fact_check_result, cost_info)

    # Step 3: Review analysis
    # TODO: Improve implementation with GPT-4 to confirm answer and provide a nuanced perspective
    # TODO: Include the request to assure the answer has no more than xxx char
    # deep_analysis_result_gpt = gpt.review_previous_analysis(message, json.dumps(deep_analysis_result_perplexity), cost_info)

    # Output results
    return {
        "initial_fact_check_result": fact_check_result,
        "deep_analysis": utils.json_to_formatted_string(deep_analysis_result),
    }
