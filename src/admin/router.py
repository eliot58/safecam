from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import paginate, LimitOffsetPage
from src.file.models import File, File_Pydantic
from src.auth.models import User, ChangeStatus
from src.auth.schemas import UserRead
from .utils import Sort
from src.auth.config import current_user
from src.info.models import StorageStatistic, FileStatistic
from tortoise.exceptions import DoesNotExist
from src.admin.schemas import PydanticChangeStatus


router = APIRouter(
    tags=["admin"]
)


@router.get("/get-users", response_model=LimitOffsetPage[UserRead])
async def get_users(sort: Sort = Sort.BY_REGISTER_DATE, search: str | None = None, user: User = Depends(current_user)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only available to admin")
    if sort == Sort.BY_LATEST_DOWNLOADS:
        if search != None:
            return paginate(await User.filter(email__icontains=search).order_by("last_upload"))
        else:
            return paginate(await User.all().order_by("last_upload"))
    elif sort == Sort.BY_SPACE:
        if search != None:
            return paginate(await User.filter(email__icontains=search).order_by("storage"))
        else:
            return paginate(await User.all().order_by("storage"))
    elif sort == Sort.BY_NOTACTIVE:
        if search != None:
            return paginate(await User.filter(email__icontains=search).filter(is_unlock=True))
        else:
            return paginate(await User.filter(is_unlock=True))
    if search != None:
        return paginate(await User.filter(email__icontains=search).order_by("registered_at"))
    else:
        return paginate(await User.all().order_by("registered_at"))


@router.get("/get-files/{id}", response_model=LimitOffsetPage[File_Pydantic])
async def get_files(id: int, user: User = Depends(current_user)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only available to admin")
    return paginate(await File.filter(user_id=id).filter(is_cart=False).order_by("-id"))


@router.get("/get-gallery/{id}", response_model=LimitOffsetPage[File_Pydantic])
async def get_gallery(id: int, user: User = Depends(current_user)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only available to admin")
    return paginate(await File.filter(user_id=id).filter(is_cart=False).filter(is_gallery=True).order_by("-id"))


@router.get("/user-cart/{id}", response_model=LimitOffsetPage[File_Pydantic])
async def get_user_cart(id: int, user: User = Depends(current_user)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only available to admin")
    return paginate(await File.filter(user_id=id).filter(is_cart=True).order_by("-id"))


@router.delete("/destroy-files")
async def delete_files(files: List[int], user: User = Depends(current_user)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only available to admin")
    size = 0
    for id in files:
        file = await File.filter(id=id).first()
        size = size + file.size
        await user.save()
        file.is_cart = True
        file.cart_date = datetime.now().date()
        await file.save()

    user.storage = user.storage - size
    await user.save()

    try:
        storage_stats = await StorageStatistic.get(date=datetime.utcnow().date().strftime("%Y-%m-%d"))
    except DoesNotExist:
        all_storage_stats = await StorageStatistic.all()
        await StorageStatistic.create(fill=all_storage_stats[-1].fill - size, date=datetime.utcnow().date())
    
    storage_stats.fill -= size
    await storage_stats.save()


    try:
        file_stats = await FileStatistic.get(date=datetime.utcnow().date().strftime("%Y-%m-%d"))
    except DoesNotExist:
        all_file_stats = await FileStatistic.all()
        await StorageStatistic.create(files_count=all_file_stats[-1].files_count - len(files), downloads=all_file_stats[-1].downloads, date=datetime.utcnow().date())
    
    file_stats.files_count -= len(files)
    await file_stats.save()
    return {"status": "success", "detail": "files delete", "data": None}

@router.post("/change-status")
async def change_status(change_status: PydanticChangeStatus, user: User = Depends(current_user)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only available to admin")
    user = await User.get(id=change_status.user_id)
    user.status = change_status.new_status
    await user.save()
    status = await ChangeStatus.create(**change_status.dict())
    return {"status": "success", "detail": None, "data": status}