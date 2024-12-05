import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



class FinanceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")

        # Database setup
        self.conn = sqlite3.connect('finance.db')
        self.create_table()

        # Main frames
        self.entry_frame = ttk.Frame(root, padding="10")
        self.entry_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.stats_frame = ttk.Frame(root, padding="10")
        self.stats_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.setup_entry_widgets()
        self.setup_stats_widgets()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            description TEXT
        )
        ''')
        self.conn.commit()

    def setup_entry_widgets(self):
        # Date entry
        ttk.Label(self.entry_frame, text="Date:").grid(row=0, column=0, sticky=tk.W)
        self.date_entry = ttk.Entry(self.entry_frame)
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        # Category dropdown
        ttk.Label(self.entry_frame, text="Category:").grid(row=1, column=0, sticky=tk.W)
        self.categories = ['Food', 'Transport', 'Utilities', 'Entertainment', 'Other']
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(self.entry_frame, textvariable=self.category_var)
        self.category_dropdown['values'] = self.categories
        self.category_dropdown.grid(row=1, column=1, padx=5, pady=5)

        # Amount entry
        ttk.Label(self.entry_frame, text="Amount:").grid(row=2, column=0, sticky=tk.W)
        self.amount_entry = ttk.Entry(self.entry_frame)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)

        # Transaction type
        ttk.Label(self.entry_frame, text="Type:").grid(row=3, column=0, sticky=tk.W)
        self.type_var = tk.StringVar(value="expense")
        ttk.Radiobutton(self.entry_frame, text="Expense", variable=self.type_var,
                        value="expense").grid(row=3, column=1, sticky=tk.W)
        ttk.Radiobutton(self.entry_frame, text="Income", variable=self.type_var,
                        value="income").grid(row=3, column=1, sticky=tk.E)

        # Description entry
        ttk.Label(self.entry_frame, text="Description:").grid(row=4, column=0, sticky=tk.W)
        self.desc_entry = ttk.Entry(self.entry_frame)
        self.desc_entry.grid(row=4, column=1, padx=5, pady=5)

        # Add transaction button
        ttk.Button(self.entry_frame, text="Add Transaction",
                   command=self.add_transaction).grid(row=5, column=0, columnspan=2, pady=10)

    def setup_stats_widgets(self):
        # Summary statistics
        self.summary_label = ttk.Label(self.stats_frame, text="")
        self.summary_label.grid(row=0, column=0, pady=10)

        # Matplotlib figure for charts
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.stats_frame)
        self.canvas.get_tk_widget().grid(row=1, column=0)

        self.update_stats()

    def add_transaction(self):
        try:
            date = self.date_entry.get()
            category = self.category_var.get()
            amount = float(self.amount_entry.get())
            trans_type = self.type_var.get()
            description = self.desc_entry.get()

            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO transactions (date, category, amount, type, description)
            VALUES (?, ?, ?, ?, ?)
            ''', (date, category, amount, trans_type, description))

            self.conn.commit()
            self.clear_entries()
            self.update_stats()
            messagebox.showinfo("Success", "Transaction added successfully!")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount!")

    def clear_entries(self):
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

    def update_stats(self):
        # Get transactions from database
        df = pd.read_sql_query("SELECT * FROM transactions", self.conn)

        if len(df) > 0:
            # Calculate summary statistics
            total_income = df[df['type'] == 'income']['amount'].sum()
            total_expenses = df[df['type'] == 'expense']['amount'].sum()
            balance = total_income - total_expenses

            summary_text = f"Total Income: ${total_income:.2f}\n"
            summary_text += f"Total Expenses: ${total_expenses:.2f}\n"
            summary_text += f"Balance: ${balance:.2f}"
            self.summary_label.config(text=summary_text)

            # Update chart
            self.ax.clear()
            expenses_by_category = df[df['type'] == 'expense'].groupby('category')['amount'].sum()
            expenses_by_category.plot(kind='pie', ax=self.ax)
            self.ax.set_title('Expenses by Category')
            self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceTracker(root)
    root.mainloop()