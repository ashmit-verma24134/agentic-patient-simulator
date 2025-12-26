from agents.patient_agent import PatientAgent
from langgraph.graph import StateGraph
GraphState = dict
def patient_node(state: GraphState) -> GraphState:
    """
    Single LangGraph node.
    Reads user_message from state.
    """
    user_message = state.pop("last_user_message", "")
    agent = PatientAgent(state)
    reply = agent.respond(user_message)
    state["reply"] = reply
    return state

def build_patient_graph():
    graph = StateGraph(GraphState)
    graph.add_node("patient", patient_node)
    graph.set_entry_point("patient")
    graph.set_finish_point("patient")
    return graph.compile()
