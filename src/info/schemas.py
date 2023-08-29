from pydantic import BaseModel
from datetime import date

class UserStatistics(BaseModel):
    users: int
    new_subscribed: int
    cancel_subscribed: int
    date: date


class FileStatistics(BaseModel):
    files_count: int
    downloads: int
    date: date


class StorageStatistics(BaseModel):
    fill: int
    date: date

class PayStatistics(BaseModel):
    year_count: int
    month_count: int
    week_count: int
    date: date