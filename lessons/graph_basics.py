from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict, total=False):
    topic: str
    draft: str
    needs_revision: bool


def write(state):
    return {"draft": "A retailer owes Rs 100 and pays Rs 40. Rs 60 remains."}


def check(state):
    return {"needs_revision": "fictional" not in state["draft"].lower()}


def revise(state):
    return {"draft": "Fictional example: " + state["draft"]}


builder = StateGraph(State)
builder.add_node("write", write)
builder.add_node("check", check)
builder.add_node("revise", revise)
builder.add_edge(START, "write")
builder.add_edge("write", "check")
builder.add_conditional_edges("check", lambda state: "revise" if state["needs_revision"] else "done",
                              {"revise": "revise", "done": END})
builder.add_edge("revise", "check")
graph = builder.compile()
print(graph.invoke({"topic": "Partial payments"}))
print("The checker routed the first draft to revise, then ended after the example was labelled.")
