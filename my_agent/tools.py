from google.adk.tools.tool_context import ToolContext


def get_employee(
    employee_id: str,
    tool_context: ToolContext,
) -> dict:
    """Get employee information using an employee ID and save it to session state."""

    employees = {
        "101": {
            "name": "John",
            "department": "Data Engineering",
            "role": "Data Engineer",
        },
        "102": {
            "name": "Sarah",
            "department": "Analytics",
            "role": "Data Analyst",
        },
        "103": {
            "name": "David",
            "department": "Machine Learning",
            "role": "ML Engineer",
        },
    }

    employee = employees.get(employee_id)

    if employee is None:
        return {
            "error": f"No employee found with ID {employee_id}"
        }

    # Save employee information into the current session state
    tool_context.state["employee"] = employee

    return employee


def get_department(department_name: str) -> dict:
    """Get information about a department."""

    departments = {
        "Data Engineering": {
            "manager": "Robert",
            "location": "Chennai",
            "team_size": 25,
        },
        "Analytics": {
            "manager": "Priya",
            "location": "Bangalore",
            "team_size": 18,
        },
        "Machine Learning": {
            "manager": "Michael",
            "location": "Hyderabad",
            "team_size": 12,
        },
    }

    department = departments.get(department_name)

    if department is None:
        return {
            "error": f"No department found with name {department_name}"
        }

    return department


def get_project_status(project_name: str) -> dict:
    """Get the current status of a project."""

    projects = {
        "Customer360": {
            "status": "In Progress",
            "owner": "Data Engineering Team",
            "completion": "75%",
        },
        "MLPlatform": {
            "status": "Completed",
            "owner": "Machine Learning Team",
            "completion": "100%",
        },
        "AnalyticsDashboard": {
            "status": "On Hold",
            "owner": "Analytics Team",
            "completion": "40%",
        },
    }

    project = projects.get(project_name)

    if project is None:
        return {
            "error": f"No project found with name {project_name}"
        }

    return project


def save_user_preference(
    preference: str,
    value: str,
    tool_context: ToolContext,
) -> dict:
    """Save user preferences in the current session."""

    tool_context.state[preference] = value

    return {
        "status": "success",
        "message": f"saved {preference} as {value}",
    }


def save_employee_department(
    department_name: str,
    tool_context: ToolContext,
) -> dict:
    """Save the employee department into session state."""

    tool_context.state["employee_department"] = department_name

    return {
        "status": "success",
        "employee_department": department_name,
    }


def save_parallel_tasks(
    employee_task: str,
    project_task: str,
    tool_context: ToolContext,
) -> dict:
    """Save specialist tasks into the current session state."""

    tool_context.state["employee_task"] = employee_task
    tool_context.state["project_task"] = project_task

    return {
        "status": "success",
        "employee_task": employee_task,
        "project_task": project_task,
    }