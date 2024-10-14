import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class ToDoList:
    def __init__(self, master):
        self.master = master
        self.master.title("To-Do List")
        self.master.geometry("600x400")
        self.master.configure(bg='#f0f0f0')

        self.create_db()
        self.create_widgets()

    def create_db(self):
        self.conn = sqlite3.connect('todo.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS tasks
                         (id INTEGER PRIMARY KEY,
                          task TEXT,
                          date TEXT,
                          status TEXT)''')
        self.conn.commit()

    def create_widgets(self):
        # Task Entry
        self.task_frame = tk.Frame(self.master, bg='#f0f0f0')
        self.task_frame.pack(pady=10)

        self.task_label = tk.Label(self.task_frame, text="Task:", bg='#f0f0f0', font=('Arial', 12))
        self.task_label.grid(row=0, column=0, padx=5)

        self.task_entry = tk.Entry(self.task_frame, width=40, font=('Arial', 12))
        self.task_entry.grid(row=0, column=1, padx=5)

        self.add_button = tk.Button(self.task_frame, text="Add Task", command=self.add_task, 
                                    bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
        self.add_button.grid(row=0, column=2, padx=5)

        # Task List
        self.tree_frame = tk.Frame(self.master)
        self.tree_frame.pack(pady=10)

        self.tree = ttk.Treeview(self.tree_frame, columns=("Task", "Date", "Status"), show="headings", height=10)
        self.tree.heading("Task", text="Task")
        self.tree.heading("Date", text="Date Added")
        self.tree.heading("Status", text="Status")
        self.tree.column("Task", width=300)
        self.tree.column("Date", width=100)
        self.tree.column("Status", width=100)
        self.tree.pack(side=tk.LEFT)

        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Buttons Frame
        self.button_frame = tk.Frame(self.master, bg='#f0f0f0')
        self.button_frame.pack(pady=10)

        self.complete_button = tk.Button(self.button_frame, text="Mark Complete", command=self.mark_complete,
                                         bg='#2196F3', fg='white', font=('Arial', 10, 'bold'))
        self.complete_button.grid(row=0, column=0, padx=5)

        self.delete_button = tk.Button(self.button_frame, text="Delete Task", command=self.delete_task,
                                       bg='#F44336', fg='white', font=('Arial', 10, 'bold'))
        self.delete_button.grid(row=0, column=1, padx=5)

        self.update_button = tk.Button(self.button_frame, text="Update Task", command=self.update_task,
                                       bg='#FF9800', fg='white', font=('Arial', 10, 'bold'))
        self.update_button.grid(row=0, column=2, padx=5)

        self.set_tree_colors()
        self.view_tasks()

    def set_tree_colors(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#D3D3D3",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="#D3D3D3")
        style.map('Treeview', background=[('selected', '#4CAF50')])
        
        self.tree.tag_configure('completed', background='light green')

    def add_task(self):
        task = self.task_entry.get()
        if task:
            date = datetime.now().strftime("%Y-%m-%d")
            self.c.execute("INSERT INTO tasks (task, date, status) VALUES (?, ?, ?)",
                           (task, date, "Pending"))
            self.conn.commit()
            self.task_entry.delete(0, tk.END)
            self.view_tasks()
        else:
            messagebox.showerror("Error", "Please enter a task!")

    def view_tasks(self):
        self.tree.delete(*self.tree.get_children())
        self.c.execute("SELECT * FROM tasks")
        for row in self.c.fetchall():
            if row[3] == "Completed":
                self.tree.insert("", tk.END, values=(row[1], row[2], row[3]), tags=('completed',))
            else:
                self.tree.insert("", tk.END, values=(row[1], row[2], row[3]))

    def mark_complete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a task to mark as complete!")
            return
        task = self.tree.item(selected)['values'][0]
        self.c.execute("UPDATE tasks SET status=? WHERE task=?", ("Completed", task))
        self.conn.commit()
        self.view_tasks()

    def delete_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a task to delete!")
            return
        task = self.tree.item(selected)['values'][0]
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this task?"):
            self.c.execute("DELETE FROM tasks WHERE task=?", (task,))
            self.conn.commit()
            self.view_tasks()

    def update_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a task to update!")
            return
        task = self.tree.item(selected)['values'][0]
        
        update_window = tk.Toplevel(self.master)
        update_window.title("Update Task")
        update_window.configure(bg='#f0f0f0')
        
        tk.Label(update_window, text="Update Task:", bg='#f0f0f0', font=('Arial', 12)).pack(pady=5)
        update_entry = tk.Entry(update_window, width=40, font=('Arial', 12))
        update_entry.insert(0, task)
        update_entry.pack(pady=5)
        
        def save_update():
            new_task = update_entry.get()
            if new_task:
                self.c.execute("UPDATE tasks SET task=? WHERE task=?", (new_task, task))
                self.conn.commit()
                update_window.destroy()
                self.view_tasks()
            else:
                messagebox.showerror("Error", "Task cannot be empty!")
        
        save_button = tk.Button(update_window, text="Save", command=save_update,
                                bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
        save_button.pack(pady=10)

def main():
    root = tk.Tk()
    app = ToDoList(root)
    root.mainloop()

if __name__ == "__main__":
    main()