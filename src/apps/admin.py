from django.contrib import admin

# Register your models here.
from .models import App, AppEnvVariable, AppSecretVariable, AppVariableChoices


class AppEnvVariableAdmin(admin.TabularInline):
    model = AppEnvVariable
    fields = ["user", "key", "value", "value_encoded"]
    raw_id_fields = ["user"]
    readonly_fields = ["value_encoded"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(type=AppVariableChoices.ENV)


class AppSecretVariableAdmin(admin.TabularInline):
    model = AppSecretVariable
    fields = ["user", "key", "value", "value_encoded"]
    raw_id_fields = ["user"]
    readonly_fields = ["value_encoded"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(type=AppVariableChoices.SECRET)


class AppAdmin(admin.ModelAdmin):
    inlines = [AppEnvVariableAdmin, AppSecretVariableAdmin]
    list_display = ["__str__", "project", "user", "container"]
    list_filter = ["updated", "timestamp"]
    search_fields = [
        "user__username",
        "container",
        "user__email",
        "project__id",
        "project__label",
    ]
    raw_id_fields = ["user", "project"]

    class Meta:
        model = App


admin.site.register(App, AppAdmin)
