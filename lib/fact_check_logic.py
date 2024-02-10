"""Main fact check logic"""
import requests
from . import utils
from . import perplexity


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


def process_fact_check_request(message, cost_info):
    """
    Process a fact-check request through initial fact-checking and deep analysis.
    """
    # Step 1: Initial Fact-Checking with Datasets/APIs
    fact_check_result = initial_fact_checking(message, cost_info)

    # Step 2: Advanced Analysis
    # deep_analysis_result_gpt = gpt.deep_analysis_with_gpt4_langchain(
    #     message, fact_check_result, cost_info)
    deep_analysis_result_perplexity = perplexity.deep_analysis_with_perplexity(
        message, fact_check_result, cost_info)

    # Placeholder for Fetching Related News Articles or Official Reports
    # TODO: Integrate news API to fetch related articles

    # Output results
    return {
        "initial_fact_check_result": fact_check_result,
        "deep_analysis": deep_analysis_result_perplexity,
    }
