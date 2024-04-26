from time import sleep

from celery import shared_task


@shared_task
def get_metar(station: str) -> str:
    sleep(5)
    return "Wind is high"
