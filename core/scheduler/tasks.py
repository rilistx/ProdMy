from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler_di import ContextSchedulerDecorator
# from core.handlers.play import play_scheduler


# Time Tasks
def scheduler_tasks():
    redis = {
        'default': RedisJobStore(
            jobs_key='dispatched_trips_jobs',
            run_times_key='dispatched_trips_running',
            host='localhost',
            db=2,
            port=6379
        )
    }

    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone="Europe/Kiev", jobstores=redis))

    # scheduler.add_job(play_scheduler, trigger='cron', minute='*', kwargs={'bot': bot})
    # scheduler.add_job(play_scheduler, trigger='cron', minute='*', kwargs={'bot': bot})

    return scheduler
