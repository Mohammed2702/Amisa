from django.contrib import admin
from . import models


class ProfileAdmin(admin.ModelAdmin):
	list_display = ('reference_id', 'state', 'phone_number')
	list_filter = ['date_joined']
	list_per_page = 10
	search_fields = ['reference_id', 'state', 'phone_number']

	fieldsets = [
		('Account Details', {'fields': ['reference_id']}),
		('Contact Details', {'fields': ['state', 'phone_number']})
	]

class LocatorAdmin(admin.ModelAdmin):
	list_display = ('location', 'information', 'date', 'last_updated')
	list_filter = ['date', 'last_updated']
	list_per_page = 10
	search_fields = ['location', 'information', 'date', 'last_updated']

	fieldsets = [
		('Location', {'fields': ['location']}),
		('Details', {'fields': ['information']})
	]



admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.Locator, LocatorAdmin)
admin.site.register(models.Code)
admin.site.register(models.CodeGroup)
admin.site.register(models.Wallet)
admin.site.register(models.SiteSetting)
