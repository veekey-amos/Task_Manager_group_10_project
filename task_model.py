person 1:  from datetime import datetime, timedelta

class Task:
    def _init_(self, name, deadline, time_str, priority):
        self.name = name
        self.deadline = deadline
        self.time_str = time_str
        self.priority = priority
        self.completed = False
        self.notified = False

    def is_overdue(self):
        try:
            full_datetime = f"{self.deadline} {self.time_str}"
            return datetime.strptime(full_datetime, "%Y-%m-%d %H:%M") < datetime.now()
        except ValueError:
            return False

    def is_due_soon(self):
        try:
            full_datetime = f"{self.deadline} {self.time_str}"
            task_time = datetime.strptime(full_datetime, "%Y-%m-%d %H:%M")
            now = datetime.now()
            return now <= task_time <= now + timedelta(minutes=10)
        except ValueError:
            return False

if _name_ == "_main_":
    t = Task("Demo", datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M"), "Medium")
    print(t.name, t.deadline, t.time_str, t.priority)
    print("overdue:", t.is_overdue(), "due soon:", t.is_due_soon())