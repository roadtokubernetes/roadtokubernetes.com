from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin as OriginalGroupAdmin
from django.contrib.auth.admin import UserAdmin as OriginalUserAdmin
from django.contrib.auth.models import Group
from rangefilter.filter import DateRangeFilter

from .models import Profile

User = get_user_model()

admin.site.unregister(Group)
admin.site.unregister(User)


class ProfileInline(admin.StackedInline):
    model = Profile
    fields = ["image", "title", "description"]
    verbose_name_plural = "Profile"


class UserAdmin(OriginalUserAdmin):
    inlines = [
        ProfileInline,
    ]
    list_display = [
        "username",
        # "display_photo",
        "email",
        "first_name",
        "last_name",
        "date_joined",
    ]
    list_filter = [
        ("date_joined", DateRangeFilter),
        "date_joined",
        "is_active",
        "is_staff",
    ]
    readonly_fields = [
        "date_joined",
        "last_login",
    ]
    exclude = []
    ordering = ["-date_joined"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "profile",
            )
        )


admin.site.register(User, UserAdmin)


class GroupAdmin(OriginalGroupAdmin):
    list_display = ["__str__", "user_count"]

    def user_count(self, obj):
        return obj.user_set.count()


admin.site.register(Group, GroupAdmin)
