from lib.fact_check_logic import process_fact_check_request

cost_info = []
DUMMY_MESSAGE = "olives make you fat"

response = process_fact_check_request(
    DUMMY_MESSAGE, cost_info)
print(response)
print(cost_info)
