# import os

# from google.adk.agents import Agent
# from dotenv import load_dotenv
# from .tools import get_employee,get_department,get_project_status,save_user_preference

# load_dotenv()

# root_agent = Agent(
#     name="my_first_agent",
#     model="gemini-3.6-flash",
#     instruction="""
#         You are an employee and project information assistant.

#         You have access to four tools:

#         1. get_employee
#         Use this when the user asks about a specific employee.

#         2. get_department
#         Use this when the user asks about a department.

#         3. get_project_status
#         Use this when the user asks about a project.

#         4. save_user_preference
#         Use this when the user explicitly asks you to remember
#         a preference or piece of information for the current conversation.

#         Use the appropriate tool when required.

#         Do not invent employee, department, or project information.
#         """,
#     tools = [get_employee,get_project_status,get_department,save_user_preference],
# )

#----------------------------------------------

# from dotenv import load_dotenv

# from .sequential_workflow import employee_workflow


# load_dotenv()

# root_agent = employee_workflow

#-------------------------------------------------

# from dotenv import load_dotenv

# from .parallel_workflow import parallel_workflow
# from .loop_workflow import project_review_loop


# load_dotenv()


# root_agent = parallel_workflow

#-------------------------------------------------
# from .workflow import employee_information_workflow

# root_agent = employee_information_workflow

#-------------------------------------------------

# from .multi_agent import root_agent

# root_agent = root_agent

#--------------------------------------------------

# from .parallel_multi_agent import parallel_multi_agent_workflow

# root_agent = parallel_multi_agent_workflow

#---------------------------------------------------

#from .mcp_agent import root_agent
#from .business_agent import root_agent
from .pipeline_monitor_agent import root_agent

root_agent = root_agent
