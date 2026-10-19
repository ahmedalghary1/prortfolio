from django.contrib import admin
from .models import Portfolio, Project


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "owner", "updated_at")
    search_fields = ("name", "slug", "owner__username")
    inlines = [ProjectInline]
