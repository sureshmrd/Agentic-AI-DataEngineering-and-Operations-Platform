from pydantic import BaseModel
from typing import List


class EmployeeResponse(BaseModel):
    employee_id: int
    name: str
    email: str
    role: str
    salary: float
    department: str


class DepartmentResponse(BaseModel):
    department_id: int
    department_name: str
    manager: str | None
    location: str | None
    team_size: int | None
    description: str | None