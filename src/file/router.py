from datetime import datetime
from pathlib import Path
import shutil
from typing import List
import uuid
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from src.info.models import StorageStatistic, FileStatistic
from src.file.models import File, File_Pydantic, PartsFile
from src.auth.models import User
from src.auth.config import current_user
from fastapi_pagination import paginate, LimitOffsetPage
from src.config.settings import aws_access_key_id, aws_secret_access_key, bucket, GOOGLE_MAP
import boto3
from botocore.client import Config
import cv2
from geopy.geocoders import GoogleV3
from tortoise.exceptions import DoesNotExist
from moviepy.editor import VideoFileClip, concatenate_videoclips


router = APIRouter(
    tags=["file"]
)

def save_upload_file(upload_file: UploadFile) -> Path:
    suffix = Path(upload_file.filename).suffix
    filename = uuid.uuid4()
    with open(f"media/{filename}{suffix}", "wb") as f:
        shutil.copyfileobj(upload_file.file, f)
        tmp_path = Path(f.name)
    return tmp_path

def video_concat(videos):
    final_clip = concatenate_videoclips(videos)
    filename = f"media/{uuid.uuid4()}.mp4"
    final_clip.write_videofile(filename)
    return filename

@router.post("/upload")
async def upload_files(files: List[UploadFile], latitude: float | None = None, longitude: float | None = None, background_upload: bool = False, user: User = Depends(current_user)):
    for file in files:
        if file.content_type not in ["image/jpeg", "image/png", "image/gif", "image/jpg", "video/mp4"]:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
    size = 0

    s3 = boto3.client(
        's3',
        endpoint_url='https://s3.timeweb.com',
        region_name='ru-1',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        config=Config(s3={'addressing_style': 'path'})
    )
    
    geolocator = GoogleV3(api_key=GOOGLE_MAP)

    if background_upload:
        for file in files:

            size = size + file.size
            
            filename = f"{str(uuid.uuid4()) + '.' + file.filename.split('.')[-1]}"

            address = None

            city = None

            try:
                location = geolocator.reverse(f"{latitude}, {longitude}", language="ru")
                address = location.address
                for components in location.raw["address_components"]:
                    if "locality" in components["types"]:
                        city = components["long_name"]
                        break
            except BaseException:
                pass

            if file.content_type == "video/mp4":
                video_name = str(save_upload_file(file))
                vidcap = cv2.VideoCapture(video_name)
                vidcap.set(cv2.CAP_PROP_POS_MSEC,round(0.5, 2)*1000)
                hasFrames,image = vidcap.read()
                thumbnail = str(uuid.uuid4())
                if hasFrames:
                    cv2.imwrite("media/" +  thumbnail + '.jpg', image)

                with open("media/" +  thumbnail + '.jpg', 'rb') as data:
                    s3.upload_fileobj(data, bucket['Name'], thumbnail + '.jpg')

                with open(video_name, 'rb') as data:
                    s3.upload_fileobj(data, bucket['Name'], filename)

                await File.create(path = filename, user_id = user.id, size = file.size, thumbnail = thumbnail + '.jpg', address = address, latitude = latitude, longitude = longitude, city = city, is_gallery = True)
            else:
                await File.create(path = filename, user_id = user.id, size = file.size, address = address, latitude = latitude, longitude = longitude, city = city, is_gallery = True)

                s3.upload_fileobj(file.file, bucket['Name'], filename)

            file.file.close()
    else:
    
        for file in files:

            size = size + file.size
            
            filename = f"{str(uuid.uuid4()) + '.' + file.filename.split('.')[-1]}"

            address = None

            city = None

            try:
                location = geolocator.reverse(f"{latitude}, {longitude}", language="ru")
                address = location.address
                for components in location.raw["address_components"]:
                    if "locality" in components["types"]:
                        city = components["long_name"]
                        break
            except BaseException:
                pass

            if file.content_type == "video/mp4":
                video_name = str(save_upload_file(file))
                vidcap = cv2.VideoCapture(video_name)
                vidcap.set(cv2.CAP_PROP_POS_MSEC,round(0.5, 2)*1000)
                hasFrames,image = vidcap.read()
                thumbnail = str(uuid.uuid4())
                if hasFrames:
                    cv2.imwrite("media/" +  thumbnail + '.jpg', image)

                with open("media/" +  thumbnail + '.jpg', 'rb') as data:
                    s3.upload_fileobj(data, bucket['Name'], thumbnail + '.jpg')

                with open(video_name, 'rb') as data:
                    s3.upload_fileobj(data, bucket['Name'], filename)

                await File.create(path = filename, user_id = user.id, size = file.size, thumbnail = thumbnail + '.jpg', address = address, latitude = latitude, longitude = longitude, city = city)
            else:
                await File.create(path = filename, user_id = user.id, size = file.size, address = address, latitude = latitude, longitude = longitude, city = city)

                s3.upload_fileobj(file.file, bucket['Name'], filename)

            file.file.close()

    user.last_upload = datetime.now()
    user.storage = user.storage + size
    await user.save()
    try:
        storage_stats = await StorageStatistic.get(date=datetime.utcnow().date().strftime("%Y-%m-%d"))
    except DoesNotExist:
        all_storage_stats = await StorageStatistic.all()
        if len(all_storage_stats) == 0:
            await StorageStatistic.create(fill=size, date=datetime.utcnow().date())
        else:
            await StorageStatistic.create(fill=all_storage_stats[-1].fill + size, date=datetime.utcnow().date())

    else:
        storage_stats.fill = storage_stats.fill + size
        await storage_stats.save()

    try:
        file_stats = await FileStatistic.get(date=datetime.utcnow().date().strftime("%Y-%m-%d"))
    except DoesNotExist:
        all_file_stats = await FileStatistic.all()
        if len(all_file_stats) == 0:
            await FileStatistic.create(files_count=len(files), downloads=0, date=datetime.utcnow().date())
        else:
            await FileStatistic.create(files_count=all_file_stats[-1].files_count + len(files), downloads=all_file_stats[-1].downloads, date=datetime.utcnow().date())
    else:
        file_stats.files_count = file_stats.files_count + len(files)
        await file_stats.save()

    return {"status": "success", "detail": None, "data": None}


@router.post("/set-description/{id}")
async def set_description(id: int, description: str, user: User = Depends(current_user)):
    file = await File.filter(id=id).first()
    try:
        if file.user_id != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
    except Exception:
        raise HTTPException(status_code=400, detail="Bad request")
    file.description = description
    await file.save()
    return {"status": "success", "detail": None, "data": None}


@router.get("/file-list")
async def file_list(user: User = Depends(current_user)) -> LimitOffsetPage[File_Pydantic]:
    return paginate(await File_Pydantic.from_queryset(File.filter(user_id=user.id).filter(is_cart=False).order_by("-id")))


@router.get("/get-file/{id}", response_model=File_Pydantic)
async def get_file(id: int, user: User = Depends(current_user)):
    file = await File.filter(id=id).first()
    try:
        if file.user_id != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
    except Exception:
        raise HTTPException(status_code=400, detail="Bad request")
    return file


@router.delete("/delete-files")
async def delete_files(files: List[int], user: User = Depends(current_user)):
    size = 0
    for id in files:
        file = await File.filter(id=id).first()
        try:
            if file.user_id != user.id:
                raise HTTPException(status_code=403, detail="Forbidden")
        except Exception:
            raise HTTPException(status_code=400, detail="Bad request")
        size = size + file.size
        await user.save()
        file.is_cart = True
        file.cart_date = datetime.utcnow().date()
        await file.save()

    user.storage = user.storage - size
    await user.save()

    try:
        storage_stats = await StorageStatistic.get(date=datetime.utcnow().date().strftime("%Y-%m-%d"))
    except DoesNotExist:
        all_storage_stats = await StorageStatistic.all()
        await StorageStatistic.create(fill=all_storage_stats[-1].fill - size, date=datetime.utcnow().date())
    else:
        storage_stats.fill = storage_stats.fill - size
        await storage_stats.save()


    try:
        file_stats = await FileStatistic.get(date=datetime.utcnow().date().strftime("%Y-%m-%d"))
    except DoesNotExist:
        all_file_stats = await FileStatistic.all()
        await StorageStatistic.create(files_count=all_file_stats[-1].files_count - len(files), downloads=all_file_stats[-1].downloads, date=datetime.utcnow().date())
    else:
        file_stats.files_count = file_stats.files_count - len(files)
        await file_stats.save()

    return {"status": "success", "detail": "files delete", "data": None}


@router.post("/downloads")
async def downloads(files: List[int], user: User = Depends(current_user)):
    user.downloads = user.downloads + len(files)
    await user.save()
    try:
        file_stats = await FileStatistic.get(date=datetime.utcnow().date().strftime("%Y-%m-%d"))
    except DoesNotExist:
        all_file_stats = await FileStatistic.all()
        if len(all_file_stats) == 0:
            await FileStatistic.create(files_count=0, downloads=len(files), date=datetime.utcnow().date())
        else:
            await FileStatistic.create(files_count=all_file_stats[-1].files_count, downloads=all_file_stats[-1].downloads + len(files), date=datetime.utcnow().date())
    
    file_stats.downloads += len(files)
    await file_stats.save()

    return {"status": "success", "detail": None, "data": None}


@router.post("/parts-upload")
async def parts_upload_files(file: UploadFile, uuid_name: uuid.UUID, latitude: float | None = None, longitude: float | None = None, is_loading: bool = False, user: User = Depends(current_user)):
    if file.content_type not in ["video/mp4"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
        

    s3 = boto3.client(
        's3',
        endpoint_url='https://s3.timeweb.com',
        region_name='ru-1',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        config=Config(s3={'addressing_style': 'path'})
    )
    
    geolocator = GoogleV3(api_key=GOOGLE_MAP)
    
    filename = f"{str(uuid.uuid4()) + '.' + file.filename.split('.')[-1]}"

    address = None

    city = None

    try:
        location = geolocator.reverse(f"{latitude}, {longitude}", language="ru")
        address = location.address
        for components in location.raw["address_components"]:
            if "locality" in components["types"]:
                city = components["long_name"]
                break
    except BaseException:
        pass

    user.last_upload = datetime.now()
    user.storage = user.storage + file.size
    await user.save()
    try:
        storage_stats = await StorageStatistic.get(date=datetime.utcnow().date().strftime("%Y-%m-%d"))
    except DoesNotExist:
        all_storage_stats = await StorageStatistic.all()
        if len(all_storage_stats) == 0:
            await StorageStatistic.create(fill=file.size, date=datetime.utcnow().date())
        else:
            await StorageStatistic.create(fill=all_storage_stats[-1].fill + file.size, date=datetime.utcnow().date())
    else:
        storage_stats.fill += file.size
        await storage_stats.save()

    video_name = str(save_upload_file(file))


    await PartsFile.create(path = f"{video_name}", uuid_field = uuid_name, size = file.size)


    if is_loading:
        vidcap = cv2.VideoCapture(video_name)
        vidcap.set(cv2.CAP_PROP_POS_MSEC,round(0.5, 2)*1000)
        hasFrames,image = vidcap.read()
        thumbnail = str(uuid.uuid4())
        if hasFrames:
            cv2.imwrite("media/" +  thumbnail + '.jpg', image)

        with open("media/" +  thumbnail + '.jpg', 'rb') as data:
            s3.upload_fileobj(data, bucket['Name'], thumbnail + '.jpg')

        parts_of_video = await PartsFile.filter(uuid_field=uuid_name)

        paths = []
        size = 0
        for part in parts_of_video:
            size = size + part.size
            paths.append(VideoFileClip(part.path))


        with open(video_concat(paths), 'rb') as data:
            s3.upload_fileobj(data, bucket['Name'], filename)

        await File.create(path = filename, user_id = user.id, size = size, thumbnail = thumbnail + '.jpg', address = address, latitude = latitude, longitude = longitude, city = city)


        try:
            file_stats = await FileStatistic.get(date=datetime.utcnow().date().strftime("%Y-%m-%d"))
        except DoesNotExist:
            all_file_stats = await FileStatistic.all()
            if len(all_file_stats) == 0:
                await FileStatistic.create(files_count=1, downloads=0, date=datetime.utcnow().date())
            else:
                await FileStatistic.create(files_count=all_file_stats[-1].files_count + 1, downloads=all_file_stats[-1].downloads, date=datetime.utcnow().date())
        else:
            file_stats.files_count += 1
            await file_stats.save()

    file.file.close()

    return {"status": "success", "detail": None, "data": None}