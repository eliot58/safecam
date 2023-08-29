from enum import Enum
from fastapi_users_tortoise import TortoiseBaseUserAccountModel, TortoiseBaseUserOAuthAccountModel
from tortoise import fields, models

class Status(Enum):
    premium = "premium"
    ambassador = "ambassador"

class User(TortoiseBaseUserAccountModel):
    name = fields.CharField(max_length=80)
    phone = fields.CharField(max_length=20, null=True)
    registered_at = fields.DatetimeField(auto_now_add=True)
    expiration_date = fields.DatetimeField(null=True)
    otp = fields.IntField(null=True)
    auto_upload = fields.BooleanField(default=False)
    date_of_send_otp = fields.DatetimeField(null=True)
    downloads = fields.IntField(default=0)
    storage = fields.BigIntField(default=0)
    last_upload = fields.DatetimeField(null=True)
    tarif = fields.OneToOneField("models.Tarif", on_delete=fields.CASCADE, null=True)
    is_unlock = fields.BooleanField(default=False)
    status = fields.CharEnumField(enum_type=Status, null=True)



class ChangeStatus(models.Model):
    old_status = fields.CharEnumField(enum_type=Status)
    new_status = fields.CharEnumField(enum_type=Status)
    cause = fields.TextField()
    user = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE)




class OAuthAccount(TortoiseBaseUserOAuthAccountModel):
    pass

