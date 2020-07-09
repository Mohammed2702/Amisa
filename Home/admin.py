from django.contrib import admin
from . import models
from Amisacb import settings


admin.site.register(models.Profile)
admin.site.register(models.History)
admin.site.register(models.Post)

if settings.DEBUG:
	admin.site.register(models.Network)
	admin.site.register(models.Code)
	admin.site.register(models.CodeGroup)
	admin.site.register(models.Order)
	admin.site.register(models.Wallet)
	admin.site.register(models.SiteSetting)
	admin.site.register(models.PasswordReset)
