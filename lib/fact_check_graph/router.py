def router(state):
    print("\nWe are inside ROUTER: ")
    print(state, '\n')
    return state["next"]
