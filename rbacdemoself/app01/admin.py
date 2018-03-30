from django.contrib import admin
from app01 import models

admin.site.register(models.UserInfo)
admin.site.register(models.Order)
