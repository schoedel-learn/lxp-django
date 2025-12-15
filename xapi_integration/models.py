"""
xAPI Integration models for the LXP platform.

Implements:
- xAPI vocabulary definitions
- Statement builders
- LRS configuration
- cmi5 package management
"""

import uuid
from django.conf import settings
from django.db import models


class LRSConfiguration(models.Model):
    """
    Configuration for connecting to a Learning Record Store.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # LRS endpoint
    endpoint = models.URLField(max_length=500)
    
    # Authentication
    auth_type = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic Auth'),
            ('oauth', 'OAuth 2.0'),
        ],
        default='basic'
    )
    username = models.CharField(max_length=255, blank=True)
    # Password should be stored encrypted - consider using django-encrypted-model-fields
    password = models.CharField(max_length=255, blank=True)
    
    # OAuth settings
    oauth_client_id = models.CharField(max_length=255, blank=True)
    oauth_client_secret = models.CharField(max_length=255, blank=True)
    oauth_token_url = models.URLField(max_length=500, blank=True)
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    # xAPI version
    xapi_version = models.CharField(max_length=10, default='1.0.3')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'LRS configuration'
        verbose_name_plural = 'LRS configurations'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Ensure only one default LRS
        if self.is_default:
            LRSConfiguration.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class XAPIVerb(models.Model):
    """
    Custom xAPI verb definitions for the platform.
    """
    id = models.CharField(
        max_length=500,
        primary_key=True,
        help_text='Full IRI of the verb'
    )
    
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Language mappings for display
    display_names = models.JSONField(
        default=dict,
        help_text='Language-tagged display names {"en": "completed", "es": "completado"}'
    )
    
    # Categorization
    category = models.CharField(
        max_length=50,
        choices=[
            ('learning', 'Learning Activities'),
            ('social', 'Social Actions'),
            ('assessment', 'Assessment'),
            ('ai', 'AI Interactions'),
            ('system', 'System Events'),
        ],
        default='learning'
    )
    
    # Whether this is a standard ADL verb or custom
    is_custom = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'xAPI verb'
        verbose_name_plural = 'xAPI verbs'
        ordering = ['category', 'display_name']
    
    def __str__(self):
        return f'{self.display_name} ({self.id})'


class XAPIActivityType(models.Model):
    """
    Activity type definitions for xAPI statements.
    """
    id = models.CharField(
        max_length=500,
        primary_key=True,
        help_text='Full IRI of the activity type'
    )
    
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Category
    category = models.CharField(
        max_length=50,
        choices=[
            ('content', 'Content'),
            ('assessment', 'Assessment'),
            ('social', 'Social'),
            ('community', 'Community'),
            ('path', 'Learning Path'),
        ],
        default='content'
    )
    
    is_custom = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'xAPI activity type'
        verbose_name_plural = 'xAPI activity types'
        ordering = ['category', 'display_name']
    
    def __str__(self):
        return f'{self.display_name} ({self.id})'


class CMI5Package(models.Model):
    """
    A cmi5 content package imported into the platform.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Package info
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Storage location in MinIO
    package_key = models.CharField(
        max_length=500,
        help_text='Object key in MinIO for the package ZIP'
    )
    
    # Extracted package structure
    course_structure = models.JSONField(
        default=dict,
        help_text='Parsed cmi5.xml course structure'
    )
    
    # Publisher info from cmi5.xml
    publisher_id = models.CharField(max_length=255, blank=True)
    publisher_name = models.CharField(max_length=255, blank=True)
    
    # Version
    version = models.CharField(max_length=50, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('uploading', 'Uploading'),
            ('processing', 'Processing'),
            ('ready', 'Ready'),
            ('error', 'Error'),
        ],
        default='uploading'
    )
    error_message = models.TextField(blank=True)
    
    # Ownership
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='cmi5_packages_uploaded'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'cmi5 package'
        verbose_name_plural = 'cmi5 packages'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class CMI5AssignableUnit(models.Model):
    """
    An Assignable Unit (AU) within a cmi5 package.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Parent package
    package = models.ForeignKey(
        CMI5Package,
        on_delete=models.CASCADE,
        related_name='assignable_units'
    )
    
    # AU info from cmi5.xml
    au_id = models.CharField(
        max_length=255,
        help_text='AU ID from cmi5.xml'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Launch info
    launch_url = models.URLField(max_length=500)
    launch_method = models.CharField(
        max_length=20,
        choices=[
            ('OwnWindow', 'Own Window'),
            ('AnyWindow', 'Any Window'),
        ],
        default='AnyWindow'
    )
    
    # Move on criteria
    move_on = models.CharField(
        max_length=20,
        choices=[
            ('Passed', 'Passed'),
            ('Completed', 'Completed'),
            ('CompletedAndPassed', 'Completed and Passed'),
            ('CompletedOrPassed', 'Completed or Passed'),
            ('NotApplicable', 'Not Applicable'),
        ],
        default='CompletedOrPassed'
    )
    
    # Mastery score
    mastery_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Ordering within package
    order = models.PositiveIntegerField(default=0)
    
    # Link to platform activity
    activity = models.OneToOneField(
        'content.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cmi5_au'
    )
    
    class Meta:
        verbose_name = 'cmi5 assignable unit'
        verbose_name_plural = 'cmi5 assignable units'
        unique_together = ['package', 'au_id']
        ordering = ['order']
    
    def __str__(self):
        return f'{self.package.title} - {self.title}'


class CMI5Session(models.Model):
    """
    A cmi5 launch session for tracking AU launches.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # What and who
    assignable_unit = models.ForeignKey(
        CMI5AssignableUnit,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cmi5_sessions'
    )
    
    # Registration (links to enrollment/attempt)
    registration = models.UUIDField(db_index=True)
    
    # Session state
    state = models.CharField(
        max_length=20,
        choices=[
            ('initialized', 'Initialized'),
            ('launched', 'Launched'),
            ('completed', 'Completed'),
            ('abandoned', 'Abandoned'),
            ('waived', 'Waived'),
            ('terminated', 'Terminated'),
        ],
        default='initialized'
    )
    
    # Results
    is_passed = models.BooleanField(null=True, blank=True)
    is_completed = models.BooleanField(null=True, blank=True)
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Timing
    launched_at = models.DateTimeField(null=True, blank=True)
    terminated_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    # Launch token (for security)
    launch_token = models.CharField(max_length=255, unique=True)
    token_expires_at = models.DateTimeField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'cmi5 session'
        verbose_name_plural = 'cmi5 sessions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.email} - {self.assignable_unit.title}'


class StatementQueue(models.Model):
    """
    Queue for xAPI statements to be sent to the LRS.
    Used for reliability and retry logic.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Statement data
    statement = models.JSONField(help_text='Full xAPI statement JSON')
    
    # Target LRS
    lrs = models.ForeignKey(
        LRSConfiguration,
        on_delete=models.CASCADE,
        related_name='queued_statements'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('sent', 'Sent'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    
    # Retry info
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=5)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    next_attempt_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Response from LRS
    lrs_statement_id = models.UUIDField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'statement queue'
        verbose_name_plural = 'statement queue'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['status', 'next_attempt_at']),
        ]
    
    def __str__(self):
        return f'Statement {self.id} ({self.status})'

