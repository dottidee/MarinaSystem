import tkinter as tk
import datetime
from tkinter import messagebox
import mysql.connector
from mysql.connector import errorcode


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
        x_pad = 50
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
        tk.Label(self, text="\n*** Must be logged in to use the system ***\n", fg='#cc3300').grid(row=1, column=1,
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


#
# AdminPanel Class
#
class AdminPanel(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.configure(bg=master.admin_bg_color)
        tk.Label(self, text="\nADMINISTRATOR:\n", fg="white", bg=master.admin_bg_color).grid(row=0, column=1)
        tk.Label(self, text="", bg=master.admin_bg_color).grid(row=0, column=0)
        tk.Label(self, text="   ", bg=master.admin_bg_color).grid(row=0, column=25)
        tk.Label(self, text="\n", bg=master.admin_bg_color).grid(row=2, column=0)
        tk.Button(self, text="Add Employee", padx=4, pady=4,
                  command=lambda: master.add_employee()).grid(row=1, column=1)
        tk.Button(self, text="View All Employees", padx=4, pady=4).grid(row=1, column=2)
        tk.Label(self, text="", bg=master.admin_bg_color).grid(row=1, column=3)
        tk.Entry(self).grid(row=1, column=4, pady=2)
        tk.Button(self, text="Search Employees", padx=4, pady=4, command=self.search()).grid(row=1, column=5)

    def search(self):
        return


#
# CurUserPanel Class
#
class CurUserPanel(tk.Frame):
    def __init__(self, master):
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
        tk.Button(self, text="Logout", command=lambda: master.logout(), padx=10, pady=4).grid(row=10, column=1,
                                                                                              sticky='w')
        tk.Label(self, text="").grid(row=11, column=0, sticky="nsew")


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
        self.update_cur_usr_panel()
        self.update_admin_panel()

    def update_cur_usr_panel(self):
        new_frame = CurUserPanel(self)
        if self.cur_usr_frame is not None:
            self.cur_usr_frame.destroy()
        self.cur_usr_frame = new_frame
        self.cur_usr_frame.grid(row=0, column=1, sticky="nsew")

    def update_admin_panel(self):
        admin_start_row = 2
        admin_start_col = 1
        """Destroys current admin frame and replaces it with a new one if privilege = 1."""
        new_frame = AdminPanel(self)
        if self.cur_admin_frame is not None:
            self.cur_admin_frame.destroy()
        if FingerLakesSystem.privilege == 1:
            self.cur_admin_frame = new_frame
            self.cur_admin_frame.grid(row=admin_start_row, column=admin_start_col, sticky="nsew")

    def add_employee(self):
        return

    def logout(self):
        self.master.switch_main_frame(LoginPage)
        self.master.disable_menu()

    def get_login_time(self):
        return self.master.login_time

    def get_user(self):
        return self.master.user


if __name__ == "__main__":
    app = FingerLakesSystem()
    app.mainloop()
