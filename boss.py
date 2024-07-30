from datetime import datetime
import csv
import os
from dateutil import parser


class WorkSession:
    def __init__(self, employee_id, employee_name, date_login, date_logout=None):
        self.employee_id = employee_id
        self.employee_name = employee_name
        self.date_login = date_login
        self.date_logout = date_logout

    def work_session_time(self):
        if self.date_logout:
            duration = self.date_logout - self.date_login
            hours_worked = duration.total_seconds() / 3600
            return hours_worked
        return 0


class Sales:
    def __init__(self, employee_id, product_name, total_price, sales_date):
        self.employee_id = employee_id
        self.product_name = product_name
        self.total_price = total_price
        self.sales_date = sales_date


class Employees:
    def __init__(self, employee_id, username, password, is_admin=False):
        self.employee_id = employee_id
        self.username = username
        self.password = password
        self.is_admin = is_admin


class CsvHelper:
    def __init__(self, file_path, data_class=None, dtypes=None, newline="", encoding="utf-8"):
        self.file_path = file_path
        self.data_class = data_class
        self.dtypes = dtypes
        self.newline = newline
        self.encoding = encoding

    def row_to_obj(self, row):
        cls = globals()[self.data_class]
        if cls == WorkSession:
            row['date_login'] = parser.parse(row['date_login'])
            row['date_logout'] = parser.parse(row['date_logout']) if row['date_logout'] else None
        elif cls == Sales:
            row['sales_date'] = parser.parse(row['sales_date'])
        return cls(**row)

    def row_apply_datatypes(self, row):
        for col_index, col_type in self.dtypes.items():
            col_value = row[col_index]

            if col_type == "int":
                row[col_index] = int(col_value)
            elif col_type == "float":
                row[col_index] = float(col_value)
            elif col_type == "bool":
                row[col_index] = col_value.lower() in ("true", "1")
            elif col_type == "str":
                row[col_index] = str(col_value)

        return row

    def read(self):
        with open(self.file_path, "r", newline=self.newline, encoding=self.encoding) as file:
            rows = list(csv.DictReader(file))
            for index, row in enumerate(rows):
                if self.dtypes:
                    rows[index] = self.row_apply_datatypes(row)
                if self.data_class:
                    rows[index] = self.row_to_obj(row)

        return rows

    def save(self, data):
        if len(data) == 0:
            keys = []
        elif isinstance(data[0], dict):
            keys = data[0].keys()
        else:
            keys = data[0].__dict__.keys()

        with open(self.file_path, "w", newline=self.newline, encoding=self.encoding) as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()

            for row in data:
                if isinstance(row, dict):
                    dict_writer.writerow(row)
                else:
                    dict_writer.writerow(row.__dict__)

    def delete(self):
        os.remove(self.file_path)


class Admin:
    def __init__(self, sales_file, employees_file, work_sessions_file):
        self.sales_file = sales_file
        self.employees_file = employees_file
        self.work_sessions_file = work_sessions_file

    def sort_employees_by_sales_and_work_hours(self, by_sales=True, most=True):
        sales_data = self.sales_file.read()
        employees_data = self.employees_file.read()

        if by_sales:
            sales_summary = {}
            for sale in sales_data:
                if sale.employee_id in sales_summary:
                    sales_summary[sale.employee_id] += sale.total_price
                else:
                    sales_summary[sale.employee_id] = sale.total_price

            target_employee_id = max(sales_summary, key=sales_summary.get) if most else min(sales_summary, key=sales_summary.get)
            target_employee_sales = sales_summary[target_employee_id]

            print(f"{'Best' if most else 'Worst'} Sales Employee: {next(e.username for e in employees_data if e.employee_id == target_employee_id)}")
            print(f"Total Sales Amount: {target_employee_sales:.2f}")

            print("Sales Details:")
            for sale in sales_data:
                if sale.employee_id == target_employee_id:
                    print(f" - Product: {sale.product_name}, Price: {sale.total_price:.2f}, Date: {sale.sales_date}")

        else:
            hours_summary = {}
            for session in self.work_sessions_file.read():
                if session.employee_id in hours_summary:
                    hours_summary[session.employee_id] += session.work_session_time()
                else:
                    hours_summary[session.employee_id] = session.work_session_time()

            target_employee_id = max(hours_summary, key=hours_summary.get) if most else min(hours_summary, key=hours_summary.get)
            target_employee_hours = hours_summary[target_employee_id]

            print(f"Employee with {'Most' if most else 'Least'} Hours: {next(e.username for e in employees_data if e.employee_id == target_employee_id)}")
            print(f"Total Hours Worked: {target_employee_hours:.2f}")

    def get_employee_hours(self, most=True):
        self.sort_employees_by_sales_and_work_hours(by_sales=False, most=most)

    def get_best_sales_employee(self):
        self.sort_employees_by_sales_and_work_hours(by_sales=True, most=True)

    def get_worst_sales_employee(self):
        self.sort_employees_by_sales_and_work_hours(by_sales=True, most=False)


def authenticate(username, password, employees):
    for employee in employees:
        if employee.username == username and employee.password == password:
            return employee
    return None


def register_employee(employees):
    employee_id = len(employees) + 1
    username = input("Enter a username: ")
    password = input("Enter a password: ")

    new_employee = Employees(employee_id, username, password)
    employees.append(new_employee)

    employees_file = CsvHelper(r"C:\Users\ulatiju0001\OneDrive - anicura.onmicrosoft.com\Bureaublad\employees.csv",
                               data_class="Employees", dtypes={"employee_id": "int", "is_admin": "bool"})
    employees_file.save(employees)
    print(f"Employee {username} registered successfully.")


def main():
    employees_file = CsvHelper(r"C:\Users\ulatiju0001\OneDrive - anicura.onmicrosoft.com\Bureaublad\employees.csv",
                               data_class="Employees", dtypes={"employee_id": "int", "is_admin": "bool"})
    work_sessions_file = CsvHelper(
        r"C:\Users\ulatiju0001\OneDrive - anicura.onmicrosoft.com\Bureaublad\worktime_log.csv",
        data_class="WorkSession", dtypes={"employee_id": "int"})
    sales_file = CsvHelper(r"C:\Users\ulatiju0001\OneDrive - anicura.onmicrosoft.com\Bureaublad\sales.csv",
                           data_class="Sales", dtypes={"employee_id": "int", "total_price": "float"})

    print("Welcome! Please choose an option:")
    print("1. Register a new employee")
    print("2. Log in as an employee")
    print("3. Log in as an admin")

    choice = input("Enter your choice (1, 2, or 3): ")

    if choice == "1":
        employees = employees_file.read()
        register_employee(employees)
    elif choice == "2":
        employees = employees_file.read()
        username = input("Username: ")
        password = input("Password: ")
        user = authenticate(username, password, employees)
        if user:
            login_time = datetime.now()
            print("Logged in successfully.")

            while True:
                product_name = input("Enter product name (or 'logout' to log out): ")
                if product_name.lower() == 'logout':
                    break

                total_price = float(input("Enter total price: "))
                sales_date = datetime.now()

                new_sale = Sales(employee_id=user.employee_id, product_name=product_name, total_price=total_price,
                                 sales_date=sales_date)
                sales = sales_file.read()
                sales.append(new_sale)
                sales_file.save(sales)

                print(f"Sale recorded: {product_name} for {total_price:.2f}")

            logout_time = datetime.now()
            new_session = WorkSession(employee_id=user.employee_id, employee_name=user.username, date_login=login_time,
                                     date_logout=logout_time)
            work_sessions = work_sessions_file.read()
            work_sessions.append(new_session)
            work_sessions_file.save(work_sessions)

            print("Work session recorded.")
        else:
            print("Invalid credentials.")
    elif choice == "3":
        username = input("Admin Username: ")
        password = input("Admin Password: ")

        if username == "Tomas" and password == "slaptazodis":
            admin = Admin(sales_file=sales_file, employees_file=employees_file, work_sessions_file=work_sessions_file)
            print("Welcome, Admin!")
            while True:
                print("Choose an option:")
                print("1. Best sales employee")
                print("2. Worst sales employee")
                print("3. Employee with most hours")
                print("4. Employee with least hours")
                print("5. Log out")

                admin_choice = input("Enter choice (1, 2, 3, 4, or 5): ")

                if admin_choice == "1":
                    admin.get_best_sales_employee()
                elif admin_choice == "2":
                    admin.get_worst_sales_employee()
                elif admin_choice == "3":
                    admin.get_employee_hours(most=True)
                elif admin_choice == "4":
                    admin.get_employee_hours(most=False)
                elif admin_choice == "5":
                    break
                else:
                    print("Invalid choice.")
        else:
            print("Invalid credentials or not an admin.")
    else:
        print("Invalid choice. Please restart the program.")


if __name__ == "__main__":
    main()
