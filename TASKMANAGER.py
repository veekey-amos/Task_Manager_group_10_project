# import necessary libraries/packages
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime, timedelta
import re
from tkcalendar import DateEntry


class Task:
    # create a Task with name, date deadline, time, and priority level
    def __init__(self, name, deadline, time_str, priority):
        self.name = name
        self.deadline = deadline
        self.time_str = time_str
        self.priority = priority
        self.completed = False
        self.notified = False  # prevent repeat alerts

    # Return True if the task's date/time is before current time
    def is_overdue(self):
        try:
            full_datetime = f"{self.deadline} {self.time_str}"
            return datetime.strptime(full_datetime, "%Y-%m-%d %H:%M") < datetime.now()
        except ValueError:
            return False

    # Return True if the task is due within the next 10 minutes
    def is_due_soon(self):
        try:
            full_datetime = f"{self.deadline} {self.time_str}"
            task_time = datetime.strptime(full_datetime, "%Y-%m-%d %H:%M")
            now = datetime.now()
            return now <= task_time <= now + timedelta(minutes=10)
        except ValueError:
            return False


class TaskManagerApp:
    #window, inputs, control and table set up
    def __init__(self, root):
        self.root = root
        self.root.title("Group 10 Task Manager")
        self.root.geometry("750x520")

        self.tasks = []

        #Input Frame
        frame = tk.Frame(root)
        frame.pack(pady=10)

        # Task name label and name input
        tk.Label(frame, text="Task:").grid(row=0, column=0)
        self.task_entry = tk.Entry(frame, width=25)
        self.task_entry.grid(row=0, column=1, padx=5)

        # select Date or input date
        tk.Label(frame, text="Date:").grid(row=1, column=0)
        self.deadline_entry = DateEntry(
            frame,
            width=22,
            background="darkblue",
            foreground="white",
            date_pattern="yyyy-mm-dd"
        )
        self.deadline_entry.grid(row=1, column=1, padx=5)

        # Time drop down
        tk.Label(frame, text="Time (HH:MM):").grid(row=2, column=0)
        time_values = [f"{h:02d}:{m:02d}" for h in range(0, 24) for m in (0, 30)]
        self.time_combo = ttk.Combobox(frame, values=time_values, width=22)
        self.time_combo.grid(row=2, column=1, padx=5)
        self.time_combo.set(datetime.now().strftime("%H:%M"))

        # Priority dropdown
        tk.Label(frame, text="Priority Level:").grid(row=3, column=0)
        self.priority_combo = ttk.Combobox(frame, values=["Low", "Medium", "High"], width=22)
        self.priority_combo.grid(row=3, column=1, padx=5)
        self.priority_combo.set("Medium")

        # Add Task button
        add_btn = tk.Button(frame, text="Add Task", command=self.add_task)
        add_btn.grid(row=4, column=1, pady=5, sticky="e")

        #Task List (Table)
        self.tree = ttk.Treeview(
            root,
            columns=("Name", "Deadline", "Time", "Priority", "Status"),
            show="headings"
        )
        for col, text in zip(("Name", "Deadline", "Time", "Priority", "Status"),
                             ("Task Name", "Date", "Time", "Priority", "Status")):
            self.tree.heading(col, text=text)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Bind drag-and-drop function
        self.tree.bind("<ButtonPress-1>", self.on_drag_start)
        self.tree.bind("<B1-Motion>", self.on_drag_motion)
        self.tree.bind("<ButtonRelease-1>", self.on_drag_drop)
        self.drag_data = {"start_index": None}

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        # Mark complete, Delete task, Edit task,Filter search,Clear search and Export to calendar Buttons
        tk.Button(btn_frame, text="Mark Complete", command=self.mark_complete).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Delete Task", command=self.delete_task).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Edit Task", command=self.edit_task).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Filter Search", command=self.filter_tasks).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Clear Search", command=self.update_tree).grid(row=0, column=4, padx=5)
        tk.Button(btn_frame, text="Export to Calendar", command=self.export_calendar).grid(row=0, column=5, padx=5)

        # Sort dropdown to choose sorting type
        tk.Label(btn_frame, text="Sort:").grid(row=0, column=6, padx=(15, 5))
        self.sort_combo = ttk.Combobox(btn_frame, values=["Sort by Priority", "Sort by Date/Time"], width=18)
        self.sort_combo.grid(row=0, column=7)
        self.sort_combo.bind("<<ComboboxSelected>>", self.auto_sort)

        # Progress bar for task completion
        self.progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
        self.progress.pack(pady=10)
        self.update_progress()

        # Begin recurring notification checks
        self.check_notifications()

    # Record index of the row where drag started
    def on_drag_start(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.drag_data["start_index"] = self.tree.index(item)

    # Placeholder for drag motion handling
    def on_drag_motion(self, event):
        pass

    # drop selsected task and reorder the tasks list when mouse is released
    def on_drag_drop(self, event):
        if self.drag_data["start_index"] is None:
            return
        target_item = self.tree.identify_row(event.y)
        if not target_item:
            return
        new_index = self.tree.index(target_item)
        old_index = self.drag_data["start_index"]
        if new_index != old_index:
            task = self.tasks.pop(old_index)
            self.tasks.insert(new_index, task)
            self.update_tree()
        self.drag_data["start_index"] = None

    # Add new task
    def add_task(self):
        name = self.task_entry.get()
        deadline = self.deadline_entry.get()
        time_str = self.time_combo.get()
        priority = self.priority_combo.get()

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
        self.update_tree()
        self.clear_entries()

    # Open edit window to modify name, date, time, and priority
    def edit_task(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select Task", "Please select a task to edit.")
            return

        task_name = self.tree.item(selected, "values")[0]
        task_to_edit = next((t for t in self.tasks if t.name == task_name), None)
        if not task_to_edit:
            return

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Task")
        edit_window.geometry("360x300")
        edit_window.configure(bg="#F5F6FA")
        edit_window.resizable(False, False)

        tk.Label(edit_window, text="Edit Task Details", font=("Arial", 13, "bold"), bg="#F5F6FA", fg="#333").pack(pady=10)

        #create a labeled entry field
        def labeled_entry(label, default_value):
            frame = tk.Frame(edit_window, bg="#F5F6FA")
            frame.pack(pady=4)
            tk.Label(frame, text=label, bg="#F5F6FA", fg="#333").pack(anchor="w")
            entry = tk.Entry(frame, width=35, relief="solid", borderwidth=1)
            entry.pack()
            entry.insert(0, default_value)
            return entry

        name_entry = labeled_entry("Task Name:", task_to_edit.name)
        date_entry = labeled_entry("Date (YYYY-MM-DD):", task_to_edit.deadline)
        time_entry = labeled_entry("Time (HH:MM):", task_to_edit.time_str)

        tk.Label(edit_window, text="Priority:", bg="#F5F6FA", fg="#333").pack(anchor="w", padx=15)
        priority_combo = ttk.Combobox(edit_window, values=["Low", "Medium", "High"], width=32)
        priority_combo.pack(pady=4)
        priority_combo.set(task_to_edit.priority)

        # Save  edited values back to the Task object after validation
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

            self.update_tree()
            messagebox.showinfo("Task Updated", f"'{new_name}' was updated successfully.")
            edit_window.destroy()

        btn_frame = tk.Frame(edit_window, bg="#F5F6FA")
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="Save Changes", command=save_changes, bg="#007BFF", fg="white",
                  relief="flat", padx=12, pady=6).grid(row=0, column=0, padx=8)
        tk.Button(btn_frame, text="Cancel", command=edit_window.destroy, bg="#B0B0B0", fg="white",
                  relief="flat", padx=12, pady=6).grid(row=0, column=1, padx=8)

    # Clear the Add Task inputs and reset to default settings
    def clear_entries(self):
        self.task_entry.delete(0, tk.END)
        self.deadline_entry.set_date(datetime.now())
        self.time_combo.set(datetime.now().strftime("%H:%M"))
        self.priority_combo.set("Medium")

    # update the table from the tasks list and apply tags/colors
    def update_tree(self):
        self.tree.delete(*self.tree.get_children())
        for task in self.tasks:
            status = "Completed" if task.completed else "Pending"
            tag = "completed" if task.completed else ("overdue" if task.is_overdue() else "")
            self.tree.insert("", "end", values=(task.name, task.deadline, task.time_str, task.priority, status), tags=(tag,))
        self.tree.tag_configure("overdue", background="tomato")
        self.tree.tag_configure("completed", background="lightgreen")
        self.update_progress()

    # Mark the selected task as completed
    def mark_complete(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select Task", "Please select a task to mark complete.")
            return
        task_name = self.tree.item(selected, "values")[0]
        for t in self.tasks:
            if t.name == task_name:
                t.completed = True
        self.update_tree()

    # Delete the selected task from the list
    def delete_task(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select Task", "Please select a task to delete.")
            return
        task_name = self.tree.item(selected, "values")[0]
        self.tasks = [t for t in self.tasks if t.name != task_name]
        self.update_tree()

    # filter search Prompt
    def filter_tasks(self):
        keyword = simpledialog.askstring("Filter Search", "Enter keyword or regex:")
        if not keyword:
            return
        try:
            pattern = re.compile(keyword, re.IGNORECASE)
        except re.error:
            messagebox.showerror("Invalid Pattern", "Invalid regular expression.")
            return
        filtered = [t for t in self.tasks if pattern.search(t.name)]
        self.tree.delete(*self.tree.get_children())
        for t in filtered:
            status = "Completed" if t.completed else "Pending"
            tag = "completed" if t.completed else ("overdue" if t.is_overdue() else "")
            self.tree.insert("", "end", values=(t.name, t.deadline, t.time_str, t.priority, status), tags=(tag,))
        self.tree.tag_configure("overdue", background="tomato")
        self.tree.tag_configure("completed", background="lightgreen")

    # Sort tasks drop down
    def auto_sort(self, event=None):
        option = self.sort_combo.get()
        if option == "Sort by Priority":
            order = {"High": 1, "Medium": 2, "Low": 3}
            self.tasks.sort(key=lambda x: order.get(x.priority, 3))
        elif option == "Sort by Date/Time":
            try:
                self.tasks.sort(key=lambda x: datetime.strptime(f"{x.deadline} {x.time_str}", "%Y-%m-%d %H:%M"))
            except ValueError:
                messagebox.showerror("Invalid Date/Time", "One or more tasks have invalid date/time.")
        self.update_tree()

    # Export created tasks to desktop to enable exporting to local calender
    def export_calendar(self):
        if not self.tasks:
            messagebox.showwarning("No Tasks", "There are no tasks to export.")
            return
        ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nCALSCALE:GREGORIAN\n"
        for t in self.tasks:
            try:
                dtstart = datetime.strptime(f"{t.deadline} {t.time_str}", "%Y-%m-%d %H:%M")
                ics_content += (
                    "BEGIN:VEVENT\n"
                    f"SUMMARY:{t.name}\n"
                    f"DTSTART:{dtstart.strftime('%Y%m%dT%H%M%S')}\n"
                    f"DTEND:{dtstart.strftime('%Y%m%dT%H%M%S')}\n"
                    f"DESCRIPTION:Priority - {t.priority}\n"
                    "END:VEVENT\n"
                )
            except ValueError:
                continue
        ics_content += "END:VCALENDAR"
        file_path = filedialog.asksaveasfilename(defaultextension=".ics", filetypes=[("Calendar files", "*.ics")])
        if not file_path:
            return
        with open(file_path, "w") as f:
            f.write(ics_content)
        messagebox.showinfo("Export Successful", f"Tasks exported to {file_path}")

    # Updates the progress bar according to completed tasks
    def update_progress(self):
        if not self.tasks:
            self.progress["value"] = 0
            return
        completed = sum(t.completed for t in self.tasks)
        self.progress["value"] = (completed / len(self.tasks)) * 100

    # notify users of overdue or upcoming tasks  every minute
    def check_notifications(self):
        for t in self.tasks:
            if not t.completed and not t.notified:
                if t.is_overdue():
                    messagebox.showwarning("Task Overdue", f"⚠ '{t.name}' is overdue!")
                    t.notified = True
                elif t.is_due_soon():
                    messagebox.showinfo("Upcoming Task", f"🕒 '{t.name}' is due soon!")
                    t.notified = True
        self.root.after(60000, self.check_notifications)  # check every minute


# starts the main loop
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()
