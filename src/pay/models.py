from tortoise import models, fields
from tortoise.contrib.pydantic import pydantic_model_creator
from src.pay.schemas import Period


class Tarif(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=160)
    price = fields.IntField()
    period = fields.CharEnumField(enum_type=Period, max_length=10)
    period_amount = fields.IntField()
    is_active = fields.BooleanField(default=True)

Tarif_Pydantic = pydantic_model_creator(Tarif, name="Tarif", exclude_readonly=True)