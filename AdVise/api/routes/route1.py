"""Employee CRUD (primary API group)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import EmployeeDB
from schema import Employee, EmployeeCreate

router = APIRouter()


@router.get("/{employee_id}", response_model=Employee)
async def get_employee(employee_id: int, db: Session = Depends(get_db)):
    """
    Retrieve an employee by their unique ID.
    """
    employee = (
        db.query(EmployeeDB).filter(EmployeeDB.employee_id == employee_id).first()
    )
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.post("/", response_model=Employee)
async def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """
    Create a new employee.
    """
    db_employee = EmployeeDB(
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        salary=employee.salary,
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return Employee(
        employee_id=db_employee.employee_id,
        first_name=db_employee.first_name,
        last_name=db_employee.last_name,
        email=db_employee.email,
        salary=db_employee.salary,
    )


@router.put("/{employee_id}", response_model=Employee)
async def update_employee(
    employee_id: int, updated_employee: EmployeeCreate, db: Session = Depends(get_db)
):
    """
    Update an existing employee.
    """
    employee = (
        db.query(EmployeeDB).filter(EmployeeDB.employee_id == employee_id).first()
    )
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    for key, value in updated_employee.dict().items():
        setattr(employee, key, value)
    db.commit()
    db.refresh(employee)
    return employee


@router.delete("/{employee_id}")
async def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """
    Delete an employee by ID.
    """
    employee = (
        db.query(EmployeeDB).filter(EmployeeDB.employee_id == employee_id).first()
    )
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(employee)
    db.commit()
    return {"message": "Employee deleted successfully"}
