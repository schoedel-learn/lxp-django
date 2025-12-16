"""
Community models for the LXP platform.

Implements:
- Communities (parish, cohort, ministry, class, interest group)
- Groups/small circles (sub-communities)
- Memberships with roles
"""

import uuid
from django.db import models


class CommunityVisibility(models.TextChoices):
    """Visibility options for communities."""
    PUBLIC = 'public', 'Public'
    PRIVATE = 'private', 'Private'
    UNLISTED = 'unlisted', 'Unlisted'


class CommunityType(models.TextChoices):
    """Type categories for communities."""
    PARISH = 'parish', 'Parish'
    COHORT = 'cohort', 'Cohort'
    MINISTRY = 'ministry', 'Ministry'
    CLASS = 'class', 'Class'
    INTEREST_GROUP = 'interest_group', 'Interest Group'
    OTHER = 'other', 'Other'


class MembershipRole(models.TextChoices):
    """Roles within a community."""
    MEMBER = 'member', 'Member'
    FACILITATOR = 'facilitator', 'Facilitator'
    ADMIN = 'admin', 'Administrator'


class Community(models.Model):
    """
    A community represents a group of learners organized around
    a common purpose (parish, cohort, ministry, class, interest group).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic info
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True)
    
    # Classification
    community_type = models.CharField(
        max_length=20,
        choices=CommunityType.choices,
        default=CommunityType.OTHER
    )
    visibility = models.CharField(
        max_length=20,
        choices=CommunityVisibility.choices,
        default=CommunityVisibility.PRIVATE
    )
    
    # Branding
    logo_url = models.URLField(max_length=500, blank=True)
    banner_url = models.URLField(max_length=500, blank=True)
    
    # Metadata
    tags = models.JSONField(default=list, blank=True)
    community_settings = models.JSONField(default=dict, blank=True)
    
    # Hierarchy - communities can have parent communities
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    
    # Ownership
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='communities_created'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'community'
        verbose_name_plural = 'communities'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def member_count(self):
        """Return the number of active members."""
        return self.memberships.filter(is_active=True).count()


class Group(models.Model):
    """
    A group is a sub-community for projects, study circles, or mentoring.
    Groups exist within a community.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Parent community
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='groups'
    )
    
    # Basic info
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    
    # Group purpose
    purpose = models.CharField(max_length=100, blank=True)
    
    # Capacity
    max_members = models.PositiveIntegerField(null=True, blank=True)
    
    # Metadata
    group_settings = models.JSONField(default=dict, blank=True)
    
    # Ownership
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='groups_created'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'group'
        verbose_name_plural = 'groups'
        unique_together = ['community', 'slug']
        ordering = ['name']
    
    def __str__(self):
        return f'{self.name} ({self.community.name})'
    
    @property
    def member_count(self):
        """Return the number of active members."""
        return self.memberships.filter(is_active=True).count()


class CommunityMembership(models.Model):
    """
    Represents a user's membership in a community with a specific role.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='community_memberships'
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    
    # Role in the community
    role = models.CharField(
        max_length=20,
        choices=MembershipRole.choices,
        default=MembershipRole.MEMBER
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    # Invitation tracking
    invited_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invitations_sent'
    )
    
    # Custom settings for this membership
    notification_preferences = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'community membership'
        verbose_name_plural = 'community memberships'
        unique_together = ['user', 'community']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f'{self.user.email} - {self.community.name} ({self.role})'


class GroupMembership(models.Model):
    """
    Represents a user's membership in a group within a community.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='group_memberships'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    
    # Role in the group
    role = models.CharField(
        max_length=20,
        choices=MembershipRole.choices,
        default=MembershipRole.MEMBER
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'group membership'
        verbose_name_plural = 'group memberships'
        unique_together = ['user', 'group']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f'{self.user.email} - {self.group.name} ({self.role})'
