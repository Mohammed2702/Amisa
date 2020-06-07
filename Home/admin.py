from django.contrib import admin
from . import models


admin.site.register(models.Profile)
admin.site.register(models.CodeGroup)
admin.site.register(models.Code)
admin.site.register(models.Wallet)
admin.site.register(models.History)
admin.site.register(models.Order)
admin.site.register(models.Post)
