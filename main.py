import tkinter as tk
import datetime
import time
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
        self.menu_frame.pack(side="top")
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
        self.main_frame.pack(side="top")
        self.activate_menu()

    def connect_database(self):
        # Connect to remote database
        while 1:
            try:
                self.database = mysql.connector.connect(
                    host="remotemysql.com",
                    user="3rybg59bIE",
                    password="Rb8WxAwcfD",
                    database="3rybg59bIE"
                )
                return self.database
            # Catch all errors
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    messagebox.showerror("Database Error", "Invalid user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    messagebox.showerror("Database Error", "Database does not exist")
                else:
                    messagebox.showerror("Database Error", err)
                time.sleep(1)

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
        x_pad = 30
        y_pad = 10

        tk.Frame.__init__(self, master)
        self.slip_button = tk.Button(self, text="Slip Rentals", padx=x_pad, pady=y_pad,
                                     command=lambda: master.switch_main_frame(SlipPage))
        self.service_button = tk.Button(self, text="  Services  ", padx=x_pad, pady=y_pad,
                                        command=lambda: master.switch_main_frame(ServicePage))
        self.customer_button = tk.Button(self, text="  Customer  ", padx=x_pad, pady=y_pad,
                                         command=lambda: master.switch_main_frame(CustomerPage))

        self.customer_button.pack(side="left")
        self.slip_button.pack(side="left")
        self.service_button.pack(side="left")

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
    entry_fname = None
    entry_lname = None
    entry_id = None

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.db = master.get_database()
        # Lookup Customer ---------------------------------------------------------------------------------
        tk.Label(self, text="      Lookup Customer:      ", bg="black", fg="white").grid(row=0, column=0, columnspan=2)
        # first name
        tk.Label(self, text="First Name:").grid(row=1, column=0, sticky="e")
        self.entry_fname = tk.Entry(self, width=12)
        self.entry_fname.grid(row=1, column=1)
        # last name
        tk.Label(self, text="Last Name:").grid(row=2, column=0, sticky="e")
        self.entry_lname = tk.Entry(self, width=12)
        self.entry_lname.grid(row=2, column=1)
        # id
        tk.Label(self, text="Customer ID:").grid(row=3, column=0, sticky="e")
        self.entry_id = tk.Entry(self, width=12)
        self.entry_id.grid(row=3, column=1)
        # clear button
        tk.Button(self, text="Clear", padx=20,
                  command=lambda: self.clear_lookup_entry()).grid(row=4, column=0)
        # search button
        self.bind("<Return>",
                  (lambda event: self.update_search_panel(self.db, self.entry_fname.get(), self.entry_lname.get(),
                                                          self.entry_id.get())))

        tk.Button(self, text="Search", padx=20,
                  command=lambda: self.update_search_panel(self.db, self.entry_fname.get(), self.entry_lname.get(),
                                                           self.entry_id.get())).grid(row=4, column=1)

        # Add Customer ---------------------------------------------------------------------------------
        tk.Button(self, text="      Add Customer      ", command=lambda: self.add_customer()).grid(row=5, column=0,
                                                                                                   columnspan=2)

        # initially show all customers
        self.update_search_panel(self.db, "", "", "")

    def update_search_panel(self, db, f, l, id):
        new_frame = CustomerSearchPanel(self, db, f, l, id)
        if self.cur_search_frame is not None:
            self.cur_search_frame.destroy()
        self.cur_search_frame = new_frame
        self.cur_search_frame.grid(row=0, column=2, rowspan=30)

    def clear_lookup_entry(self):
        self.entry_fname.delete(0, 'end')
        self.entry_lname.delete(0, 'end')
        self.entry_id.delete(0, 'end')

    def add_customer(self):
        AddCustomerPopup(self.master, self.db)
        self.update_search_panel(self.db, self.entry_fname.get(), self.entry_lname.get(),
                                 self.entry_id.get())


class AddCustomerPopup(tk.Toplevel):
    db = None
    f_name = None
    l_name = None
    phone = None
    street = None
    city = None
    state = None

    def __init__(self, parent, db, title="Add Customer"):
        self.top = tk.Toplevel.__init__(self, parent)
        self.db = db
        self.transient(parent)
        if title:
            self.title(title)
        self.parent = parent
        self.result = None
        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)
        self.buttonbox()
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                  parent.winfo_rooty() + 50))
        self.initial_focus.focus_set()
        self.wait_window(self)

    #
    # construction hooks
    def body(self, master):
        tk.Label(master, text="* First Name:").grid(row=0, sticky="e")
        tk.Label(master, text="* Last Name:").grid(row=1, sticky="e")
        tk.Label(master, text="* Phone #:").grid(row=2, sticky="e")
        tk.Label(master, text="Street Address:").grid(row=3, sticky="e")
        tk.Label(master, text="City:").grid(row=4, sticky="e")
        tk.Label(master, text="State:").grid(row=5, sticky="e")

        self.f_name = tk.Entry(master)
        self.l_name = tk.Entry(master)
        self.phone = tk.Entry(master)
        self.street = tk.Entry(master)
        self.city = tk.Entry(master)
        self.state = tk.Entry(master)

        self.f_name.grid(row=0, column=1)
        self.l_name.grid(row=1, column=1)
        self.phone.grid(row=2, column=1)
        self.street.grid(row=3, column=1)
        self.city.grid(row=4, column=1)
        self.state.grid(row=5, column=1)
        return self.f_name  # initial focus

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons
        box = tk.Frame(self)
        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()

    #
    # standard button semantics
    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks
    def validate(self):
        return 1  # override

    def apply(self):
        if self.f_name.get() is not "" and self.l_name.get() is not "" and self.phone.get() is not "":
            self.db = self.master.connect_database()
            cursor = self.db.cursor()
            add_employee = ("INSERT INTO customer "
                            "(first_name, last_name, phone, street, city, state) "
                            "VALUES (%s, %s, %s, %s, %s, %s)")
            data_employee = (self.f_name.get(), self.l_name.get(), self.phone.get(), self.street.get(), self.city.get(),
                             self.state.get())
            # Insert new employee
            cursor.execute(add_employee, data_employee)
            # Make sure data is committed to the database
            self.db.commit()
            cursor.close()
        else:
            messagebox.showerror("Error", "Customer must have a first name, last name and phone number.")


#
# CustomerSearchPanel Class
#
class CustomerSearchPanel(tk.Frame):
    f_name = None
    l_name = None
    remove_id = None
    s = None
    t = None
    result = None

    def __init__(self, master, db, f, l, x):
        tk.Frame.__init__(self, master)
        self.configure(bg="#e6e6e6")
        self.s = tk.Scrollbar(self)
        self.t = tk.Text(self, height=50, width=150, relief="sunken")
        self.s.pack(side='right', fill='y')
        self.t.pack(side='left', fill='y')
        self.s.config(command=self.t.yview)
        self.t.config(yscrollcommand=self.s.set)
        # search database insert string into scrollbar
        # print(self.search(db, f, l, x))
        self.t.insert(tk.INSERT, self.search(db, f, l, x))
        self.t.configure(state='disabled')

    # return string of search results
    def search(self, db, f, l, i):
        if i is not "":
            sql = "SELECT * FROM customer WHERE customer_id = %s"
            usr_entry = (i,)
            db = self.master.master.connect_database()
            cursor = db.cursor()
            cursor.execute(sql, usr_entry)
            self.result = cursor.fetchall()
            cursor.close()
        else:
            sql = "SELECT * FROM customer WHERE first_name LIKE %s AND last_name LIKE %s ORDER BY last_name ASC"
            usr_entry = (f + "%", l + "%")
            db = self.master.master.connect_database()
            cursor = db.cursor()
            cursor.execute(sql, usr_entry)
            self.result = cursor.fetchall()
            cursor.close()
        # if only one customer found display detailed view
        if self.result.__len__() == 1:
            CustomerDetailPopup(self.master.master, db, self.result)
            # update result in case of change
            sql = "SELECT * FROM customer WHERE customer_id = %s"
            usr_entry = (self.result[0][0],)
            db = self.master.master.connect_database()
            cursor = db.cursor()
            cursor.execute(sql, usr_entry)
            self.result = cursor.fetchall()
            cursor.close()
        # only display first 6 columns
        for i in range(0, self.result.__len__()):
            self.result[i] = self.result[i][:7]
        s = tabulate(self.result,
                     headers=["ID", "First Name", "Last Name", "Phone", "Street", "City", "State"],
                     tablefmt="simple")
        return s


class CustomerDetailPopup(tk.Toplevel):
    db = None
    f_name = None
    l_name = None
    phone = None
    street = None
    city = None
    state = None
    customer = None
    apply_button = None
    edit_button = None
    close_button = None

    def __init__(self, parent, db, result, title="Customer Details"):
        self.top = tk.Toplevel.__init__(self, parent)
        self.db = db
        self.customer = result
        self.transient(parent)
        if title:
            self.title(title)
        self.parent = parent
        self.result = None
        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)
        self.buttonbox()
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                  parent.winfo_rooty() + 50))
        self.initial_focus.focus_set()
        self.wait_window(self)

    #
    # construction hooks
    def body(self, master):
        tk.Label(master, text="First Name:").grid(row=0, sticky="e")
        tk.Label(master, text="Last Name:").grid(row=1, sticky="e")
        tk.Label(master, text="Phone #:").grid(row=2, sticky="e")
        tk.Label(master, text="Street Address:").grid(row=3, sticky="e")
        tk.Label(master, text="City:").grid(row=4, sticky="e")
        tk.Label(master, text="State:").grid(row=5, sticky="e")

        self.f_name = tk.Entry(master)
        self.f_name.insert(tk.END, self.customer[0][1])
        self.l_name = tk.Entry(master)
        self.l_name.insert(tk.END, self.customer[0][2])
        self.phone = tk.Entry(master)
        self.phone.insert(tk.END, self.customer[0][3])
        self.street = tk.Entry(master)
        self.street.insert(tk.END, self.customer[0][4])
        self.city = tk.Entry(master)
        self.city.insert(tk.END, self.customer[0][5])
        self.state = tk.Entry(master)
        self.state.insert(tk.END, self.customer[0][6])
        self.disable_entries()

        self.f_name.grid(row=0, column=1)
        self.l_name.grid(row=1, column=1)
        self.phone.grid(row=2, column=1)
        self.street.grid(row=3, column=1)
        self.city.grid(row=4, column=1)
        self.state.grid(row=5, column=1)
        return self.f_name  # initial focus

    def disable_entries(self):
        self.f_name.configure(state="disabled")
        self.l_name.configure(state="disabled")
        self.phone.configure(state="disabled")
        self.street.configure(state="disabled")
        self.city.configure(state="disabled")
        self.state.configure(state="disabled")

    def buttonbox(self):
        # add button box
        box = tk.Frame(self)
        self.edit_button = tk.Button(box, text="Edit Customer", width=15, command=self.enable_entries)
        self.edit_button.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Delete Customer", width=15, command=self.delete_customer)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        self.apply_button = tk.Button(box, text="Apply Changes", width=15, command=self.ok, state=tk.DISABLED)
        self.apply_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.close_button = tk.Button(box, text="Close", width=10, command=self.cancel, state=tk.ACTIVE)
        self.close_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.cancel)
        self.bind("<Escape>", self.cancel)
        box.pack()

    #
    # standard button semantics
    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks
    def validate(self):
        return 1  # override

    def apply(self):
        # confirm removal
        msg_box = tk.messagebox.askquestion("Confirm Update",
                                            "Are you sure you want to update this customer?\n",
                                            icon='warning')
        if msg_box == 'yes':
            sql = "UPDATE customer SET first_name = %s, last_name = %s, phone = %s, street = %s, city = %s, state = %s WHERE customer_id = %s"
            usr_entry = (
                self.f_name.get(), self.l_name.get(), self.phone.get(), self.street.get(), self.city.get(),
                self.state.get(),
                self.customer[0][0])
            self.db = self.master.connect_database()
            cursor = self.db.cursor()
            cursor.execute(sql, usr_entry)
            self.db.commit()
            self.parent.focus_set()
            self.destroy()

    def enable_entries(self):
        self.f_name.configure(state="normal")
        self.l_name.configure(state="normal")
        self.phone.configure(state="normal")
        self.street.configure(state="normal")
        self.city.configure(state="normal")
        self.state.configure(state="normal")
        self.apply_button.configure(state="normal")
        self.bind("<Return>", self.ok)
        self.close_button.configure(state=tk.NORMAL)
        self.apply_button.configure(state=tk.ACTIVE)
        self.edit_button.configure(state=tk.DISABLED)

    def delete_customer(self):
        # confirm removal
        msg_box = tk.messagebox.askquestion("Confirm Removal",
                                            "Are you sure you want to remove this customer? \n\nThis action cannot be undone.\n",
                                            icon='warning')
        if msg_box == 'yes':
            sql2 = "DELETE FROM customer WHERE customer_id = %s"
            usr_entry = (self.customer[0][0],)
            self.db = self.master.connect_database()
            cursor = self.db.cursor()
            cursor.execute(sql2, usr_entry)
            self.db.commit()
            self.cancel()


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
