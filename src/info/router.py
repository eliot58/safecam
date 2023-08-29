from src.info.models import UserStatistic, FileStatistic, StorageStatistic, PayStatistic
from src.info.schemas import UserStatistics, FileStatistics, StorageStatistics, PayStatistics
from fastapi import APIRouter
from fastapi_pagination import Page, paginate
from datetime import date

router = APIRouter(
    tags=["info"]
)


@router.get("/user-statistics", tags=["info"], response_model=Page[UserStatistics])
async def user_statistics(from_date: date, to_date: date):
    return paginate(await UserStatistic.filter(date__range=[from_date, to_date]))


@router.get("/file-statistics", tags=["info"], response_model=Page[FileStatistics])
async def file_statistics(from_date: date, to_date: date):
    return paginate(await FileStatistic.filter(date__range=[from_date, to_date]))


@router.get("/storage-statistics", tags=["info"], response_model=Page[StorageStatistics])
async def storage_statistics(from_date: date, to_date: date):
    return paginate(await StorageStatistic.filter(date__range=[from_date, to_date]))

@router.get("/pay-statistics", tags=["info"], response_model=Page[PayStatistics])
async def pay_statistics(from_date: date, to_date: date):
    return paginate(await PayStatistic.filter(date__range=[from_date, to_date]))