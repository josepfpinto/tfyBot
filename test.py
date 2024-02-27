from lib.gpt import translate_with_gpt4_langchain

cost_info = []
DUMMY_MESSAGE = "Eu chamo-me José"

message = translate_with_gpt4_langchain(DUMMY_MESSAGE, cost_info)
print(message)
print(cost_info)
