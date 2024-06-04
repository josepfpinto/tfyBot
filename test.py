"""Testing"""

from tests import test_functions

# -------------
# Resolver /test
# test_functions.test_environment_variables()
# test_functions.test_saving_in_db()
# test_functions.test_saving_user()
# test_functions.test_fetching_of_chat_history()
# test_functions.test_if_new_message_has_arrived()
# test_functions.test_changing_user_language()
# test_functions.test_get_user_language()
# test_functions.test_fetching_user_language()

# -------------
# Test via requests that simmulates the WhatsApp API
# test_functions.test_welcome_message() # OK - 2022-03-02
test_functions.test_greeting_message()
# test_functions.test_changing_language("Spanish")

# TODO:
# Test button change language (with a prefered language and without one)
# Test button fact check + cancel

# Test WhatsApp + FACT CHECKING

# Test button fact check + ready: "Olives make you fat"
# Test button fact check + add more + ready: "Breast milk is a very good substitute" + "for COVID-19 vaccines"

# -------------
# CLAIMS TO TEST
# Breast milk is a very good substitute for COVID-19 vaccines. FALSE
# Technically, since Ukraine never officially registered its borders with the United Nations, Russia has not committed any violation of international law by invading its territory. FALSE
# Groups of Pakistani students used Indian flags in order to escape from Ukraine during the Russian invasion. FALSE
# Health care costs per person in the U.S. are one of the highest in the developed world. TRUE
# Image1 FALSE
# Image2 FALSE
# Image3 FALSE
# Image4 TRUE
# Image5 FALSE
# Image6 FALSE
# Image7 FALSE

# -------------
# OLD TESTS

# initial_state = {"messages": [HumanMessage(content=DUMMY_MESSAGE)], "history": []}
# response = graph.invoke(initial_state)
# final_message_content = response.get("messages")[0].content
# this_logger.info("response: %s", response)
# this_logger.info("final_message_content: %s", final_message_content)
