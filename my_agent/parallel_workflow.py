from google.adk.agents import Agent, ParallelAgent
from .config import MODEL_NAME

from .tools import (
    get_department,
    get_project_status,
)


department_agent = Agent(
    name="parallel_department_agent",
    model = f"groq/{MODEL_NAME}",
    instruction="""
    Retrieve information about the Data Engineering
    department using the get_department tool.
    """,
    tools=[get_department],
)


project_agent = Agent(
    name="parallel_project_agent",
    model = f"groq/{MODEL_NAME}",
    instruction="""
    Retrieve the current status of the Customer360 project
    using the get_project_status tool.
    """,
    tools=[get_project_status],
)


parallel_workflow = ParallelAgent(
    name="parallel_information_workflow",
    sub_agents=[
        department_agent,
        project_agent,
    ],
)