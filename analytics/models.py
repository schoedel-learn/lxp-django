"""
Analytics models for the LXP platform.

Implements:
- ClickHouse integration configuration
- Metrics definitions
- Dashboard configurations
"""

import uuid
from django.conf import settings
from django.db import models


class AnalyticsConnection(models.Model):
    """
    Configuration for connecting to ClickHouse or other analytics backends.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Connection type
    backend_type = models.CharField(
        max_length=20,
        choices=[
            ('clickhouse', 'ClickHouse'),
            ('postgresql', 'PostgreSQL'),
        ],
        default='clickhouse'
    )
    
    # Connection details
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField(default=8123)
    database = models.CharField(max_length=100)
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=255, blank=True)
    
    # SSL settings
    use_ssl = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_connected_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'analytics connection'
        verbose_name_plural = 'analytics connections'
    
    def __str__(self):
        return f'{self.name} ({self.backend_type})'


class MetricDefinition(models.Model):
    """
    Defines a metric that can be calculated and displayed.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Metric category
    category = models.CharField(
        max_length=30,
        choices=[
            ('engagement', 'Engagement'),
            ('participation', 'Participation'),
            ('learning', 'Learning Outcomes'),
            ('social', 'Social'),
            ('ai', 'AI Usage'),
            ('system', 'System'),
        ],
        default='engagement'
    )
    
    # Value type
    value_type = models.CharField(
        max_length=20,
        choices=[
            ('count', 'Count'),
            ('percentage', 'Percentage'),
            ('duration', 'Duration'),
            ('score', 'Score'),
            ('rate', 'Rate'),
        ],
        default='count'
    )
    
    # Aggregation
    aggregation = models.CharField(
        max_length=20,
        choices=[
            ('sum', 'Sum'),
            ('avg', 'Average'),
            ('min', 'Minimum'),
            ('max', 'Maximum'),
            ('count', 'Count'),
            ('count_distinct', 'Count Distinct'),
        ],
        default='count'
    )
    
    # Query template (for ClickHouse)
    query_template = models.TextField(
        blank=True,
        help_text='SQL query template with placeholders'
    )
    
    # Scope
    scopes = models.JSONField(
        default=list,
        help_text='Available scopes: platform, community, group, user, activity, path'
    )
    
    # Time dimensions
    supports_time_series = models.BooleanField(default=True)
    default_time_range = models.CharField(
        max_length=20,
        choices=[
            ('day', 'Day'),
            ('week', 'Week'),
            ('month', 'Month'),
            ('quarter', 'Quarter'),
            ('year', 'Year'),
        ],
        default='week'
    )
    
    # Display settings
    format_string = models.CharField(
        max_length=50,
        blank=True,
        help_text='Python format string for display'
    )
    unit = models.CharField(max_length=20, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'metric definition'
        verbose_name_plural = 'metric definitions'
        ordering = ['category', 'display_name']
    
    def __str__(self):
        return self.display_name


class Dashboard(models.Model):
    """
    A dashboard containing multiple widgets/metrics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    # Dashboard type
    dashboard_type = models.CharField(
        max_length=30,
        choices=[
            ('learner', 'Learner Dashboard'),
            ('facilitator', 'Facilitator Dashboard'),
            ('admin', 'Admin Dashboard'),
            ('community', 'Community Dashboard'),
            ('custom', 'Custom Dashboard'),
        ],
        default='custom'
    )
    
    # Scope
    community = models.ForeignKey(
        'communities.Community',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='dashboards'
    )
    
    # Layout configuration
    layout = models.JSONField(
        default=dict,
        help_text='Grid layout configuration for widgets'
    )
    
    # Access control
    is_public = models.BooleanField(default=False)
    allowed_roles = models.JSONField(
        default=list,
        help_text='Roles that can view this dashboard'
    )
    
    # Ownership
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='dashboards_created'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'dashboard'
        verbose_name_plural = 'dashboards'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DashboardWidget(models.Model):
    """
    A widget on a dashboard displaying a metric or visualization.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name='widgets'
    )
    
    title = models.CharField(max_length=100)
    
    # Widget type
    widget_type = models.CharField(
        max_length=30,
        choices=[
            ('metric', 'Single Metric'),
            ('line_chart', 'Line Chart'),
            ('bar_chart', 'Bar Chart'),
            ('pie_chart', 'Pie Chart'),
            ('table', 'Table'),
            ('leaderboard', 'Leaderboard'),
            ('progress', 'Progress Indicator'),
            ('activity_feed', 'Activity Feed'),
        ],
        default='metric'
    )
    
    # Metric(s) to display
    metrics = models.ManyToManyField(
        MetricDefinition,
        related_name='widgets',
        blank=True
    )
    
    # Configuration
    config = models.JSONField(
        default=dict,
        help_text='Widget-specific configuration'
    )
    
    # Position in grid
    position_x = models.PositiveSmallIntegerField(default=0)
    position_y = models.PositiveSmallIntegerField(default=0)
    width = models.PositiveSmallIntegerField(default=1)
    height = models.PositiveSmallIntegerField(default=1)
    
    # Refresh settings
    refresh_interval_seconds = models.PositiveIntegerField(
        default=0,
        help_text='Auto-refresh interval (0 = no auto-refresh)'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'dashboard widget'
        verbose_name_plural = 'dashboard widgets'
        ordering = ['position_y', 'position_x']
    
    def __str__(self):
        return f'{self.dashboard.name} - {self.title}'


class ExportedReport(models.Model):
    """
    Tracks exported analytics reports.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Report type
    report_type = models.CharField(
        max_length=30,
        choices=[
            ('dashboard_snapshot', 'Dashboard Snapshot'),
            ('custom_query', 'Custom Query'),
            ('scheduled_report', 'Scheduled Report'),
        ],
        default='dashboard_snapshot'
    )
    
    # Source
    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exports'
    )
    query = models.TextField(blank=True)
    
    # Output
    format = models.CharField(
        max_length=10,
        choices=[
            ('csv', 'CSV'),
            ('xlsx', 'Excel'),
            ('pdf', 'PDF'),
            ('json', 'JSON'),
        ],
        default='csv'
    )
    file_key = models.CharField(
        max_length=500,
        blank=True,
        help_text='MinIO object key for the exported file'
    )
    file_size = models.PositiveIntegerField(null=True, blank=True)
    
    # Scope
    community = models.ForeignKey(
        'communities.Community',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exported_reports'
    )
    time_range_start = models.DateTimeField(null=True, blank=True)
    time_range_end = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True)
    
    # Ownership
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reports_exported'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the exported file will be deleted'
    )
    
    class Meta:
        verbose_name = 'exported report'
        verbose_name_plural = 'exported reports'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class ETLJob(models.Model):
    """
    Tracks ETL jobs from LRS to ClickHouse.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Job type
    job_type = models.CharField(
        max_length=30,
        choices=[
            ('lrs_to_clickhouse', 'LRS to ClickHouse'),
            ('aggregate_metrics', 'Aggregate Metrics'),
            ('custom', 'Custom ETL'),
        ],
        default='lrs_to_clickhouse'
    )
    
    # Schedule (cron expression)
    schedule = models.CharField(
        max_length=100,
        blank=True,
        help_text='Cron expression for scheduled runs'
    )
    
    # Configuration
    config = models.JSONField(default=dict, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Last run info
    last_run_at = models.DateTimeField(null=True, blank=True)
    last_run_status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('partial', 'Partial'),
        ],
        null=True,
        blank=True
    )
    last_run_records = models.PositiveIntegerField(null=True, blank=True)
    last_run_error = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'ETL job'
        verbose_name_plural = 'ETL jobs'
        ordering = ['name']
    
    def __str__(self):
        return self.name

