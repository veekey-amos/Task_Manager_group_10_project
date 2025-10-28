import tkinter as tk
from datetime import datetime
from task_model import Task
from input_panel import InputPanel
from list_panel import ListPanel
from tkinter import messagebox, filedialog
import re

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Group 10 Task Manager")
        self.root.geometry("750x520")
        self.tasks = []
        self.input_panel = InputPanel(root, self.add_task_callback)
        callbacks = {"mark_complete": self.mark_complete_callback, "delete_task": self.delete_task_callback, "edit_task": self.edit_task_callback, "export_calendar": self.export_calendar}
        self.list_panel = ListPanel(root, self.get_tasks, self.set_tasks, callbacks)
        self.progress = None
        self._make_progress()
        self.list_panel.update_tree()
        self.check_notifications()

    def _make_progress(self):
        from tkinter import ttk
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=500, mode="determinate")
        self.progress.pack(pady=10)
        self.update_progress()

    def add_task_callback(self, name, deadline, time_str, priority):
        if not name or not deadline or not time_str:
            messagebox.showerror("Error", "Please fill all fields.")
            return
        try:
            datetime.strptime(deadline, "%Y-%m-%d")
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            messagebox.showerror("Invalid Format", "Use YYYY-MM-DD for date and HH:MM for time.")
            return
        task = Task(name, deadline, time_str, priority)
        self.tasks.append(task)
        self.list_panel.update_tree()
        self.input_panel.clear()

    def get_tasks(self):
        return self.tasks

    def set_tasks(self, new_tasks):
        self.tasks = new_tasks

    def update_progress(self):
        if not self.tasks:
            self.progress["value"] = 0
            return
        completed = sum(1 for t in self.tasks if getattr(t, "completed", False))
        self.progress["value"] = (completed / len(self.tasks)) * 100

    def mark_complete_callback(self, name):
        for t in self.tasks:
            if t.name == name:
                t.completed = True
        self.list_panel.update_tree()
        self.update_progress()

    def delete_task_callback(self, name):
        self.tasks = [t for t in self.tasks if t.name != name]
        self.list_panel.update_tree()
        self.update_progress()

    def edit_task_callback(self, name):
        task_to_edit = next((t for t in self.tasks if t.name == name), None)
        if not task_to_edit:
            return
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Task")
        edit_window.geometry("360x300")
        edit_window.configure(bg="#F5F6FA")
        edit_window.resizable(False, False)
        tk.Label(edit_window, text="Edit Task Details", font=("Arial", 13, "bold"), bg="#F5F6FA", fg="#333").pack(pady=10)
        def labeled_entry(label, default):
            frm = tk.Frame(edit_window, bg="#F5F6FA")
            frm.pack(pady=4)
            tk.Label(frm, text=label, bg="#F5F6FA", fg="#333").pack(anchor="w")
            e = tk.Entry(frm, width=35, relief="solid", borderwidth=1)
            e.pack()
            e.insert(0, default)
            return e
        name_entry = labeled_entry("Task Name:", task_to_edit.name)
        date_entry = labeled_entry("Date (YYYY-MM-DD):", task_to_edit.deadline)
        time_entry = labeled_entry("Time (HH:MM):", task_to_edit.time_str)
        tk.Label(edit_window, text="Priority:", bg="#F5F6FA", fg="#333").pack(anchor="w", padx=15)
        from tkinter import ttk
        priority_combo = ttk.Combobox(edit_window, values=["Low", "Medium", "High"], width=32)
        priority_combo.pack(pady=4)
        priority_combo.set(task_to_edit.priority)
        def save_changes():
            new_name = name_entry.get().strip()
            new_deadline = date_entry.get().strip()
            new_time = time_entry.get().strip()
            new_priority = priority_combo.get().strip()
            if not new_name or not new_deadline or not new_time:
                messagebox.showerror("Error", "All fields must be filled.")
                return
            try:
                datetime.strptime(new_deadline, "%Y-%m-%d")
                datetime.strptime(new_time, "%H:%M")
            except ValueError:
                messagebox.showerror("Invalid Format", "Use YYYY-MM-DD for date and HH:MM for time.")
                return
            task_to_edit.name = new_name
            task_to_edit.deadline = new_deadline
            task_to_edit.time_str = new_time
            task_to_edit.priority = new_priority
            self.list_panel.update_tree()
            messagebox.showinfo("Task Updated", f"'{new_name}' was updated successfully.")
            edit_window.destroy()
        btn_frame = tk.Frame(edit_window, bg="#F5F6FA")
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="Save Changes", command=save_changes, bg="#007BFF", fg="white", relief="flat", padx=12, pady=6).grid(row=0, column=0, padx=8)
        tk.Button(btn_frame, text="Cancel", command=edit_window.destroy, bg="#B0B0B0", fg="white", relief="flat", padx=12, pady=6).grid(row=0, column=1, padx=8)

    def export_calendar(self):
        if not self.tasks:
            messagebox.showwarning("No Tasks", "There are no tasks to export.")
            return
        ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nCALSCALE:GREGORIAN\n"
        for t in self.tasks:
            try:
                dtstart = datetime.strptime(f"{t.deadline} {t.time_str}", "%Y-%m-%d %H:%M")
                ics_content += "BEGIN:VEVENT\n"
                ics_content += f"SUMMARY:{t.name}\n"
                ics_content += f"DTSTART:{dtstart.strftime('%Y%m%dT%H%M%S')}\n"
                ics_content += f"DTEND:{dtstart.strftime('%Y%m%dT%H%M%S')}\n"
                ics_content += f"DESCRIPTION:Priority - {t.priority}\n"
                ics_content += "END:VEVENT\n"
            except ValueError:
                continue
        ics_content += "END:VCALENDAR"
        file_path = filedialog.asksaveasfilename(defaultextension=".ics", filetypes=[("Calendar files", "*.ics")])
        if not file_path:
            return
        with open(file_path, "w") as f:
            f.write(ics_content)
        messagebox.showinfo("Export Successful", f"Tasks exported to {file_path}")

    def check_notifications(self):
        for t in self.tasks:
            if not t.completed and not t.notified:
                if t.is_overdue():
                    messagebox.showwarning("Task Overdue", f"⚠ '{t.name}' is overdue!")
                    t.notified = True
                elif t.is_due_soon():
                    messagebox.showinfo("Upcoming Task", f"🕒 '{t.name}' is due soon!")
                    t.notified = True
        self.root.after(60000, self.check_notifications)

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()
