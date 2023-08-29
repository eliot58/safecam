from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

class File(models.Model):
    id = fields.IntField(pk=True)
    path = fields.CharField(max_length=200)
    description = fields.TextField(default="")
    upload_date = fields.DatetimeField(auto_now_add=True)
    is_cart = fields.BooleanField(default=False)
    cart_date = fields.DateField(null=True)
    size = fields.BigIntField()
    thumbnail = fields.CharField(max_length=100, null=True)
    address = fields.CharField(max_length=200, null=True)
    latitude = fields.FloatField(null=True)
    longitude = fields.FloatField(null=True)
    city = fields.CharField(max_length=100, null = True)
    is_gallery = fields.BooleanField(default=False)

    user = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE)


class PartsFile(models.Model):
    id = fields.IntField(pk=True)
    uuid_field = fields.UUIDField()
    path = fields.CharField(max_length=200)
    size = fields.BigIntField()


File_Pydantic = pydantic_model_creator(File, name="File")