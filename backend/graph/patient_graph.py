from agents.patient_agent import PatientAgent  #Patientagent decides replies for normal ques
from langgraph.graph import StateGraph,END
from langgraph.checkpoint.memory import MemorySaver  #Memory for graph
from tools.lab_report_tool import generate_lab_report  #Tool used

GraphState =dict
#Patient node
def patient_node(state:GraphState)->GraphState:
    user_message = state.pop("last_user_message", "")
    agent= PatientAgent(state)  #PatientAgent directly modifies state

    # LAB REPORT RESPONSE
    if "lab_report" in state:
        report = state.pop("lab_report")

        #Pure factual output
        state["reply"] =(
            f"My CRP is {report['CRP']}, "
            f"my stool test is {report['Stool Test']}, "
            f"and my photophobia test is {report['Photophobia Test']}."
        )

        # END GRAPH HERE
        state["_end"] = True
        return state

    # NORMAL PATIENT FLOW
    reply= agent.respond(user_message)
    state["reply"]= reply
    return state


#LAB REPORT TOOL NODE

def lab_report_node(state: GraphState) -> GraphState:
    state["lab_report"] = generate_lab_report(state)
    return state


#ROUTER

def route_from_patient(state: GraphState):

    if state.get("_end"):          #Avoids infinite loop of show lab report by adding _end in state
        return END

    if state.get("next_action") == "show_lab_report":
        return "lab_report"

    return END


# GRAPH BUILDER

def build_patient_graph():
    graph = StateGraph(GraphState)

    graph.add_node("patient", patient_node)
    graph.add_node("lab_report", lab_report_node)

    graph.set_entry_point("patient")
    graph.add_conditional_edges(
        "patient",
        route_from_patient,
    )
    # Tool -> patient exactly once
    graph.add_edge("lab_report", "patient")

    memory = MemorySaver()           #remebers state so that when graph grows tool re-entry risk can be avoided
    return graph.compile(checkpointer=memory)
