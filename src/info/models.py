from tortoise import models, fields


class UserStatistic(models.Model):
    id = fields.IntField(pk=True)
    users = fields.IntField()
    new_subscribed = fields.IntField()
    cancel_subscribed = fields.IntField()
    date = fields.DateField(unique=True)


class FileStatistic(models.Model):
    id = fields.IntField(pk=True)
    files_count = fields.IntField()
    downloads = fields.IntField()
    date = fields.DateField(unique=True)


class StorageStatistic(models.Model):
    id = fields.IntField(pk=True)
    fill = fields.IntField()
    date = fields.DateField(unique=True)


class PayStatistic(models.Model):
    id = fields.IntField(pk=True)
    year_count = fields.IntField()
    month_count = fields.IntField()
    week_count = fields.IntField()
    date = fields.DateField(unique=True)