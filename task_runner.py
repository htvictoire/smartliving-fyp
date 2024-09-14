

import time
import threading
from energy.tasks import energy_consumption_control, reset_today_limit






def run_periodic_task():
    while True:
        reset_today_limit()
        energy_consumption_control() 
        time.sleep(120)  

def start_periodic_task():
    # Create a separate thread to run the task
    task_thread = threading.Thread(target=run_periodic_task)
    task_thread.daemon = True  # This allows the thread to exit when the main program does
    task_thread.start()
