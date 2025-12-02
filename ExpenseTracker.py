# Expense Tracker System--------------------------------------------------------

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime

# --- Global Variables ---
conn = None
cursor = None
root = None
dateEntry = None
categoryVar = None
amountEntry = None
descEntry = None
tree = None

def initDatabase():
    """Connect to database and create table"""
    global conn, cursor
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='anward$2244$',
            database='tkinter',
            port='3306'
        )
        cursor = conn.cursor()
        
        # MySQL syntax is slightly different from SQLite
        query = """
            CREATE TABLE IF NOT EXISTS expenses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date VARCHAR(20),
                category VARCHAR(50),
                amount DECIMAL(10, 2),
                description VARCHAR(255)
            )
        """
        cursor.execute(query)
        conn.commit()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Could not connect to MySQL: {err}")

def loadData():
    # Clear current data in the list
    for row in tree.get_children():
        tree.delete(row)
    
    # Fetch new data
    if cursor:
        cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
        rows = cursor.fetchall()
        
        for row in rows:
            tree.insert("", tk.END, values=row)

def addExpense():
    dateVal = dateEntry.get()
    categoryVal = categoryVar.get()
    amountVal = amountEntry.get()
    descVal = descEntry.get()

    # Validation
    if not dateVal or not amountVal:
        messagebox.showerror("Input Error", "Date and Amount fields are required!")
        return

    try:
        # Insert into database - MySQL uses %s placeholder
        if cursor:
            cursor.execute("INSERT INTO expenses (date, category, amount, description) VALUES (%s, %s, %s, %s)",
                                (dateVal, categoryVal, float(amountVal), descVal))
            conn.commit()
            
            # Clear inputs
            amountEntry.delete(0, tk.END)
            descEntry.delete(0, tk.END)
            
            # Refresh UI
            loadData()
            messagebox.showinfo("Success", "Expense added successfully!")
    except ValueError:
        messagebox.showerror("Value Error", "Amount must be a valid number!")

def deleteExpense():
    selectedItem = tree.selection()
    if not selectedItem:
        messagebox.showwarning("Selection Error", "Please select an item to delete")
        return

    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?")
    if confirm:
        for item in selectedItem:
            itemId = tree.item(item, 'values')[0]
            if cursor:
                # MySQL uses %s placeholder
                cursor.execute("DELETE FROM expenses WHERE id=%s", (itemId,))
        if conn:
            conn.commit()
        loadData()

def viewSummary():
    if cursor:
        cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        data = cursor.fetchall()

        summaryText = "Expense Summary by Category:\n----------------------------\n"
        totalSpent = 0
        for category, amount in data:
            # Handle potential None/Decimal types from MySQL
            val = float(amount) if amount else 0.0
            summaryText += f"{category}: {val:.2f}\n"
            totalSpent += val
        
        summaryText += f"----------------------------\nTotal Spent: {totalSpent:.2f}"
        
        messagebox.showinfo("Spending Summary", summaryText)

def onClosing():
    if conn:
        conn.close()
    root.destroy()


# 1. Setup Root Window
root = tk.Tk()
root.title("My Expense Tracker")
root.geometry("800x600")

# 2. Setup Database
initDatabase()

# 3. UI Layout

# Input Frame
entryFrame = tk.LabelFrame(root, text="Add New Expense", padx=10, pady=10)
entryFrame.pack(fill="x", padx=10, pady=5)

# Date Input
tk.Label(entryFrame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5)
dateEntry = tk.Entry(entryFrame)
dateEntry.insert(0, datetime.today().strftime('%Y-%m-%d'))
dateEntry.grid(row=0, column=1, padx=5, pady=5)

# Category Input
tk.Label(entryFrame, text="Category:").grid(row=0, column=2, padx=5, pady=5)
categoryVar = tk.StringVar()
categoryDropdown = ttk.Combobox(entryFrame, textvariable=categoryVar)
categoryDropdown['values'] = ('Food', 'Transport', 'Rent', 'Entertainment', 'Bills', 'Other')
categoryDropdown.current(0)
categoryDropdown.grid(row=0, column=3, padx=5, pady=5)

# Amount Input
tk.Label(entryFrame, text="Amount:").grid(row=1, column=0, padx=5, pady=5)
amountEntry = tk.Entry(entryFrame)
amountEntry.grid(row=1, column=1, padx=5, pady=5)

# Description Input
tk.Label(entryFrame, text="Description:").grid(row=1, column=2, padx=5, pady=5)
descEntry = tk.Entry(entryFrame)
descEntry.grid(row=1, column=3, padx=5, pady=5)

# Add Button
addBtn = tk.Button(entryFrame, text="Add Expense", command=addExpense, bg="#4CAF50", fg="white")
addBtn.grid(row=2, column=0, columnspan=4, sticky="ew", pady=10)

# Treeview (Data List)
treeFrame = tk.Frame(root)
treeFrame.pack(fill="both", expand=True, padx=10, pady=5)

columns = ("ID", "Date", "Category", "Amount", "Description")
tree = ttk.Treeview(treeFrame, columns=columns, show="headings")

# Configure Columns
tree.heading("ID", text="ID")
tree.heading("Date", text="Date")
tree.heading("Category", text="Category")
tree.heading("Amount", text="Amount")
tree.heading("Description", text="Description")

tree.column("ID", width=30)
tree.column("Date", width=100)
tree.column("Category", width=100)
tree.column("Amount", width=80)
tree.column("Description", width=200)

tree.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(treeFrame, orient="vertical", command=tree.yview)
scrollbar.pack(side="right", fill="y")
tree.configure(yscrollcommand=scrollbar.set)

# Action Buttons Frame
actionFrame = tk.Frame(root)
actionFrame.pack(fill="x", padx=10, pady=10)

deleteBtn = tk.Button(actionFrame, text="Delete Selected", command=deleteExpense, bg="#f44336", fg="white")
deleteBtn.pack(side="left", padx=5)

summaryBtn = tk.Button(actionFrame, text="View Summary", command=viewSummary, bg="#2196F3", fg="white")
summaryBtn.pack(side="left", padx=5)

# 4. Final Initialization
loadData()

# Ensure database closes when window is closed
root.protocol("WM_DELETE_WINDOW", onClosing)

root.mainloop()