person 3:  import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime

class ListPanel:
    def __init__(self, parent, get_tasks, set_tasks, callbacks):
        self.frame = tk.Frame(parent)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.get_tasks = get_tasks
        self.set_tasks = set_tasks
        self.callbacks = callbacks

        self.tree = ttk.Treeview(self.frame, columns=("Name", "Deadline", "Time", "Priority", "Status"), show="headings")
        for col, text in zip(("Name", "Deadline", "Time", "Priority", "Status"), ("Task Name", "Date", "Time", "Priority", "Status")):
            self.tree.heading(col, text=text)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<ButtonPress-1>", self._on_drag_start)
        self.tree.bind("<ButtonRelease-1>", self._on_drag_drop)
        self.drag_data = {"start_index": None}

        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Mark Complete", command=self._mark_complete).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Delete Task", command=self._delete_task).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Edit Task", command=self._edit_task).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Filter Search", command=self._filter_tasks).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Clear Search", command=self.update_tree).grid(row=0, column=4, padx=5)
        tk.Button(btn_frame, text="Export to Calendar", command=self._export_calendar).grid(row=0, column=5, padx=5)

    def _on_drag_start(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.drag_data["start_index"] = self.tree.index(item)

    def _on_drag_drop(self, event):
        if self.drag_data["start_index"] is None:
            return
        target_item = self.tree.identify_row(event.y)
        if not target_item:
            return
        new_index = self.tree.index(target_item)
        old_index = self.drag_data["start_index"]
        if new_index != old_index:
            tasks = self.get_tasks()
            task = tasks.pop(old_index)
            tasks.insert(new_index, task)
            self.set_tasks(tasks)
            self.update_tree()
        self.drag_data["start_index"] = None

    def update_tree(self):
        self.tree.delete(*self.tree.get_children())
        tasks = self.get_tasks()
        for task in tasks:
            status = "Completed" if getattr(task, "completed", False) else "Pending"
            tag = "completed" if getattr(task, "completed", False) else ("overdue" if getattr(task, "is_overdue") and task.is_overdue() else "")
            self.tree.insert("", "end", values=(task.name, task.deadline, task.time_str, task.priority, status), tags=(tag,))
        self.tree.tag_configure("overdue", background="tomato")
        self.tree.tag_configure("completed", background="lightgreen")

    def _selected_task_name(self):
        sel = self.tree.focus()
        if not sel:
            return None
        return self.tree.item(sel, "values")[0]

    def _mark_complete(self):
        name = self._selected_task_name()
        if not name:
            messagebox.showwarning("Select Task", "Please select a task to mark complete.")
            return
        self.callbacks["mark_complete"](name)
        self.update_tree()

    def _delete_task(self):
        name = self._selected_task_name()
        if not name:
            messagebox.showwarning("Select Task", "Please select a task to delete.")
            return
        self.callbacks["delete_task"](name)
        self.update_tree()

    def _edit_task(self):
        name = self._selected_task_name()
        if not name:
            messagebox.showwarning("Select Task", "Please select a task to edit.")
            return
        self.callbacks["edit_task"](name)
        self.update_tree()

    def _filter_tasks(self):
        keyword = simpledialog.askstring("Filter Search", "Enter keyword or regex:")
        if not keyword:
            return
        try:
            import re
            pattern = re.compile(keyword, re.IGNORECASE)
        except Exception:
            messagebox.showerror("Invalid Pattern", "Invalid regular expression.")
            return
        tasks = [t for t in self.get_tasks() if pattern.search(t.name)]
        self.tree.delete(*self.tree.get_children())
        for t in tasks:
            status = "Completed" if getattr(t, "completed", False) else "Pending"
            tag = "completed" if getattr(t, "completed", False) else ("overdue" if getattr(t, "is_overdue") and t.is_overdue() else "")
            self.tree.insert("", "end", values=(t.name, t.deadline, t.time_str, t.priority, status), tags=(tag,))
        self.tree.tag_configure("overdue", background="tomato")
        self.tree.tag_configure("completed", background="lightgreen")

    def _export_calendar(self):
        self.callbacks["export_calendar"]()

if __name__ == "__main__":
    from task_model import Task
    root = tk.Tk()
    tasks = [Task("A", "2099-01-01", "09:00", "Low")]
    def get_tasks(): return tasks
    def set_tasks(t):
        nonlocal tasks
        tasks = t
    def dummy_mark(name): print("mark", name)
    def dummy_delete(name): print("del", name)
    def dummy_edit(name): print("edit", name)
    def dummy_export(): print("export")
    callbacks = {"mark_complete": dummy_mark, "delete_task": dummy_delete, "edit_task": dummy_edit, "export_calendar": dummy_export}
    panel = ListPanel(root, get_tasks, set_tasks, callbacks)
    panel.update_tree()
    root.mainloop()