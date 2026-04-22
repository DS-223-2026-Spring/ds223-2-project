"""
Streamlit Application for Employee Management.

This module provides a user interface for interacting with a FastAPI backend to perform CRUD
operations on employee records, including retrieving, creating, updating, and deleting.

Modules:
    - streamlit: For creating the web application interface.
    - requests: For making HTTP requests to the FastAPI backend.
    - os: For accessing environment variables (used for the API URL).
"""

import streamlit as st
import requests
import os

# Get the FastAPI URL from environment variables
api_url = os.getenv("API_URL", "http://localhost:8000")

# Set up the Streamlit app title
st.title("Employee Management System")

# -----------------------------------------------------
# Utility Functions (API Interactions)
# -----------------------------------------------------

def get_employee_by_id(employee_id: int) -> dict:
    """
    Fetch employee details by their ID.

    **Parameters:**
    
    - `employee_id (int):` The ID of the employee to retrieve.

    **Returns:**
        - `dict:` The employee's details if found, or `None` with an error message.
    """
    response = requests.get(f"{api_url}/employees/{employee_id}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Employee not found.")
        return None

def create_employee(first_name: str, last_name: str, email: str, salary: int) -> dict:
    """
    Create a new employee record.

    **Parameters:**
    
    - `first_name (str):` Employee's first name.
    - `last_name (str):` Employee's last name.
    - `email (str):` Employee's email address.
    - `salary (int):` Employee's salary.

    **Returns:**
        - `dict:` The created employee's details or an error message if the operation fails.
    """
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "salary": salary
    }
    response = requests.post(f"{api_url}/employees/", json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to create employee.")
        return None

def update_salary(employee_id: int, new_salary: int) -> dict:
    """
    Update an existing employee's salary by sending the full employee payload.

    **Parameters:**
    
    - `employee_id (int):` The ID of the employee whose salary will be updated.
    - `new_salary (int):` The new salary amount.

    **Returns:**
        - `dict:` The updated employee details if successful, or an error message if the operation fails.
    """
    employee = get_employee_by_id(employee_id)
    if not employee:
        st.error("Employee not found, cannot update salary.")
        return None
    
    payload = {
        "first_name": employee["first_name"],
        "last_name": employee["last_name"],
        "email": employee["email"],
        "salary": new_salary
    }
    response = requests.put(f"{api_url}/employees/{employee_id}", json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to update salary.")
        return None

def delete_employee(employee_id: int) -> dict:
    """
    Delete an employee record by ID.

    **Parameters:**
    
    - `employee_id (int):` The ID of the employee to delete.

    **Returns:**
        - `dict:` A success message if the deletion is successful, or an error message if the operation fails.
    """
    response = requests.delete(f"{api_url}/employees/{employee_id}")
    if response.status_code == 200:
        return {"message": "Employee deleted successfully."}
    else:
        st.error("Failed to delete employee.")
        return None

# -----------------------------------------------------
# UI Components
# -----------------------------------------------------

# Section: Get an Employee by ID
st.subheader("Get Employee by ID")
employee_id_search = st.number_input("Employee ID for Search", min_value=1, step=1)
if st.button("Get Employee"):
    employee = get_employee_by_id(employee_id_search)
    if employee:
        st.write("Employee Details:")
        st.json(employee)

# Section: Add New Employee
st.subheader("Add New Employee")
with st.form("employee_form"):
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email")
    salary = st.number_input("Salary", min_value=0, step=1000)
    submit_button = st.form_submit_button("Add Employee")
    if submit_button:
        new_employee = create_employee(first_name, last_name, email, salary)
        if new_employee:
            st.success("Employee added successfully!")
            st.json(new_employee)

# Section: Update Employee Salary
st.subheader("Update Employee Salary")
employee_id_update = st.number_input("Employee ID to Update Salary", min_value=1, step=1)
new_salary = st.number_input("New Salary", min_value=0, step=1000)
if st.button("Update Salary"):
    updated_employee = update_salary(employee_id_update, new_salary)
    if updated_employee:
        st.success("Salary updated successfully!")
        st.json(updated_employee)

# Section: Delete Employee
st.subheader("Delete Employee")
employee_id_delete = st.number_input("Employee ID to Delete", min_value=1, step=1)
if st.button("Delete Employee"):
    result = delete_employee(employee_id_delete)
    if result:
        st.success(result["message"])
