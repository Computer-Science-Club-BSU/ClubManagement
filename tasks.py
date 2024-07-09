from datetime import datetime
from tasks.minute import run_minute



def run_tasks():
    start = datetime.now().timestamp()
    mins = start // 60
    if mins % 1 == 0:
        run_minute()
    if mins % 5 == 1:
        pass
    


if __name__ == "__main__":
    run_tasks()