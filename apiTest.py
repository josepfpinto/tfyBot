from dotenv import load_dotenv
import os
import requests
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, ChatMessage


# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Setup for LangChain
chat_gpt = ChatOpenAI(temperature=0, api_key=OPENAI_API_KEY)


# Adjust to bypass errors and add the error message to the next step
def initial_fact_checking(claim):
    """
    Fact-checking by querying an external API.
    """
    api_url = f"https://nli.wmflabs.org/fact_checking_aggregated/?claim={
        requests.utils.quote(claim)}"
    headers = {"accept": "application/json"}

    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch fact-checking data", "status_code": response.status_code}
    except Exception as e:
        return {"error": f"Exception occurred: {e}"}


def deep_analysis_with_gpt4_langchain(claim, previous_step_result):
    """
    Perform deep analysis on a claim using LangChain with an OpenAI model, considering previous steps' output.
    """
    # If leveraging dialogue over several turns, you might update the context here
    # chat_gpt.update_context(...) # This method might vary depending on LangChain's future updates

    # Constructing the messages list to include both the user's claim and the preliminary fact-checking result
    previous_result_str = str(previous_step_result)
    messages = [
        SystemMessage(
            content="Assess the truthfulness of the following claim:"
        ),
        HumanMessage(
            content=claim
        ),
        ChatMessage(
            role="assistant",
            content=f'''A preliminary fact-check was done with this result:
                {previous_result_str}'''
        ),
    ]

    print(
        f"A preliminary fact-check was done with this result: {previous_step_result}")

    # Use the chat model to generate a response based on the conversation history
    response = chat_gpt.invoke(messages, max_tokens=250)
    print('chatgpt4')
    print(response)

    # Extracting and returning the generated text from the response
    return response[-1]['content'] if response else "No response generated."


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
    # 4.1: Complexity Assessment (Optional)
    # TODO: Integrate Perplexity API if needed

    # 4.2: Deep Analysis with GPT-4
    # TODO: Integrate OpenAI GPT-4 API for deep analysis
    deep_analysis_result = deep_analysis_with_gpt4_langchain(
        message, fact_check_result)

    # Placeholder for Fetching Related News Articles or Official Reports
    # TODO: Integrate news API to fetch related articles

    # Output results
    return {
        "initial_fact_check_result": fact_check_result,
        "deep_analysis_result": deep_analysis_result,
    }


if __name__ == "__main__":
    dummy_message = "olives make you fat"
    result = process_fact_check_request(dummy_message)
    print("Process Result:", result)
