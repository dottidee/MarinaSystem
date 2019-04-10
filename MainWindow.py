import tkinter as tk
import datetime
from tkinter import messagebox
import mysql.connector
from mysql.connector import errorcode
from tabulate import tabulate


#
# FingerLakesSystem Class
# Acts as system's Main Window, contains a menu frame and a main frame
# Menu Frame sets main frame to either Customer, Slips, Service, or Employee Page
# Methods: switch_main_frame, activate_menu, disable_menu, set_login_time
#
class FingerLakesSystem(tk.Tk):
    database = None
    menu_frame = None
    main_frame = None
    privilege = None  # 1=ADMIN, 2=Regular
    login_time = ""
    user = ""

    def __init__(self):
        tk.Tk.__init__(self)
        self.winfo_toplevel().title("Finger Lakes Marinas System")
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.minsize(width=682, height=666)
        # add menu bar to top
        self.menu_frame = MenuFrame(self)
        self.menu_frame.pack()
        # connect to database
        self.connect_database()
        # load login page
        self.switch_main_frame(LoginPage)
        self.disable_menu()

    def connect_database(self):
        # Connect to remote database
        try:
            self.database = mysql.connector.connect(
                host="remotemysql.com",
                user="3rybg59bIE",
                password="Rb8WxAwcfD",
                database="3rybg59bIE"
            )
        # Catch all errors
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                messagebox.showerror("Database Error", "Invalid user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                messagebox.showerror("Database Error", "Database does not exist")
            else:
                messagebox.showerror("Database Error", err)
            self.destroy()

    def switch_main_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self.main_frame is not None:
            self.main_frame.destroy()
        self.main_frame = new_frame
        self.main_frame.pack()
        self.activate_menu()

    def activate_menu(self):
        self.menu_frame.activate()

    def disable_menu(self):
        self.menu_frame.disable()

    def set_login_time(self, time):
        self.login_time = time


#
# MenuFrame: Frame containing 4 buttons to allow for switching between Pages
# Methods: activate, disable
#
class MenuFrame(tk.Frame):
    slip_button = None
    service_button = None
    customer_button = None
    employee_button = None

    def __init__(self, master):
        x_pad = 70
        y_pad = 20

        tk.Frame.__init__(self, master)
        self.slip_button = tk.Button(self, text="Slip Rentals", padx=x_pad, pady=y_pad,
                                     command=lambda: master.switch_main_frame(SlipPage))
        self.service_button = tk.Button(self, text="Services", padx=x_pad, pady=y_pad,
                                        command=lambda: master.switch_main_frame(ServicePage))
        self.customer_button = tk.Button(self, text="Customer", padx=x_pad, pady=y_pad,
                                         command=lambda: master.switch_main_frame(CustomerPage))
        self.employee_button = tk.Button(self, text="Employee", padx=x_pad, pady=y_pad,
                                         command=lambda: master.switch_main_frame(EmployeePage))

        self.slip_button.grid(row=0, column=1)
        self.service_button.grid(row=0, column=2)
        self.customer_button.grid(row=0, column=3)
        self.employee_button.grid(row=0, column=4)

        self.activate()

    def activate(self):
        self.disable()
        if not isinstance(self.master.main_frame, SlipPage):
            self.slip_button.configure(state="normal")
        if not isinstance(self.master.main_frame, ServicePage):
            self.service_button.configure(state="normal")
        if not isinstance(self.master.main_frame, CustomerPage):
            self.customer_button.configure(state="normal")
        if not isinstance(self.master.main_frame, EmployeePage):
            self.employee_button.configure(state="normal")

    def disable(self):
        self.slip_button.configure(state="disabled")
        self.service_button.configure(state="disabled")
        self.customer_button.configure(state="disabled")
        self.employee_button.configure(state="disabled")


#
# ServicePage Class
#
class ServicePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="This is the service page").pack(side="top", fill="x", pady=10)


#
# SlipPage Class
#
class SlipPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="This is slip page").pack(side="top", fill="x", pady=10)


#
# CostomerPage Class
#
class CustomerPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="This is customer page").pack(side="top", fill="x", pady=10)


#
# LoginPage Class
#
class LoginPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        master.disable_menu()
        tk.Label(self, text=" " * 20 + "\n\n").grid(row=0, column=0)
        tk.Label(self, text="\n*** Must be logged in to use the system ***\n", fg="black").grid(row=1, column=1,
                                                                                                columnspan=3, padx=10,
                                                                                                sticky='nsew')
        tk.Label(self, text="Employee ID:").grid(row=2, column=1, padx=10, sticky='nsw')
        self.entry = tk.Entry(self)
        self.entry.grid(row=2, column=2, pady=2, sticky='nsw')
        tk.Button(self, text="Login", padx=4, pady=4, command=lambda: self.login(master, self.entry.get())).grid(row=2,
                                                                                                                 column=3)

    def login(self, master, entry):
        # search employee table for id that matches entry
        sql = "SELECT * FROM employee WHERE employee_id = %s"
        usr_entry = (entry,)
        cursor = master.database.cursor()
        cursor.execute(sql, usr_entry)
        result = cursor.fetchall()
        # check if user entry is a valid ID from employee table
        if result.__len__() != 0:
            # valid user id: set user_id
            master.user_id = entry
            # Set user
            master.user = ""
            if isinstance(result[0][2], str):  # check if user has a last name
                master.user += result[0][2] + ", "
            if isinstance(result[0][1], str):  # check if user has a first name
                master.user += result[0][1]
            # Set privilege
            if result[0][4] == 1:
                FingerLakesSystem.privilege = 1
            else:
                FingerLakesSystem.privilege = 2
            now = datetime.datetime.now()
            master.set_login_time(now.strftime("%Y-%m-%d %H:%M"))
            master.switch_main_frame(EmployeePage)
            master.activate_menu()
        else:
            # invalid user id: show error and return to login page
            messagebox.showerror("Login Error", "Invalid User ID\nPlease try again")
            master.switch_main_frame(LoginPage)
            master.disable_menu()
        cursor.close()


#
# AdminPanel Class
#
class AdminPanel(tk.Frame):
    f_name = None
    l_name = None
    remove_id = None

    def __init__(self, master, db):
        tk.Frame.__init__(self, master)
        self.configure(bg=master.admin_bg_color)
        tk.Label(self, text="\nADMINISTRATOR TOOLS\n\n", fg="white", bg=master.admin_bg_color).grid(row=0, column=1,
                                                                                                    columnspan=10)

        # Spacers
        tk.Label(self, text="   ", bg=master.admin_bg_color).grid(row=0, column=25)
        tk.Label(self, text="   " * 8, bg=master.admin_bg_color).grid(row=1, column=3)
        tk.Label(self, text="\n    ", bg=master.admin_bg_color).grid(row=50, column=0)

        # Add Employee Section
        tk.Label(self, text="{:^60s}".format(" Add Employee "), fg="black", bg="white", borderwidth=2,
                 relief="sunken").grid(row=1, column=1, columnspan=2, sticky="n")
        is_admin = tk.IntVar()
        # Administrator
        tk.Label(self, text="\nAdmin:", fg="white", bg=master.admin_bg_color).grid(row=2, column=1, sticky="se")
        admin_check = tk.Checkbutton(self, text="", variable=is_admin, onvalue=1, offvalue=2, fg="white",
                                     bg=master.admin_bg_color)
        admin_check.grid(row=2, column=2, sticky="sw")
        # first name
        tk.Label(self, text="First Name:", fg="white", bg=master.admin_bg_color).grid(row=3, column=1, sticky="se")
        self.f_name = tk.Entry(self)
        self.f_name.grid(row=3, column=2, pady=5, sticky="se")
        # last name
        tk.Label(self, text="Last Name:", fg="white", bg=master.admin_bg_color).grid(row=4, column=1, sticky="se")
        self.l_name = tk.Entry(self)
        self.l_name.grid(row=4, column=2, pady=5, sticky="se")
        # add button
        tk.Button(self, text="Add", padx=80,
                  command=lambda: self.add_employee(db, self.f_name.get(), self.l_name.get(), is_admin.get())).grid(
            row=5,
            column=2, pady=5, sticky="se")

        # Remove Employee Section
        tk.Label(self, text="{:^70s}".format(" Remove Employee "), fg="black", bg="white",
                 borderwidth=2,
                 relief="sunken").grid(row=1,
                                       column=4,
                                       columnspan=2,
                                       sticky="n")
        tk.Label(self, text="Employee ID:", fg="white", bg=master.admin_bg_color).grid(row=2, column=4, sticky="ws")
        self.remove_id = tk.Entry(self)
        self.remove_id.grid(row=3, column=4, pady=2, sticky="w")
        tk.Button(self, text="Remove", padx=40, pady=4,
                  command=lambda: self.remove_employee(db, self.remove_id.get())).grid(
            row=3,
            column=5, sticky="w", padx=(10, 0))

    def add_employee(self, db, f, l, admin):
        if f is not "" and l is not "":
            cursor = db.cursor()
            add_employee = ("INSERT INTO employee "
                            "(first_name, last_name, manager_id) "
                            "VALUES (%s, %s, %s)")
            data_employee = (f, l, admin)
            # Insert new employee
            cursor.execute(add_employee, data_employee)
            emp_no = cursor.lastrowid
            # Make sure data is committed to the database
            db.commit()
            cursor.close()
            employee_info = "Employee ID: " + str(emp_no) + "\nFirst Name: " + f + "\nLast Name: " + l
            messagebox.showinfo("New Employee Added", employee_info)
            self.f_name.delete(0, 'end')
            self.l_name.delete(0, 'end')
        else:
            messagebox.showerror("Administrator Error", "Employee must have a first and last name.")

    def remove_employee(self, db, id):
        sql = "SELECT * FROM employee WHERE employee_id = %s"
        usr_entry = (id,)
        cursor = db.cursor()
        cursor.execute(sql, usr_entry)
        result = cursor.fetchall()
        cursor.close()
        # check if user entry is a valid ID from employee table
        if result.__len__() != 0:
            # valid ID confirm removal
            employee_info = "Employee ID: " + str(result[0][0]) + "\nFirst Name: " + result[0][1] + "\nLast Name: " + \
                            result[0][2]
            msg_box = tk.messagebox.askquestion('Confirm Removal',
                                                employee_info + "\n\nAre you sure you want to remove this employee?",
                                                icon='warning')
            if msg_box == 'yes':
                sql2 = "DELETE FROM employee WHERE employee_id = %s"
                usr_entry = (id,)
                cursor = db.cursor()
                cursor.execute(sql2, usr_entry)
                db.commit()
            self.remove_id.delete(0, 'end')
        else:
            messagebox.showerror("Administrator Error", "Invalid ID")
            self.remove_id.delete(0, 'end')
        cursor.close()


#
# CurUserPanel Class
#
class CurUserPanel(tk.Frame):
    f_name = None
    l_name = None
    id = None
    cur_search_frame = None

    def __init__(self, master, db):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="").grid(row=0, column=1, sticky="nsew")
        tk.Label(self, text="User: ").grid(row=1, column=0, sticky="nsw")
        tk.Label(self, text=master.get_user()).grid(row=1, column=1, sticky="nsw")
        tk.Label(self, text="Employee Type: ").grid(row=2, column=0, sticky="nsw")
        if FingerLakesSystem.privilege == 1:
            tk.Label(self, text="Administrator", fg="#cc3300").grid(row=2, column=1, sticky="nsw")
        else:
            tk.Label(self, text="Regular", fg="black").grid(row=2, column=1, sticky="nsw")
        tk.Label(self, text="Login Time: ").grid(row=3, column=0, sticky="nsw")
        tk.Label(self, text=master.get_login_time()).grid(row=3, column=1, sticky="nsw")
        tk.Button(self, text="Logout", command=lambda: master.logout(), padx=10, pady=4).grid(row=4, column=1,
                                                                                              sticky='nw')
        tk.Label(self, text="\n\n").grid(row=4, column=0, sticky="ns")
        tk.Label(self, text="").grid(row=11, column=0, sticky="nsew")

        # Employee Search
        tk.Label(self, text="{:^60s}".format("Lookup Employee"), fg="black", bg="white", borderwidth=2,
                 relief="sunken").grid(row=5, column=0, columnspan=3, sticky="ne")
        # first name
        tk.Label(self, text="First Name:").grid(row=6, column=0, sticky="se")
        self.f_name = tk.Entry(self)
        self.f_name.grid(row=6, column=1, columnspan=2, pady=5, sticky="se")
        # last name
        tk.Label(self, text="Last Name:").grid(row=7, column=0, sticky="se")
        self.l_name = tk.Entry(self)
        self.l_name.grid(row=7, column=1, columnspan=2, pady=5, sticky="se")
        # id
        tk.Label(self, text="Employee ID:").grid(row=8, column=0, sticky="se")
        self.id = tk.Entry(self)
        self.id.grid(row=8, column=1, columnspan=2, pady=5, sticky="se")
        # search button
        tk.Button(self, text="Search", padx=30,
                  command=lambda: self.update_search_panel(db, self.f_name.get(), self.l_name.get(),
                                                           self.id.get())).grid(
            row=9,
            column=2, pady=5, sticky="s")
        # clear button
        tk.Button(self, text="Clear", padx=10,
                  command=lambda: self.clear()).grid(
            row=9,
            column=1, pady=5, padx=5, sticky="se")

    def update_search_panel(self, db, f, l, id):
        new_frame = EmployeeSearchPanel(self, db, f, l, id)
        if self.cur_search_frame is not None:
            self.cur_search_frame.destroy()
        self.cur_search_frame = new_frame
        self.cur_search_frame.grid(row=1, column=3, rowspan=8, sticky="", padx=20)

    def clear(self):
        self.f_name.delete(0, 'end')
        self.l_name.delete(0, 'end')
        self.id.delete(0, 'end')


#
# EmployeeSearchPanel Class
#
class EmployeeSearchPanel(tk.Frame):
    f_name = None
    l_name = None
    remove_id = None
    s = None
    t = None
    result = None

    def __init__(self, master, db, f, l, id):
        tk.Frame.__init__(self, master)
        self.configure(bg="gray")
        self.s = tk.Scrollbar(self)
        self.t = tk.Text(self, height=20, width=60, relief="sunken", bg="#e6e6e6")
        self.s.pack(side='right', fill='y')
        self.t.pack(side='left', fill='y')
        self.s.config(command=self.t.yview)
        self.t.config(yscrollcommand=self.s.set)
        # search database insert string into scrollbar
        self.t.insert(tk.END, self.search(db, f, l, id))
        self.t.configure(state='disabled')

    # return string of search results
    def search(self, db, f, l, i):
        if i is not "":
            sql = "SELECT * FROM employee WHERE employee_id = %s"
            usr_entry = (i,)
            cursor = db.cursor()
            cursor.execute(sql, usr_entry)
            self.result = cursor.fetchall()
            cursor.close()
        else:
            sql = "SELECT * FROM employee WHERE first_name LIKE %s AND last_name LIKE %s ORDER BY last_name ASC"
            usr_entry = (f + "%", l + "%")
            cursor = db.cursor()
            cursor.execute(sql, usr_entry)
            self.result = cursor.fetchall()
        cursor.close()
        s = tabulate(self.result, headers=["ID", "First Name", "Last Name", "Email", "Type"], tablefmt="fancy_grid")
        return s


#
# EmployeePage Class
#
class EmployeePage(tk.Frame):
    admin_bg_color = "#cc3300"
    cur_admin_frame = None
    cur_usr_frame = None

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="   ").grid(row=0, column=0, sticky="nsew")
        self.update_cur_usr_panel(master)
        self.update_admin_panel(master)

    def update_cur_usr_panel(self, master):
        new_frame = CurUserPanel(self, master.database)
        if self.cur_usr_frame is not None:
            self.cur_usr_frame.destroy()
        self.cur_usr_frame = new_frame
        self.cur_usr_frame.grid(row=0, column=1, sticky="w")

    def update_admin_panel(self, master):
        admin_start_row = 2
        admin_start_col = 1
        """Destroys current admin frame and replaces it with a new one if privilege = 1."""
        if self.cur_admin_frame is not None:
            self.cur_admin_frame.destroy()
        if FingerLakesSystem.privilege == 1:
            new_frame = AdminPanel(self, master.database)
            self.cur_admin_frame = new_frame
            self.cur_admin_frame.grid(row=admin_start_row, column=admin_start_col, sticky="nsew")

    def logout(self):
        self.master.switch_main_frame(LoginPage)
        self.master.disable_menu()

    def get_login_time(self):
        return self.master.login_time

    def get_user(self):
        return self.master.user


if __name__ == "__main__":
    app = FingerLakesSystem()
    # Default window will fill screen
    w, h = app.winfo_screenwidth(), app.winfo_screenheight()
    app.geometry("%dx%d+0+0" % (w, h))
    app.mainloop()
