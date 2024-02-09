"""Main Function"""
import requests
from lib import utils, perplexity

# List to store cost information
cost_info = []


def initial_fact_checking(claim):
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


def process_fact_check_request(message):
    """
    Process a fact-check request through initial fact-checking and deep analysis.
    """
    # Placeholder for Transcription of Images or Audio
    # TODO: Integrate media transcription services here

    # Placeholder for Language Translation
    # TODO: Detect language and translate if necessary

    # Step 3: Initial Fact-Checking with Datasets/APIs
    fact_check_result = initial_fact_checking(message)

    # Step 4: Advanced Analysis
    # deep_analysis_result_gpt = gpt.deep_analysis_with_gpt4_langchain(
    #     message, fact_check_result, cost_info)
    deep_analysis_result_perplexity = perplexity.deep_analysis_with_perplexity(
        message, fact_check_result, cost_info)

    # Placeholder for Fetching Related News Articles or Official Reports
    # TODO: Integrate news API to fetch related articles

    # Output results
    return {
        "initial_fact_check_result": fact_check_result,
        "deep_analysis_result_perplexity": deep_analysis_result_perplexity,
    }


if __name__ == "__main__":
    DUMMY_MESSAGE = "olives make you fat"
    result = process_fact_check_request(DUMMY_MESSAGE)
    print("Process Result:", result)
    print("Cost Info:", cost_info)
