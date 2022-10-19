from django.contrib import admin

# Register your models here.
from .models import Project


class ProjectAdmin(admin.ModelAdmin):
    list_display = ['user', 'project_id', 'label']
    list_filter = ['active']
    search_fields = ['user__username', 'project_id', 'label']

admin.site.register(Project, ProjectAdmin)
