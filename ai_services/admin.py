"""
Admin configuration for the ai_services app.
"""
from django.contrib import admin

from .models import (
    AIProvider, AICapability, EmbeddingCollection, EmbeddingDocument,
    AIAgent, AIInteraction, AgentRun
)


@admin.register(AIProvider)
class AIProviderAdmin(admin.ModelAdmin):
    """Admin configuration for AI providers."""
    
    list_display = ('name', 'provider_type', 'default_chat_model', 'is_active', 'is_default')
    list_filter = ('provider_type', 'is_active', 'is_default')
    search_fields = ('name',)


@admin.register(AICapability)
class AICapabilityAdmin(admin.ModelAdmin):
    """Admin configuration for AI capabilities."""
    
    list_display = ('display_name', 'capability_type', 'provider', 'use_rag', 'is_active')
    list_filter = ('capability_type', 'use_rag', 'is_active')
    search_fields = ('name', 'display_name')
    raw_id_fields = ('provider',)


@admin.register(EmbeddingCollection)
class EmbeddingCollectionAdmin(admin.ModelAdmin):
    """Admin configuration for embedding collections."""
    
    list_display = ('display_name', 'qdrant_collection', 'embedding_model', 'document_count', 'last_indexed_at')
    search_fields = ('name', 'display_name', 'qdrant_collection')


@admin.register(EmbeddingDocument)
class EmbeddingDocumentAdmin(admin.ModelAdmin):
    """Admin configuration for embedding documents."""
    
    list_display = ('title', 'collection', 'source_type', 'chunk_index', 'created_at')
    list_filter = ('source_type', 'collection')
    search_fields = ('title', 'source_id')
    raw_id_fields = ('collection',)


@admin.register(AIAgent)
class AIAgentAdmin(admin.ModelAdmin):
    """Admin configuration for AI agents."""
    
    list_display = ('display_name', 'agent_type', 'trigger_type', 'is_active', 'last_run_at')
    list_filter = ('agent_type', 'trigger_type', 'is_active')
    search_fields = ('name', 'display_name')
    filter_horizontal = ('capabilities',)


@admin.register(AIInteraction)
class AIInteractionAdmin(admin.ModelAdmin):
    """Admin configuration for AI interactions."""
    
    list_display = ('interaction_type', 'user', 'capability', 'status', 'total_tokens', 'created_at')
    list_filter = ('interaction_type', 'status', 'capability')
    search_fields = ('user__email', 'input_text')
    raw_id_fields = ('user', 'agent', 'capability', 'provider')
    readonly_fields = ('created_at',)


@admin.register(AgentRun)
class AgentRunAdmin(admin.ModelAdmin):
    """Admin configuration for agent runs."""
    
    list_display = ('agent', 'trigger_type', 'status', 'items_processed', 'created_at')
    list_filter = ('status', 'agent')
    search_fields = ('agent__name',)
    raw_id_fields = ('agent',)

