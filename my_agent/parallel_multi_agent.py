from google.adk import Agent, Workflow
from google.adk.workflow import JoinNode

from .config import MODEL_NAME
from .tools import get_employee, get_project_status, save_parallel_tasks


def employee_task(node_input: str) -> str:
    """Extract the employee-related task from the user request."""
    return "Find information about employee 101."


def project_task(node_input: str) -> str:
    """Extract the project-related task from the user request."""
    return "Find the status of the Customer360 project."


employee_agent = Agent(
    name="employee_agent",
    model=f"groq/{MODEL_NAME}",
    instruction="""
    You are the Employee Information Specialist.

    Read the employee task from session state:

    state["employee_task"]

    Use the get_employee tool with the employee ID
    contained in that task.

    Return only the employee-related information.
    """,
    tools=[get_employee],
)


project_agent = Agent(
    name="project_agent",
    model=f"groq/{MODEL_NAME}",
    instruction="""
    You are the Project Information Specialist.

    Read the project task from session state:

    state["project_task"]

    Use the get_project_status tool with the project name
    contained in that task.

    Return only the project-related information.
    """,
    tools=[get_project_status],
)


synthesis_agent = Agent(
    name="synthesis_agent",
    model=f"groq/{MODEL_NAME}",
    instruction="""
    You are the final response synthesizer.

    Combine the results from the Employee Agent and Project Agent.

    Produce one clear answer containing:
    - Employee information
    - Project status

    Do not invent information.
    Only use information provided by the specialist agents.
    """,
)


coordinator_agent = Agent(
    name="coordinator_agent",
    model=f"groq/{MODEL_NAME}",
    instruction="""
    You are the Coordinator Agent.

    Analyze the user's request and identify the employee-related
    task and project-related task.

    Extract the relevant employee ID and project name.

    Then call save_parallel_tasks with:

    - employee_task: a clear task containing the employee ID
    - project_task: a clear task containing the project name

    Example:

    User:
    "Give me information about employee 102 and the status of MLPlatform."

    employee_task:
    "Find information about employee 102."

    project_task:
    "Find the status of MLPlatform."

    Do not answer the user's question yourself.
    Your job is only to prepare the tasks for the specialist agents.
    """,
    tools=[save_parallel_tasks],
)


join_node = JoinNode(name="specialist_results")


parallel_multi_agent_workflow = Workflow(
    name="parallel_multi_agent_workflow",
    edges=[
        ("START", coordinator_agent),

        (coordinator_agent, (employee_agent, project_agent)),

        (employee_agent, join_node),
        (project_agent, join_node),

        (join_node, synthesis_agent),
    ],
)