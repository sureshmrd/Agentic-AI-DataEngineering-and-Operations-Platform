from google.adk import Agent

from .config import MODEL_NAME
from .tools import get_employee, get_project_status


employee_agent = Agent(
    name="employee_agent",
    model=f"groq/{MODEL_NAME}",
    instruction="""
    You are an employee information specialist.

    Your job is to answer questions about employees.

    When the user asks about an employee, use the get_employee tool.
    Provide a concise and accurate answer based on the tool result.
    """,
    tools=[get_employee],
)


project_agent = Agent(
    name="project_agent",
    model=f"groq/{MODEL_NAME}",
    instruction="""
    You are a project information specialist.

    Your job is to answer questions about projects.

    When the user asks about a project, use the get_project_status tool.
    Provide a concise and accurate answer based on the tool result.
    """,
    tools=[get_project_status],
)


root_agent = Agent(
    name="company_assistant",
    model=f"groq/{MODEL_NAME}",
    instruction="""
    You are the main company assistant.

    You coordinate specialized agents.

    Delegate employee-related questions to employee_agent.
    Delegate project-related questions to project_agent.

    Do not answer these specialized questions yourself when the
    appropriate specialist agent can handle them.
    """,
    sub_agents=[
        employee_agent,
        project_agent,
    ],
)