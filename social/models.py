"""
Social models for the LXP platform.

Implements:
- Threads (discussion topics)
- Posts and comments
- Reactions
- Shared resources
"""

import uuid
from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class Thread(models.Model):
    """
    A discussion thread within a community or activity.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Where this thread belongs
    community = models.ForeignKey(
        'communities.Community',
        on_delete=models.CASCADE,
        related_name='threads'
    )
    # Optional: thread associated with a specific activity
    activity = models.ForeignKey(
        'content.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='threads'
    )
    # Optional: thread associated with a specific group
    group = models.ForeignKey(
        'communities.Group',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='threads'
    )
    
    # Thread content
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    
    # Thread type
    thread_type = models.CharField(
        max_length=20,
        choices=[
            ('discussion', 'Discussion'),
            ('question', 'Question'),
            ('announcement', 'Announcement'),
            ('reflection', 'Reflection'),
        ],
        default='discussion'
    )
    
    # Status
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_answered = models.BooleanField(default=False)  # For question threads
    
    # Author
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='threads_created'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity_at = models.DateTimeField(auto_now_add=True)
    
    # Metadata
    tags = models.JSONField(default=list, blank=True)
    
    # Generic relations
    reactions = GenericRelation('Reaction')
    
    class Meta:
        verbose_name = 'thread'
        verbose_name_plural = 'threads'
        ordering = ['-is_pinned', '-last_activity_at']
    
    def __str__(self):
        return self.title
    
    @property
    def post_count(self):
        """Return the number of posts in this thread."""
        return self.posts.count()
    
    @property
    def participant_count(self):
        """Return the number of unique participants."""
        return self.posts.values('author').distinct().count()


class Post(models.Model):
    """
    A post/reply within a thread.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Parent thread
    thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    
    # For nested replies
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    # Content
    body = models.TextField()
    
    # Author
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts'
    )
    
    # Status
    is_answer = models.BooleanField(default=False)  # Marked as accepted answer
    is_edited = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Generic relations
    reactions = GenericRelation('Reaction')
    
    class Meta:
        verbose_name = 'post'
        verbose_name_plural = 'posts'
        ordering = ['created_at']
    
    def __str__(self):
        return f'Post by {self.author} in {self.thread.title}'
    
    @property
    def reply_count(self):
        """Return the number of direct replies."""
        return self.replies.filter(is_deleted=False).count()


class Comment(models.Model):
    """
    A comment on any content using generic foreign keys.
    Used for comments on activities, shared resources, etc.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Generic foreign key to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Community context (required)
    community = models.ForeignKey(
        'communities.Community',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    
    # For nested replies
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    # Content
    body = models.TextField()
    
    # Author
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='comments'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    
    # Generic relations
    reactions = GenericRelation('Reaction')
    
    class Meta:
        verbose_name = 'comment'
        verbose_name_plural = 'comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f'Comment by {self.author}'


class ReactionType(models.TextChoices):
    """Available reaction types."""
    LIKE = 'like', '👍 Like'
    LOVE = 'love', '❤️ Love'
    INSIGHTFUL = 'insightful', '💡 Insightful'
    HELPFUL = 'helpful', '🙏 Helpful'
    CELEBRATE = 'celebrate', '🎉 Celebrate'


class Reaction(models.Model):
    """
    A reaction (like/upvote, etc.) on any content.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Generic foreign key to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Reaction type
    reaction_type = models.CharField(
        max_length=20,
        choices=ReactionType.choices,
        default=ReactionType.LIKE
    )
    
    # Who reacted
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'reaction'
        verbose_name_plural = 'reactions'
        unique_together = ['content_type', 'object_id', 'user', 'reaction_type']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f'{self.reaction_type} by {self.user}'


class SharedResource(models.Model):
    """
    A shared resource (link, file, content reference) within a community.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Where this resource is shared
    community = models.ForeignKey(
        'communities.Community',
        on_delete=models.CASCADE,
        related_name='shared_resources'
    )
    # Optional: shared within a specific thread
    thread = models.ForeignKey(
        Thread,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shared_resources'
    )
    # Optional: shared within a specific group
    group = models.ForeignKey(
        'communities.Group',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shared_resources'
    )
    
    # Resource info
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Resource type and location
    resource_type = models.CharField(
        max_length=20,
        choices=[
            ('link', 'External Link'),
            ('file', 'Uploaded File'),
            ('activity', 'Activity Reference'),
            ('document', 'Document'),
        ],
        default='link'
    )
    url = models.URLField(max_length=500, blank=True)  # For links
    file_key = models.CharField(max_length=500, blank=True)  # For MinIO files
    activity = models.ForeignKey(
        'content.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shares'
    )
    
    # Metadata
    thumbnail_url = models.URLField(max_length=500, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    file_type = models.CharField(max_length=50, blank=True)
    
    # Sharing info
    shared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='resources_shared'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Tags
    tags = models.JSONField(default=list, blank=True)
    
    # Generic relations
    reactions = GenericRelation(Reaction)
    
    class Meta:
        verbose_name = 'shared resource'
        verbose_name_plural = 'shared resources'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

