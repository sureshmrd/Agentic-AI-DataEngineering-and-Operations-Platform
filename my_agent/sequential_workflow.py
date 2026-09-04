from google.adk.agents import Agent, SequentialAgent
from .tools import get_employee,get_department,save_employee_department
from .config import MODEL_NAME


employee_agent = Agent(
    name="employee_agent",
    model = f"groq/{MODEL_NAME}",
    instruction="""
        You are an employee lookup specialist.

        Retrieve employee information using the get_employee tool.

        After retrieving the employee information, store the
        employee's department in session state using the key:

        employee_department

        Return the employee's:
        - name
        - department
        - role
        """,
    tools = [get_employee,save_employee_department],
)

department_agent = Agent(
    name="department_agent",
    model = f"groq/{MODEL_NAME}",
    instruction="""
    You are a department information specialist.

    Read the employee_department value from the current
    session state.

    Use the get_department tool to retrieve information
    about that department.

    Return:
    - department
    - manager
    - location
    - team size
    """,
    tools = [get_department],
)

employee_workflow = SequentialAgent(
    name="employee_information_workflow",
    sub_agents=[
        employee_agent,
        department_agent,
    ],
)