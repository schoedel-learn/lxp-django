"""
Admin configuration for the xapi_integration app.
"""
from django.contrib import admin

from .models import (
    LRSConfiguration, XAPIVerb, XAPIActivityType,
    CMI5Package, CMI5AssignableUnit, CMI5Session, StatementQueue
)


@admin.register(LRSConfiguration)
class LRSConfigurationAdmin(admin.ModelAdmin):
    """Admin configuration for LRS configurations."""
    
    list_display = ('name', 'endpoint', 'auth_type', 'is_active', 'is_default')
    list_filter = ('is_active', 'is_default', 'auth_type')
    search_fields = ('name', 'endpoint')


@admin.register(XAPIVerb)
class XAPIVerbAdmin(admin.ModelAdmin):
    """Admin configuration for xAPI verbs."""
    
    list_display = ('display_name', 'id', 'category', 'is_custom')
    list_filter = ('category', 'is_custom')
    search_fields = ('display_name', 'id')


@admin.register(XAPIActivityType)
class XAPIActivityTypeAdmin(admin.ModelAdmin):
    """Admin configuration for xAPI activity types."""
    
    list_display = ('display_name', 'id', 'category', 'is_custom')
    list_filter = ('category', 'is_custom')
    search_fields = ('display_name', 'id')


@admin.register(CMI5Package)
class CMI5PackageAdmin(admin.ModelAdmin):
    """Admin configuration for cmi5 packages."""
    
    list_display = ('title', 'publisher_name', 'version', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'publisher_name')
    raw_id_fields = ('uploaded_by',)


@admin.register(CMI5AssignableUnit)
class CMI5AssignableUnitAdmin(admin.ModelAdmin):
    """Admin configuration for cmi5 assignable units."""
    
    list_display = ('title', 'package', 'move_on', 'order')
    list_filter = ('move_on',)
    search_fields = ('title', 'package__title')
    raw_id_fields = ('package', 'activity')


@admin.register(CMI5Session)
class CMI5SessionAdmin(admin.ModelAdmin):
    """Admin configuration for cmi5 sessions."""
    
    list_display = ('user', 'assignable_unit', 'state', 'is_passed', 'is_completed', 'created_at')
    list_filter = ('state', 'is_passed', 'is_completed')
    search_fields = ('user__email', 'assignable_unit__title')
    raw_id_fields = ('user', 'assignable_unit')


@admin.register(StatementQueue)
class StatementQueueAdmin(admin.ModelAdmin):
    """Admin configuration for statement queue."""
    
    list_display = ('id', 'lrs', 'status', 'attempts', 'created_at', 'sent_at')
    list_filter = ('status', 'lrs')
    search_fields = ('id',)
    raw_id_fields = ('lrs',)

