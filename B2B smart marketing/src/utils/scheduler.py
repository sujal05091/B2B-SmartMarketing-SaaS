"""
Scheduler Module (Bonus Feature)

Implements scheduled task execution for automated lead discovery.

Features:
- Weekly/daily scheduling
- Cron-like scheduling
- Background execution
- Logging and monitoring
"""

import schedule
import time
from datetime import datetime
from typing import Callable, Optional
import threading
from src.utils.logger import LoggerMixin


class Scheduler(LoggerMixin):
    """
    Task scheduler for automated marketing campaigns.
    
    Features:
    - Periodic task execution
    - Background threading
    - Error handling
    - Schedule management
    """
    
    def __init__(self):
        """Initialize Scheduler."""
        self.setup_logging("Scheduler")
        self.running = False
        self.thread = None
        self.jobs = []
    
    def schedule_weekly(self, task: Callable, day: str = "monday", 
                       time_str: str = "09:00", *args, **kwargs):
        """
        Schedule a task to run weekly.
        
        Args:
            task: Function to execute
            day: Day of week (monday, tuesday, etc.)
            time_str: Time in HH:MM format
            *args: Arguments for task
            **kwargs: Keyword arguments for task
        """
        self.log_info(f"Scheduling weekly task on {day} at {time_str}")
        
        def job_wrapper():
            self.log_info(f"Executing scheduled task: {task.__name__}")
            try:
                task(*args, **kwargs)
                self.log_info(f"Task completed: {task.__name__}")
            except Exception as e:
                self.log_error(f"Task error: {e}", exc_info=True)
        
        # Schedule based on day
        day_methods = {
            'monday': schedule.every().monday,
            'tuesday': schedule.every().tuesday,
            'wednesday': schedule.every().wednesday,
            'thursday': schedule.every().thursday,
            'friday': schedule.every().friday,
            'saturday': schedule.every().saturday,
            'sunday': schedule.every().sunday
        }
        
        if day.lower() not in day_methods:
            raise ValueError(f"Invalid day: {day}")
        
        job = day_methods[day.lower()].at(time_str).do(job_wrapper)
        self.jobs.append(job)
        
        self.log_info(f"Task scheduled: {task.__name__} every {day} at {time_str}")
    
    def schedule_daily(self, task: Callable, time_str: str = "09:00", 
                      *args, **kwargs):
        """
        Schedule a task to run daily.
        
        Args:
            task: Function to execute
            time_str: Time in HH:MM format
            *args: Arguments for task
            **kwargs: Keyword arguments for task
        """
        self.log_info(f"Scheduling daily task at {time_str}")
        
        def job_wrapper():
            self.log_info(f"Executing scheduled task: {task.__name__}")
            try:
                task(*args, **kwargs)
                self.log_info(f"Task completed: {task.__name__}")
            except Exception as e:
                self.log_error(f"Task error: {e}", exc_info=True)
        
        job = schedule.every().day.at(time_str).do(job_wrapper)
        self.jobs.append(job)
        
        self.log_info(f"Task scheduled: {task.__name__} every day at {time_str}")
    
    def schedule_interval(self, task: Callable, minutes: int = 60,
                         *args, **kwargs):
        """
        Schedule a task to run at fixed intervals.
        
        Args:
            task: Function to execute
            minutes: Interval in minutes
            *args: Arguments for task
            **kwargs: Keyword arguments for task
        """
        self.log_info(f"Scheduling task every {minutes} minutes")
        
        def job_wrapper():
            self.log_info(f"Executing scheduled task: {task.__name__}")
            try:
                task(*args, **kwargs)
                self.log_info(f"Task completed: {task.__name__}")
            except Exception as e:
                self.log_error(f"Task error: {e}", exc_info=True)
        
        job = schedule.every(minutes).minutes.do(job_wrapper)
        self.jobs.append(job)
        
        self.log_info(f"Task scheduled: {task.__name__} every {minutes} minutes")
    
    def start(self, run_pending_immediately: bool = False):
        """
        Start the scheduler in a background thread.
        
        Args:
            run_pending_immediately: Run pending jobs immediately on start
        """
        if self.running:
            self.log_warning("Scheduler already running")
            return
        
        self.running = True
        
        if run_pending_immediately:
            schedule.run_all()
        
        def run_scheduler():
            self.log_info("Scheduler started")
            while self.running:
                schedule.run_pending()
                time.sleep(1)
            self.log_info("Scheduler stopped")
        
        self.thread = threading.Thread(target=run_scheduler, daemon=True)
        self.thread.start()
        
        self.log_info("Scheduler thread started")
    
    def stop(self):
        """Stop the scheduler."""
        self.log_info("Stopping scheduler...")
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=5)
        
        self.log_info("Scheduler stopped")
    
    def clear(self):
        """Clear all scheduled jobs."""
        schedule.clear()
        self.jobs = []
        self.log_info("All scheduled jobs cleared")
    
    def list_jobs(self) -> list:
        """
        List all scheduled jobs.
        
        Returns:
            List of job information
        """
        job_list = []
        for job in schedule.jobs:
            job_info = {
                'next_run': str(job.next_run),
                'interval': str(job.interval),
                'unit': job.unit,
                'job': str(job.job_func)
            }
            job_list.append(job_info)
        
        return job_list
    
    def print_jobs(self):
        """Print all scheduled jobs to console."""
        jobs = self.list_jobs()
        
        if not jobs:
            print("No scheduled jobs")
            return
        
        print("\n📅 Scheduled Jobs:")
        print("="*60)
        for i, job in enumerate(jobs, 1):
            print(f"{i}. Next run: {job['next_run']}")
            print(f"   Interval: {job['interval']} {job['unit']}")
            print(f"   Function: {job['job']}")
            print()


# Example usage
if __name__ == "__main__":
    def example_task(message):
        print(f"Task executed: {message}")
    
    scheduler = Scheduler()
    
    # Schedule weekly task
    scheduler.schedule_weekly(
        example_task,
        day="monday",
        time_str="09:00",
        message="Weekly lead discovery"
    )
    
    # Schedule daily task
    scheduler.schedule_daily(
        example_task,
        time_str="14:00",
        message="Daily report"
    )
    
    # Print jobs
    scheduler.print_jobs()
    
    # Start scheduler
    scheduler.start()
    
    # Keep running (in real use, this would be in a long-running process)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
