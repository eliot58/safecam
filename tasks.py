from celery import Celery
from tortoise import Tortoise, run_async
from src.config.settings import APPS_MODELS, BROKER, DATABASE_URI
from src.auth.models import User
from src.file.models import File
from src.info.models import StorageStatistic, FileStatistic, UserStatistic
from src.config.settings import aws_access_key_id, aws_secret_access_key, bucket
import boto3
from botocore.client import Config
from datetime import datetime, timedelta
from tortoise.functions import Sum



app = Celery('tasks', broker=BROKER)

async def files_delete():
    await Tortoise.init(
        db_url=DATABASE_URI,
        modules={"models": APPS_MODELS},
    )

    s3 = boto3.client(
        's3',
        endpoint_url='https://s3.timeweb.com',
        region_name='ru-1',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        config=Config(s3={'addressing_style': 'path'})
    )

    files = await File.filter(is_cart=True)
    for file in files:
        if file.cart_date + timedelta(days=3) <= datetime.utcnow().date():
            s3.delete_object(Bucket=bucket['Name'], Key=file.path)
            await file.delete()


async def statistic_create():
    await Tortoise.init(
        db_url=DATABASE_URI,
        modules={"models": APPS_MODELS},
    )

    files = await File.get(cart_date="2023-06-11")

    print(files)


    

    

    








run_async(statistic_create())
    



# @app.task
# def delete():
#     run_async(files_delete())



# app.conf.beat_schedule = {
#     'delete-every-day': {
#         'task': 'tasks.delete',
#         'schedule': 500
#     }
# }