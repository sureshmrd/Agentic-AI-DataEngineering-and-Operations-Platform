# from google.adk import Workflow

# def employee_lookup(node_input: str) -> str:
#     return f"Employee lookup completed for: {node_input}"


# def department_lookup(node_input: str) -> str:
#     return f"Department lookup completed using: {node_input}"


# employee_workflow = Workflow(
#     name="employee_information_workflow",
#     edges=[
#         ("START", employee_lookup, department_lookup),
#     ],
# )


from google.adk import Agent, Workflow

from .config import MODEL_NAME
from .tools import get_employee, get_department


employee_agent = Agent(
    name="employee_agent",
    model=f"groq/{MODEL_NAME}",
    instruction="""
    You are an employee information specialist.

    The user will provide an employee ID.

    Use the get_employee tool to retrieve the employee information.

    After retrieving the employee information, make sure the result
    is available in the workflow state under the key "employee".

    Provide a concise summary of the employee information.
    """,
    tools=[get_employee],
)


department_agent = Agent(
    name="department_agent",
    model=f"groq/{MODEL_NAME}",
    instruction="""
    You are a department information specialist.

    Look at the workflow state for the "employee" information.

    Identify the employee's department from that information.

    Then use the get_department tool to retrieve information
    about that department.

    Provide a concise department summary.
    """,
    tools=[get_department],
)


employee_information_workflow = Workflow(
    name="employee_information_workflow",
    edges=[
        ("START", employee_agent, department_agent),
    ],
)