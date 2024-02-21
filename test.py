from lib.fact_check_logic import fact_check

cost_info = []
DUMMY_MESSAGE = "olives make you fat"

response = fact_check(
    DUMMY_MESSAGE, cost_info)
print(response)
print(cost_info)
