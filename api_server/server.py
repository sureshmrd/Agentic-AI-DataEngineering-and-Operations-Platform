from fastapi import FastAPI, HTTPException
from api_server.database import execute_query
from api_server.models import EmployeeResponse, DepartmentResponse


app = FastAPI(title="Employee API")


@app.get(
    "/employees/{employee_id}",
    response_model=EmployeeResponse
)
def get_employee(employee_id: int):

    print(f"REST API called for employee: {employee_id}")

    query = """
        SELECT
            e.employee_id,
            e.name,
            e.email,
            e.role,
            e.salary,
            d.department_name AS department
        FROM employees e
        JOIN departments d
            ON e.department_id = d.department_id
        WHERE e.employee_id = %s
    """

    employee = execute_query(
        query,
        (employee_id,),
        fetch_one=True
    )

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail=f"No employee found with ID {employee_id}"
        )

    return employee

    print(f"REST API called for employee: {employee_id}")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            e.employee_id,
            e.name,
            e.email,
            e.role,
            e.salary,
            d.department_name AS department
        FROM employees e
        JOIN departments d
            ON e.department_id = d.department_id
        WHERE e.employee_id = %s
    """

    cursor.execute(query, (employee_id,))
    employee = cursor.fetchone()

    cursor.close()
    connection.close()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail=f"No employee found with ID {employee_id}"
        )

    return employee


@app.get(
    "/departments/{department_name}",
    response_model=DepartmentResponse
)
def get_department(department_name: str):   

    print(
        f"REST API called for department: {department_name}"
    )

    query = """
        SELECT
            department_id,
            department_name,
            manager,
            location,
            team_size,
            description
        FROM departments
        WHERE department_name = %s
    """

    department = execute_query(
        query,
        (department_name,),
        fetch_one=True
    )

    if department is None:
        raise HTTPException(
            status_code=404,
            detail=f"No department found with name {department_name}"
        )

    return department

@app.get(
    "/employees/search/{name}",
    response_model=list[EmployeeResponse]
)
def search_employee_by_name(name: str):

    print(f"REST API called to search employee by name: {name}")

    query = """
        SELECT
            e.employee_id,
            e.name,
            e.email,
            e.role,
            e.salary,
            d.department_name AS department
        FROM employees e
        JOIN departments d
            ON e.department_id = d.department_id
        WHERE e.name LIKE %s
        ORDER BY e.employee_id
    """

    employees = execute_query(
        query,
        (f"%{name}%",),
        fetch_all=True
    )

    if not employees:
        raise HTTPException(
            status_code=404,
            detail=f"No employee found with name {name}"
        )

    return employees
    print(f"REST API called to search employee by name: {name}")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            e.employee_id,
            e.name,
            e.email,
            e.role,
            e.salary,
            d.department_name AS department
        FROM employees e
        JOIN departments d
            ON e.department_id = d.department_id
        WHERE e.name LIKE %s
    """

    cursor.execute(query, (f"%{name}%",))
    employees = cursor.fetchall()

    cursor.close()
    connection.close()

    if not employees:
        raise HTTPException(
            status_code=404,
            detail=f"No employee found with name {name}"
        )

    return employees


@app.get(
    "/employees",
    response_model=list[EmployeeResponse]
)
def get_all_employees():

    print("REST API called to get all employees")

    query = """
        SELECT
            e.employee_id,
            e.name,
            e.email,
            e.role,
            e.salary,
            d.department_name AS department
        FROM employees e
        JOIN departments d
            ON e.department_id = d.department_id
        ORDER BY e.employee_id
    """

    return execute_query(
        query,
        fetch_all=True
    )


@app.get(
    "/departments",
    response_model=list[DepartmentResponse]
)
def get_all_departments():

    print("REST API called to get all departments")

    query = """
        SELECT
            department_id,
            department_name,
            manager,
            location,
            team_size,
            description
        FROM departments
        ORDER BY department_id
    """

    return execute_query(
        query,
        fetch_all=True
    )


@app.get(
    "/departments/{department_name}/employees",
    response_model=list[EmployeeResponse]
)
def get_department_employees(department_name: str):

    print(
        "REST API called to get employees in department: "
        f"{department_name}"
    )

    query = """
        SELECT
            e.employee_id,
            e.name,
            e.email,
            e.role,
            e.salary,
            d.department_name AS department
        FROM employees e
        JOIN departments d
            ON e.department_id = d.department_id
        WHERE d.department_name = %s
        ORDER BY e.employee_id
    """

    employees = execute_query(
        query,
        (department_name,),
        fetch_all=True
    )

    if not employees:
        raise HTTPException(
            status_code=404,
            detail=f"No employees found in department {department_name}"
        )

    return employees    