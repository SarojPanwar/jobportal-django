from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Application, Job, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "company", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser")
    fieldsets = UserAdmin.fieldsets + (
        ("Job Portal Info", {"fields": ("role", "company")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Job Portal Info", {"fields": ("role", "company", "email")}),
    )


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "category", "job_type", "is_active", "created_at")
    list_filter = ("category", "job_type", "is_active")
    search_fields = ("title", "company", "location", "description")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("job", "seeker", "status", "applied_at")
    list_filter = ("status",)
