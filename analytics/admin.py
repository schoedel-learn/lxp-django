"""
Admin configuration for the analytics app.
"""
from django.contrib import admin

from .models import (
    AnalyticsConnection, MetricDefinition, Dashboard,
    DashboardWidget, ExportedReport, ETLJob
)


@admin.register(AnalyticsConnection)
class AnalyticsConnectionAdmin(admin.ModelAdmin):
    """Admin configuration for analytics connections."""
    
    list_display = ('name', 'backend_type', 'host', 'database', 'is_active', 'is_default')
    list_filter = ('backend_type', 'is_active', 'is_default')
    search_fields = ('name', 'host', 'database')


@admin.register(MetricDefinition)
class MetricDefinitionAdmin(admin.ModelAdmin):
    """Admin configuration for metric definitions."""
    
    list_display = ('display_name', 'category', 'value_type', 'aggregation', 'is_active')
    list_filter = ('category', 'value_type', 'is_active')
    search_fields = ('name', 'display_name', 'description')


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    """Admin configuration for dashboards."""
    
    list_display = ('name', 'dashboard_type', 'community', 'is_public', 'is_active', 'created_at')
    list_filter = ('dashboard_type', 'is_public', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('community', 'created_by')


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    """Admin configuration for dashboard widgets."""
    
    list_display = ('title', 'dashboard', 'widget_type', 'position_x', 'position_y', 'is_active')
    list_filter = ('widget_type', 'is_active')
    search_fields = ('title', 'dashboard__name')
    raw_id_fields = ('dashboard',)
    filter_horizontal = ('metrics',)


@admin.register(ExportedReport)
class ExportedReportAdmin(admin.ModelAdmin):
    """Admin configuration for exported reports."""
    
    list_display = ('name', 'report_type', 'format', 'status', 'created_by', 'created_at')
    list_filter = ('report_type', 'format', 'status')
    search_fields = ('name', 'description')
    raw_id_fields = ('dashboard', 'community', 'created_by')


@admin.register(ETLJob)
class ETLJobAdmin(admin.ModelAdmin):
    """Admin configuration for ETL jobs."""
    
    list_display = ('name', 'job_type', 'schedule', 'is_active', 'last_run_at', 'last_run_status')
    list_filter = ('job_type', 'is_active', 'last_run_status')
    search_fields = ('name', 'description')

