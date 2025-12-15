"""
Content models for the LXP platform.

Implements:
- Activities (content viewing, discussion, reflection, assignment, quiz, project, peer activity)
- Learning paths (sequences of activities)
- Content references (MongoDB/MinIO pointers)
"""

import uuid
from django.conf import settings
from django.db import models


class ActivityType(models.TextChoices):
    """Types of learning activities."""
    CONTENT = 'content', 'Content Viewing'
    DISCUSSION = 'discussion', 'Discussion'
    REFLECTION = 'reflection', 'Reflection'
    ASSIGNMENT = 'assignment', 'Assignment'
    QUIZ = 'quiz', 'Quiz'
    PROJECT = 'project', 'Project'
    PEER = 'peer', 'Peer Activity'
    CMI5 = 'cmi5', 'cmi5 Package'


class ContentType(models.TextChoices):
    """Types of content storage."""
    MONGODB = 'mongodb', 'MongoDB Document'
    MINIO = 'minio', 'MinIO File'
    CMI5 = 'cmi5', 'cmi5 Package'
    EXTERNAL = 'external', 'External URL'


class Activity(models.Model):
    """
    A learning activity - the fundamental unit of learning in the LXP.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic info
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    
    # Classification
    activity_type = models.CharField(
        max_length=20,
        choices=ActivityType.choices,
        default=ActivityType.CONTENT
    )
    
    # Content reference
    content_type = models.CharField(
        max_length=20,
        choices=ContentType.choices,
        default=ContentType.MONGODB
    )
    # For MongoDB: document ID; For MinIO: object key; For cmi5: package ID
    content_ref = models.CharField(max_length=500, blank=True)
    
    # Learning metadata
    estimated_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Estimated time to complete in minutes'
    )
    outcomes = models.JSONField(
        default=list,
        blank=True,
        help_text='Learning outcomes for this activity'
    )
    prerequisites = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='unlocks'
    )
    
    # Visibility and access
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Versioning
    version = models.PositiveIntegerField(default=1)
    
    # Ownership
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='activities_created'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional metadata
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'activity'
        verbose_name_plural = 'activities'
        ordering = ['title']
    
    def __str__(self):
        return self.title


class LearningPath(models.Model):
    """
    A learning path is an ordered sequence of activities.
    Paths can be attached to communities.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic info
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True)
    
    # Cover image
    cover_image_url = models.URLField(max_length=500, blank=True)
    
    # Structure type
    is_sequential = models.BooleanField(
        default=True,
        help_text='If true, activities must be completed in order'
    )
    
    # Learning metadata
    estimated_hours = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True
    )
    outcomes = models.JSONField(
        default=list,
        blank=True,
        help_text='Learning outcomes for completing this path'
    )
    
    # Prerequisites - other paths that should be completed first
    prerequisites = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='unlocks'
    )
    
    # Visibility
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Ownership
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='paths_created'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Metadata
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'learning path'
        verbose_name_plural = 'learning paths'
        ordering = ['title']
    
    def __str__(self):
        return self.title
    
    @property
    def activity_count(self):
        """Return the number of activities in this path."""
        return self.path_activities.count()
    
    @property
    def total_estimated_minutes(self):
        """Calculate total estimated time from all activities."""
        return sum(
            pa.activity.estimated_minutes or 0
            for pa in self.path_activities.select_related('activity')
        )


class PathActivity(models.Model):
    """
    Junction table linking activities to learning paths with ordering.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    path = models.ForeignKey(
        LearningPath,
        on_delete=models.CASCADE,
        related_name='path_activities'
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='path_memberships'
    )
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    # Optional section/module grouping within the path
    section_title = models.CharField(max_length=255, blank=True)
    section_order = models.PositiveIntegerField(default=0)
    
    # Branching conditions (basic in v1)
    is_required = models.BooleanField(default=True)
    unlock_conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text='Conditions to unlock this activity (e.g., minimum score on previous)'
    )
    
    class Meta:
        verbose_name = 'path activity'
        verbose_name_plural = 'path activities'
        unique_together = ['path', 'activity']
        ordering = ['section_order', 'order']
    
    def __str__(self):
        return f'{self.path.title} - {self.activity.title} (#{self.order})'


class CommunityPath(models.Model):
    """
    Junction table linking learning paths to communities.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    community = models.ForeignKey(
        'communities.Community',
        on_delete=models.CASCADE,
        related_name='community_paths'
    )
    path = models.ForeignKey(
        LearningPath,
        on_delete=models.CASCADE,
        related_name='community_assignments'
    )
    
    # Visibility within community
    is_featured = models.BooleanField(default=False)
    is_required = models.BooleanField(default=False)
    
    # Scheduling
    available_from = models.DateTimeField(null=True, blank=True)
    available_until = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='paths_assigned'
    )
    
    class Meta:
        verbose_name = 'community path'
        verbose_name_plural = 'community paths'
        unique_together = ['community', 'path']
        ordering = ['-is_featured', '-added_at']
    
    def __str__(self):
        return f'{self.community.name} - {self.path.title}'


class Enrollment(models.Model):
    """
    Tracks a user's enrollment in a learning path.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    path = models.ForeignKey(
        LearningPath,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    # Optional: enrollment through a specific community
    community = models.ForeignKey(
        'communities.Community',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enrollments'
    )
    
    # Progress tracking
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    
    # Timestamps
    enrolled_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'enrollment'
        verbose_name_plural = 'enrollments'
        unique_together = ['user', 'path', 'community']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f'{self.user.email} - {self.path.title}'
    
    @property
    def is_completed(self):
        """Check if the enrollment is completed."""
        return self.completed_at is not None


class ActivityProgress(models.Model):
    """
    Tracks a user's progress on a specific activity.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activity_progress'
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    # Optional: progress within a specific enrollment
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='activity_progress'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('not_started', 'Not Started'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
        ],
        default='not_started'
    )
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    
    # Time spent
    total_time_seconds = models.PositiveIntegerField(default=0)
    
    # Bookmarking
    bookmark_position = models.JSONField(
        default=dict,
        blank=True,
        help_text='User position in the content for resuming'
    )
    
    class Meta:
        verbose_name = 'activity progress'
        verbose_name_plural = 'activity progress records'
        unique_together = ['user', 'activity', 'enrollment']
        ordering = ['-last_accessed_at']
    
    def __str__(self):
        return f'{self.user.email} - {self.activity.title} ({self.status})'

