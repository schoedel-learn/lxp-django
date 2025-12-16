"""
Admin configuration for the accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserRoleAssignment, MagicLink, RefreshToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the custom User model."""
    
    list_display = ('email', 'first_name', 'last_name', 'primary_role', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'primary_role', 'is_email_verified')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'avatar_url')}),
        ('Role', {'fields': ('primary_role',)}),
        ('Preferences', {'fields': ('interests', 'goals', 'preferences')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_email_verified', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'primary_role'),
        }),
    )


@admin.register(UserRoleAssignment)
class UserRoleAssignmentAdmin(admin.ModelAdmin):
    """Admin configuration for role assignments."""
    
    list_display = ('user', 'role', 'community_id', 'assigned_at')
    list_filter = ('role',)
    search_fields = ('user__email',)
    raw_id_fields = ('user', 'assigned_by')


@admin.register(MagicLink)
class MagicLinkAdmin(admin.ModelAdmin):
    """Admin configuration for magic links."""
    
    list_display = ('user', 'created_at', 'expires_at', 'used_at')
    list_filter = ('created_at',)
    search_fields = ('user__email',)
    raw_id_fields = ('user',)
    readonly_fields = ('token',)


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    """Admin configuration for refresh tokens."""
    
    list_display = ('user', 'created_at', 'expires_at', 'revoked_at')
    list_filter = ('created_at', 'revoked_at')
    search_fields = ('user__email',)
    raw_id_fields = ('user',)
    readonly_fields = ('token',)

