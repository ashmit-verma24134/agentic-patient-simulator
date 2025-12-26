from langgraph.graph import StateGraph
from graph.state import PatientState
from graph.nodes import classify_node, respond_node, diagnosis_gate_node

def build_patient_graph():
    graph = StateGraph(PatientState)
    graph.add_node("classify", classify_node)
    graph.add_node("respond", respond_node)
    graph.add_node("gate", diagnosis_gate_node)
    graph.add_edge("classify", "respond")
    graph.add_edge("respond", "gate")
    graph.set_entry_point("classify")
    graph.set_finish_point("gate")

    return graph.compile()
