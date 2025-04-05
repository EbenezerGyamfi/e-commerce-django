from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from accounts.models import Account, UserProfile


# make password readonly on admin edit page


class AccountAdmin(UserAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "username",
        "last_login",
        "is_active",
        "date_joined",
    )
    list_display_links = ("email", "first_name", "last_name")
    readonly_fields = ("last_login", "date_joined")
    ordering = ("-date_joined",)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    
    
class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        return format_html(
            '<img src="%s" style="width: 40px; height: 40px; border-radius: 50%%;" />'
            % (obj.profile_picture.url)
        )
    thumbnail.short_description = "Profile Picture"
    
    list_display = (
        "user",
        "city",
        "state",
        "thumbnail",
        "country"
    )


# Register your models here.
admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)