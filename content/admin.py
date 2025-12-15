"""
Admin configuration for the content app.
"""
from django.contrib import admin

from .models import (
    Activity, LearningPath, PathActivity, CommunityPath,
    Enrollment, ActivityProgress
)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    """Admin configuration for activities."""
    
    list_display = ('title', 'activity_type', 'is_published', 'estimated_minutes', 'created_at')
    list_filter = ('activity_type', 'is_published', 'content_type')
    search_fields = ('title', 'slug', 'description')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('created_by',)
    filter_horizontal = ('prerequisites',)


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    """Admin configuration for learning paths."""
    
    list_display = ('title', 'is_sequential', 'is_published', 'activity_count', 'created_at')
    list_filter = ('is_published', 'is_sequential')
    search_fields = ('title', 'slug', 'description')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('created_by',)
    filter_horizontal = ('prerequisites',)


@admin.register(PathActivity)
class PathActivityAdmin(admin.ModelAdmin):
    """Admin configuration for path activities."""
    
    list_display = ('path', 'activity', 'order', 'section_title', 'is_required')
    list_filter = ('is_required',)
    search_fields = ('path__title', 'activity__title')
    raw_id_fields = ('path', 'activity')
    ordering = ('path', 'section_order', 'order')


@admin.register(CommunityPath)
class CommunityPathAdmin(admin.ModelAdmin):
    """Admin configuration for community paths."""
    
    list_display = ('community', 'path', 'is_featured', 'is_required', 'added_at')
    list_filter = ('is_featured', 'is_required')
    search_fields = ('community__name', 'path__title')
    raw_id_fields = ('community', 'path', 'added_by')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Admin configuration for enrollments."""
    
    list_display = ('user', 'path', 'community', 'progress_percent', 'enrolled_at', 'completed_at')
    list_filter = ('enrolled_at', 'completed_at')
    search_fields = ('user__email', 'path__title', 'community__name')
    raw_id_fields = ('user', 'path', 'community')


@admin.register(ActivityProgress)
class ActivityProgressAdmin(admin.ModelAdmin):
    """Admin configuration for activity progress."""
    
    list_display = ('user', 'activity', 'status', 'total_time_seconds', 'last_accessed_at')
    list_filter = ('status',)
    search_fields = ('user__email', 'activity__title')
    raw_id_fields = ('user', 'activity', 'enrollment')

