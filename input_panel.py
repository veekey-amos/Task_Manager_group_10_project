person 2:    import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkcalendar import DateEntry

class InputPanel:
    def _init_(self, parent, on_add):
        self.frame = tk.Frame(parent)
        self.frame.pack(pady=10)
        tk.Label(self.frame, text="Task:").grid(row=0, column=0)
        self.task_entry = tk.Entry(self.frame, width=25)
        self.task_entry.grid(row=0, column=1, padx=5)
        tk.Label(self.frame, text="Date:").grid(row=1, column=0)
        self.deadline_entry = DateEntry(self.frame, width=22, background="darkblue", foreground="white", date_pattern="yyyy-mm-dd")
        self.deadline_entry.grid(row=1, column=1, padx=5)
        tk.Label(self.frame, text="Time (HH:MM):").grid(row=2, column=0)
        time_values = [f"{h:02d}:{m:02d}" for h in range(0, 24) for m in (0, 30)]
        self.time_combo = ttk.Combobox(self.frame, values=time_values, width=22)
        self.time_combo.grid(row=2, column=1, padx=5)
        self.time_combo.set(datetime.now().strftime("%H:%M"))
        tk.Label(self.frame, text="Priority Level:").grid(row=3, column=0)
        self.priority_combo = ttk.Combobox(self.frame, values=["Low", "Medium", "High"], width=22)
        self.priority_combo.grid(row=3, column=1, padx=5)
        self.priority_combo.set("Medium")
        self.add_btn = tk.Button(self.frame, text="Add Task", command=self._on_add)
        self.add_btn.grid(row=4, column=1, pady=5, sticky="e")
        self.on_add = on_add

    def _on_add(self):
        name = self.task_entry.get()
        deadline = self.deadline_entry.get()
        time_str = self.time_combo.get()
        priority = self.priority_combo.get()
        self.on_add(name, deadline, time_str, priority)

    def clear(self):
        self.task_entry.delete(0, tk.END)
        self.deadline_entry.set_date(datetime.now())
        self.time_combo.set(datetime.now().strftime("%H:%M"))
        self.priority_combo.set("Medium")

if _name_ == "_main_":
    root = tk.Tk()
    def demo_add(name, d, t, p):
        print("ADD", name, d, t, p)
    panel = InputPanel(root, demo_add)
    root.mainloop()