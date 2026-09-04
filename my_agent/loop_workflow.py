from google.adk.agents import Agent, LoopAgent
from .tools import get_project_status

from .config import MODEL_NAME


review_agent = Agent(
    name="project_review_agent",
    model = f"groq/{MODEL_NAME}",
    instruction="""
    You are a project review agent.

    Review the current status of the Customer360 project
    using the get_project_status tool.

    Determine whether the project is complete.

    If the project is 100% complete, indicate that the review
    is complete.

    Otherwise, indicate that another review is required.
    """,
    tools=[get_project_status],
)

project_review_loop = LoopAgent(
    name="project_review_loop",
    sub_agents=[
        review_agent,
    ],
    max_iterations=3,
)