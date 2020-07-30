from django.contrib import admin
from . import models


class ProfileAdmin(admin.ModelAdmin):
	# fields = ['reference_id', 'account_type', 'state', 'phone_number']
	list_display = ('reference_id', 'account_type', 'state', 'phone_number')
	list_filter = ['date_joined']
	list_per_page = 10
	search_fields = ['reference_id']

	fieldsets = [
		('Account Details', {'fields': ['reference_id', 'account_type']}),
		('Contact Details', {'fields': ['state', 'phone_number']})
	]


admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.History)
admin.site.register(models.Post)
admin.site.register(models.Network)
admin.site.register(models.Code)
admin.site.register(models.CodeGroup)
admin.site.register(models.Order)
admin.site.register(models.Wallet)
admin.site.register(models.SiteSetting)
admin.site.register(models.PasswordReset)
