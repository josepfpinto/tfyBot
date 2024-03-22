def router(state):
    print("\nWe are inside ROUTER: ")
    print(state, '\n')

    # The supervisor will route to the next node based on the "next" field
    return state["next"]

    # This is the router
    # messages = state["messages"]
    # last_message = messages[-1]
    # if "function_call" in last_message.additional_kwargs:
    #     # The previus agent is invoking a tool
    #     return "call_tool"
    # if "FINAL ANSWER" in last_message.content:
    #     # Any agent decided the work is done
    #     return "end"
    # return "continue"
