"""
Admin configuration for the social app.
"""
from django.contrib import admin

from .models import Thread, Post, Comment, Reaction, SharedResource


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    """Admin configuration for threads."""
    
    list_display = ('title', 'community', 'thread_type', 'author', 'is_pinned', 'is_locked', 'created_at')
    list_filter = ('thread_type', 'is_pinned', 'is_locked', 'is_answered')
    search_fields = ('title', 'body', 'author__email')
    raw_id_fields = ('community', 'activity', 'group', 'author')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin configuration for posts."""
    
    list_display = ('thread', 'author', 'is_answer', 'is_deleted', 'created_at')
    list_filter = ('is_answer', 'is_deleted', 'is_edited')
    search_fields = ('body', 'author__email', 'thread__title')
    raw_id_fields = ('thread', 'parent', 'author')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin configuration for comments."""
    
    list_display = ('author', 'community', 'is_deleted', 'created_at')
    list_filter = ('is_deleted', 'created_at')
    search_fields = ('body', 'author__email')
    raw_id_fields = ('community', 'parent', 'author')


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    """Admin configuration for reactions."""
    
    list_display = ('user', 'reaction_type', 'content_type', 'created_at')
    list_filter = ('reaction_type',)
    search_fields = ('user__email',)
    raw_id_fields = ('user',)


@admin.register(SharedResource)
class SharedResourceAdmin(admin.ModelAdmin):
    """Admin configuration for shared resources."""
    
    list_display = ('title', 'community', 'resource_type', 'shared_by', 'created_at')
    list_filter = ('resource_type',)
    search_fields = ('title', 'description', 'shared_by__email')
    raw_id_fields = ('community', 'thread', 'group', 'activity', 'shared_by')

