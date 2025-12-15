"""
User models for the LXP platform.

Implements custom user model with support for:
- Multiple roles (learner, facilitator, admin, parent/mentor)
- Passwordless authentication
- User preferences and metadata
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserRole(models.TextChoices):
    """User role choices for the LXP platform."""
    LEARNER = 'learner', 'Learner'
    FACILITATOR = 'facilitator', 'Facilitator/Instructor'
    ADMIN = 'admin', 'Administrator'
    PARENT = 'parent', 'Parent/Mentor'


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""

    def create_user(self, email, **extra_fields):
        """Create and return a regular user with the given email."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_unusable_password()  # Passwordless by default
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user(email, **extra_fields)
        if password:
            user.set_password(password)
            user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for the LXP platform.
    
    Uses email as the unique identifier and supports passwordless authentication.
    """
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    # Role can be multiple via UserRoleAssignment, but primary role stored here
    primary_role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.LEARNER
    )
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Optional profile metadata (stored as JSON)
    interests = models.JSONField(default=list, blank=True)
    goals = models.JSONField(default=list, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    
    # Avatar/profile image (stored in MinIO)
    avatar_url = models.URLField(max_length=500, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.email
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.email.split('@')[0]
    
    @property
    def roles(self):
        """Return all roles assigned to the user."""
        role_assignments = self.role_assignments.values_list('role', flat=True)
        roles = list(role_assignments)
        if self.primary_role and self.primary_role not in roles:
            roles.insert(0, self.primary_role)
        return roles


class UserRoleAssignment(models.Model):
    """
    Allows users to have multiple roles, potentially scoped to communities.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='role_assignments'
    )
    role = models.CharField(max_length=20, choices=UserRole.choices)
    # Optional: scope role to a specific community
    community_id = models.UUIDField(null=True, blank=True, db_index=True)
    
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='roles_assigned'
    )
    
    class Meta:
        unique_together = ['user', 'role', 'community_id']
        verbose_name = 'role assignment'
        verbose_name_plural = 'role assignments'
    
    def __str__(self):
        scope = f' in community {self.community_id}' if self.community_id else ''
        return f'{self.user.email} - {self.role}{scope}'


class MagicLink(models.Model):
    """
    Stores magic link tokens for passwordless authentication.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='magic_links'
    )
    token = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'magic link'
        verbose_name_plural = 'magic links'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Magic link for {self.user.email}'
    
    @property
    def is_valid(self):
        """Check if the magic link is still valid."""
        return (
            self.used_at is None and
            self.expires_at > timezone.now()
        )


class RefreshToken(models.Model):
    """
    Stores refresh tokens for JWT authentication.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='refresh_tokens'
    )
    token = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    device_info = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'refresh token'
        verbose_name_plural = 'refresh tokens'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Refresh token for {self.user.email}'
    
    @property
    def is_valid(self):
        """Check if the refresh token is still valid."""
        return (
            self.revoked_at is None and
            self.expires_at > timezone.now()
        )

