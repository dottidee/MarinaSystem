import tkinter as tk
import datetime
from tkinter import messagebox
import mysql.connector
from mysql.connector import errorcode
from tabulate import tabulate


# FingerLakesSystem Class
# Acts as system's Main Window, contains a menu frame and a main frame
class MainWindow(tk.Tk):
    main_frame = None
    database = None

    def __init__(self):
        tk.Tk.__init__(self)
        self.winfo_toplevel().title("Finger Lakes Marinas System")
        # add menu bar to left side
        self.menu_frame = MenuFrame(self)
        self.menu_frame.pack(side="left")
        # connect to database
        self.connect_database()
        # load customer page
        self.switch_main_frame(CustomerPage)

    def switch_main_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self.main_frame is not None:
            self.main_frame.destroy()
        self.main_frame = new_frame
        self.main_frame.pack(side="left")
        self.activate_menu()

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

    def activate_menu(self):
        self.menu_frame.activate()

    def disable_menu(self):
        self.menu_frame.disable()

    def get_database(self):
        return self.database


#
# MenuFrame: Frame containing 4 buttons to allow for switching between Pages
# Methods: activate, disable
#
class MenuFrame(tk.Frame):
    slip_button = None
    service_button = None
    customer_button = None

    def __init__(self, master):
        x_pad = 10
        y_pad = 10

        tk.Frame.__init__(self, master)
        self.slip_button = tk.Button(self, text="Slip Rentals", padx=x_pad, pady=y_pad,
                                     command=lambda: master.switch_main_frame(SlipPage))
        self.service_button = tk.Button(self, text="  Services  ", padx=x_pad, pady=y_pad,
                                        command=lambda: master.switch_main_frame(ServicePage))
        self.customer_button = tk.Button(self, text="  Customer  ", padx=x_pad, pady=y_pad,
                                         command=lambda: master.switch_main_frame(CustomerPage))

        self.slip_button.grid(row=1, column=0)
        self.service_button.grid(row=2, column=0)
        self.customer_button.grid(row=0, column=0)

        self.activate()

    def activate(self):
        self.disable()
        if not isinstance(self.master.main_frame, SlipPage):
            self.slip_button.configure(state="normal")
        if not isinstance(self.master.main_frame, ServicePage):
            self.service_button.configure(state="normal")
        if not isinstance(self.master.main_frame, CustomerPage):
            self.customer_button.configure(state="normal")

    def disable(self):
        self.slip_button.configure(state="disabled")
        self.service_button.configure(state="disabled")
        self.customer_button.configure(state="disabled")


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
# CustomerPage Class
#
class CustomerPage(tk.Frame):
    cur_search_frame = None
    db = None

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="This is customer page").pack(side="top", fill="x", pady=10)
        self.db = master.get_database()
        # search button
        tk.Button(self, text="Search", padx=30,
                  command=lambda: self.update_search_panel(self.db, "john", "doe",
                                                           "")).pack()


    def update_search_panel(self, db, f, l, id):
        new_frame = CustomerSearchPanel(self, db, f, l, id)
        if self.cur_search_frame is not None:
            self.cur_search_frame.destroy()
        self.cur_search_frame = new_frame
        self.cur_search_frame.pack()


#
# EmployeeSearchPanel Class
#
class CustomerSearchPanel(tk.Frame):
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
        self.t = tk.Text(self, height=20, width=200, relief="sunken", bg="#e6e6e6")
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
            sql = "SELECT * FROM customer WHERE customer_id = %s"
            usr_entry = (i,)
            cursor = db.cursor()
            cursor.execute(sql, usr_entry)
            self.result = cursor.fetchall()
            cursor.close()
        else:
            sql = "SELECT * FROM customer WHERE first_name LIKE %s AND last_name LIKE %s ORDER BY last_name ASC"
            usr_entry = (f + "%", l + "%")
            cursor = db.cursor()
            cursor.execute(sql, usr_entry)
            self.result = cursor.fetchall()
        cursor.close()
        s = tabulate(self.result, headers=["ID", "First Name", "Last Name", "Phone", "Street", "City", "State", "Boat List", "Slip List", "Service List", "Lease List"],
                     tablefmt="fancy_grid")
        return s


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
