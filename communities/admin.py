"""
Admin configuration for the communities app.
"""
from django.contrib import admin

from .models import Community, Group, CommunityMembership, GroupMembership


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    """Admin configuration for communities."""
    
    list_display = ('name', 'community_type', 'visibility', 'is_active', 'member_count', 'created_at')
    list_filter = ('community_type', 'visibility', 'is_active')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('created_by', 'parent')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Admin configuration for groups."""
    
    list_display = ('name', 'community', 'purpose', 'is_active', 'member_count', 'created_at')
    list_filter = ('is_active', 'purpose')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('community', 'created_by')


@admin.register(CommunityMembership)
class CommunityMembershipAdmin(admin.ModelAdmin):
    """Admin configuration for community memberships."""
    
    list_display = ('user', 'community', 'role', 'is_active', 'joined_at')
    list_filter = ('role', 'is_active')
    search_fields = ('user__email', 'community__name')
    raw_id_fields = ('user', 'community', 'invited_by')


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    """Admin configuration for group memberships."""
    
    list_display = ('user', 'group', 'role', 'is_active', 'joined_at')
    list_filter = ('role', 'is_active')
    search_fields = ('user__email', 'group__name')
    raw_id_fields = ('user', 'group')

