"""
Database Models for the ETL Process.

This module defines the database models using SQLAlchemy for employees, customers, and products.

Modules:
    - sqlalchemy: For ORM and database schema definition.
    - pydantic: For data validation (not used in these models).
"""

from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

Base = declarative_base()

# Database Models
class EmployeeDB(Base):
    """
    Represents an Employee in the database.

    Attributes:
        employee_id (int): The unique identifier for the employee (auto-incremented).
        first_name (str): The first name of the employee.
        last_name (str): The last name of the employee.
        email (str): The unique email address of the employee.
        salary (int): The employee's salary.
    """
    __tablename__ = "employees"
    employee_id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    salary = Column(Integer)

class CustomerDB(Base):
    """
    Represents a Customer in the database.

    Attributes:
        customer_id (int): The unique identifier for the customer (auto-incremented).
        customer_name (str): The name of the customer.
        address (str): The address of the customer.
        city (str): The city where the customer resides.
        zip_code (str): The customer's postal code.
    """
    __tablename__ = "customers"
    customer_id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    customer_name = Column(String, index=True)
    address = Column(String)
    city = Column(String)
    zip_code = Column(String)

class ProductDB(Base):
    """
    Represents a Product in the database.

    Attributes:
        product_id (int): The unique identifier for the product (auto-incremented).
        product_name (str): The name of the product.
        price (float): The price of the product.
        description (str): A short description of the product.
        category (str): The category the product belongs to.
    """
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    product_name = Column(String, index=True)
    price = Column(Float)
    description = Column(String)
    category = Column(String)
