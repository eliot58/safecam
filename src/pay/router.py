from fastapi import APIRouter, Depends, HTTPException
from src.auth.models import User
from src.config.settings import SECRET_AUTH
from datetime import datetime, timedelta
# from src.pay.schemas import Pay
from src.pay.models import Tarif, Tarif_Pydantic
from src.auth.config import current_user


router = APIRouter(
    tags=["pay"]
)
# @router.post("/paid")
# async def paid(pay: Pay):
#     if SECRET_AUTH != pay.key:
#         raise HTTPException(status_code=403, detail="")
#     user = await User.filter(email=pay.email).update(is_payed=True, expiration_date=datetime.now() + timedelta(days=pay.expiration), status = pay.status)
#     return {"status": "success", "detail": "status changed", "data": user}

@router.get("/tarif")
async def tarif(user: User = Depends(current_user)):
    if user.is_superuser:
        return await Tarif.all()
    return await Tarif.filter(is_active=True)

@router.post("/create-tarif")
async def create_tarif(tarif: Tarif_Pydantic, user: User = Depends(current_user)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only available to admin")
    tarif = await Tarif.create(**tarif.dict())
    return {"status": "success", "detail": None, "data": tarif}


@router.put("/update-tarif/{id}")
async def update_tarif(id: int, tarif: Tarif_Pydantic, user: User = Depends(current_user)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only available to admin")
    await Tarif.filter(id=id).update(**tarif.dict())
    return {"status": "success", "detail": None, "data": tarif}

@router.post("/active-tarif/{id}")
async def active_tarif(id: int, is_active: bool, user: User = Depends(current_user)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only available to admin")
    await Tarif.filter(id=id).update(is_active = is_active)
    return {"status": "success", "detail": None}


@router.delete("/delete-tarif/{id}")
async def delete_tarif(id: int, user: User = Depends(current_user)):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only available to admin")
    deleted_count = await Tarif.filter(id=id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Tarif {id} not found")
    return {"status": "success", "detail": None}

@router.post("/cancel-pay")
async def cancel_pay(user: User = Depends(current_user)):
    user.status = None
    await user.save()
    return {"status": "success", "detail": None}