from __future__ import print_function
import mysql.connector
import mysql.connector
import config
import pandas
from datetime import date, datetime, timedelta
from mysql.connector import errorcode

DATA_PATH = "./employee_data.xlsx"


def create_database(db_cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(config.DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))

    try:
        cursor.execute("USE {}".format(config.DB_NAME))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(config.DB_NAME))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print("Database {} created successfully.".format(config.DB_NAME))
            cnx.database = config.DB_NAME
        else:
            print(err)
            exit(1)


def create_tables(db_cursor):
    for table_name in config.TABLES:
        table_description = config.TABLES[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")


def create_employees(emp_cursor, emp_data):
    tomorrow = datetime.now().date() + timedelta(days=1)

    add_employee = ("INSERT INTO employees "
                    "(first_name, last_name, hire_date, title, birth_date) "
                    "VALUES (%s, %s, %s, %s, %s)")
    add_salary = ("INSERT INTO salaries "
                  "(emp_no, salary, from_date, to_date) "
                  "VALUES (%s, %s, %s, %s)")

    employees_data = [(
        emp['first_name'],
        emp['last_name'],
        emp['hire_date'],
        emp['title'],
        emp['birth_date']
    ) for emp in emp_data]

    # Insert new employee
    cursor.executemany(add_employee, employees_data)
    emp_no = cursor.lastrowid

    # Insert salary information
    data_salary = {
        'emp_no': emp_no,
        'salary': 50000,
        'from_date': tomorrow,
        'to_date': date(9999, 1, 1),
    }
    cursor.execute(add_salary, data_salary)

    # Make sure data is committed to the database
    cnx.commit()


def get_employee_data_from_xlsx(file_path):
    raw_data = pandas.read_excel(file_path, engine='openpyxl')

    formatted_data = []
    for row in raw_data.itertuples():
        formatted_data.append({
            "first_name": row.first_name,
            "last_name": row.last_name,
            "hire_date": row.hire_date,
            "title": row.title,
            "birth_date": row.birth_date
        })

    return formatted_data


if __name__ == '__main__':

    # Create Python connection to MySQL Database
    cnx = mysql.connector.connect(**config.CONFIG)
    cursor = cnx.cursor()

    # Create / initialize databases and tables
    create_database(cursor)
    create_tables(cursor)

    # Insert Employee data into the Employee table
    employee_data = get_employee_data_from_xlsx(DATA_PATH)
    create_employees(cursor, employee_data)

    cursor.close()
    cnx.close()
