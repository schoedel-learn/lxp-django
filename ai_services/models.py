"""
AI Services models for the LXP platform.

Implements:
- AI service configuration
- RAG pipeline tracking
- Agentic workflow management
- AI interaction logging for governance and provenance
"""

import uuid
from django.conf import settings
from django.db import models


class AIProvider(models.Model):
    """
    Configuration for an AI/LLM provider.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100)
    provider_type = models.CharField(
        max_length=20,
        choices=[
            ('openai', 'OpenAI'),
            ('anthropic', 'Anthropic'),
            ('azure_openai', 'Azure OpenAI'),
            ('custom', 'Custom'),
        ],
        default='openai'
    )
    
    # API configuration
    api_endpoint = models.URLField(max_length=500, blank=True)
    api_key_env_var = models.CharField(
        max_length=100,
        default='OPENAI_API_KEY',
        help_text='Environment variable name for API key'
    )
    
    # Default models
    default_chat_model = models.CharField(max_length=100, default='gpt-4-turbo-preview')
    default_embedding_model = models.CharField(max_length=100, default='text-embedding-3-small')
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    # Rate limiting
    requests_per_minute = models.PositiveIntegerField(default=60)
    tokens_per_minute = models.PositiveIntegerField(default=100000)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'AI provider'
        verbose_name_plural = 'AI providers'
    
    def __str__(self):
        return f'{self.name} ({self.provider_type})'


class AICapability(models.Model):
    """
    Defines available AI capabilities/services.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Capability type
    capability_type = models.CharField(
        max_length=30,
        choices=[
            ('generate_explanation', 'Generate Explanation'),
            ('generate_example', 'Generate Example'),
            ('summarize_discussion', 'Summarize Discussion'),
            ('summarize_content', 'Summarize Content'),
            ('classify_response', 'Classify Response'),
            ('generate_feedback', 'Generate Feedback'),
            ('answer_question', 'Answer Question'),
            ('generate_quiz', 'Generate Quiz Questions'),
            ('translate', 'Translate Content'),
            ('custom', 'Custom'),
        ],
        default='custom'
    )
    
    # Provider to use
    provider = models.ForeignKey(
        AIProvider,
        on_delete=models.SET_NULL,
        null=True,
        related_name='capabilities'
    )
    
    # Model to use (overrides provider default)
    model_name = models.CharField(max_length=100, blank=True)
    
    # Prompt template (uses Jinja2-style templating)
    system_prompt = models.TextField(
        blank=True,
        help_text='System prompt template'
    )
    user_prompt_template = models.TextField(
        blank=True,
        help_text='User prompt template with {{variables}}'
    )
    
    # RAG settings
    use_rag = models.BooleanField(default=False)
    rag_collection = models.CharField(
        max_length=100,
        blank=True,
        help_text='Qdrant collection to search'
    )
    rag_top_k = models.PositiveIntegerField(default=5)
    
    # Generation parameters
    temperature = models.DecimalField(max_digits=3, decimal_places=2, default=0.7)
    max_tokens = models.PositiveIntegerField(default=1000)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'AI capability'
        verbose_name_plural = 'AI capabilities'
        ordering = ['display_name']
    
    def __str__(self):
        return self.display_name


class EmbeddingCollection(models.Model):
    """
    Tracks Qdrant collections for RAG.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Qdrant collection name
    qdrant_collection = models.CharField(max_length=100)
    
    # Embedding configuration
    embedding_model = models.CharField(max_length=100, default='text-embedding-3-small')
    embedding_dimensions = models.PositiveIntegerField(default=1536)
    
    # Content sources
    source_types = models.JSONField(
        default=list,
        help_text='Types of content in this collection'
    )
    
    # Statistics
    document_count = models.PositiveIntegerField(default=0)
    last_indexed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'embedding collection'
        verbose_name_plural = 'embedding collections'
    
    def __str__(self):
        return self.display_name


class EmbeddingDocument(models.Model):
    """
    Tracks documents indexed in Qdrant for provenance.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    collection = models.ForeignKey(
        EmbeddingCollection,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    
    # Source reference
    source_type = models.CharField(
        max_length=50,
        choices=[
            ('activity_content', 'Activity Content'),
            ('transcript', 'Transcript'),
            ('document', 'Document'),
            ('social_post', 'Social Post'),
            ('reflection', 'Learner Reflection'),
            ('policy', 'Policy Document'),
        ]
    )
    source_id = models.CharField(max_length=255)
    
    # Content metadata
    title = models.CharField(max_length=255, blank=True)
    chunk_index = models.PositiveIntegerField(default=0)
    chunk_text = models.TextField(help_text='The actual text chunk')
    
    # Access control metadata
    community_id = models.UUIDField(null=True, blank=True, db_index=True)
    visibility = models.CharField(max_length=20, default='private')
    
    # Qdrant point ID
    qdrant_point_id = models.CharField(max_length=100)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'embedding document'
        verbose_name_plural = 'embedding documents'
        indexes = [
            models.Index(fields=['source_type', 'source_id']),
        ]
    
    def __str__(self):
        return f'{self.source_type}: {self.title or self.source_id}'


class AIAgent(models.Model):
    """
    Configuration for an AI agent.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Agent type
    agent_type = models.CharField(
        max_length=30,
        choices=[
            ('engagement_monitor', 'Engagement Monitor'),
            ('learning_recommender', 'Learning Recommender'),
            ('facilitator_assistant', 'Facilitator Assistant'),
            ('content_curator', 'Content Curator'),
            ('assessment_helper', 'Assessment Helper'),
            ('custom', 'Custom'),
        ],
        default='custom'
    )
    
    # Trigger configuration
    trigger_type = models.CharField(
        max_length=20,
        choices=[
            ('scheduled', 'Scheduled'),
            ('event', 'Event-driven'),
            ('manual', 'Manual'),
        ],
        default='scheduled'
    )
    schedule = models.CharField(
        max_length=100,
        blank=True,
        help_text='Cron expression for scheduled agents'
    )
    trigger_events = models.JSONField(
        default=list,
        help_text='Events that trigger this agent'
    )
    
    # Agent configuration
    config = models.JSONField(
        default=dict,
        help_text='Agent-specific configuration'
    )
    
    # Capabilities used
    capabilities = models.ManyToManyField(
        AICapability,
        related_name='agents',
        blank=True
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'AI agent'
        verbose_name_plural = 'AI agents'
        ordering = ['display_name']
    
    def __str__(self):
        return self.display_name


class AIInteraction(models.Model):
    """
    Logs all AI interactions for governance and provenance.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # What triggered this interaction
    interaction_type = models.CharField(
        max_length=30,
        choices=[
            ('user_request', 'User Request'),
            ('agent_action', 'Agent Action'),
            ('system_task', 'System Task'),
        ],
        default='user_request'
    )
    
    # Who/what initiated
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_interactions'
    )
    agent = models.ForeignKey(
        AIAgent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='interactions'
    )
    
    # Capability used
    capability = models.ForeignKey(
        AICapability,
        on_delete=models.SET_NULL,
        null=True,
        related_name='interactions'
    )
    
    # Context
    community_id = models.UUIDField(null=True, blank=True)
    activity_id = models.UUIDField(null=True, blank=True)
    
    # Input (sanitized if necessary)
    input_text = models.TextField(help_text='User query or agent input')
    input_metadata = models.JSONField(default=dict, blank=True)
    
    # RAG sources used
    rag_documents_used = models.JSONField(
        default=list,
        help_text='IDs of documents used from RAG'
    )
    
    # Output
    output_text = models.TextField(help_text='AI response')
    output_metadata = models.JSONField(default=dict, blank=True)
    
    # Provider/model info
    provider = models.ForeignKey(
        AIProvider,
        on_delete=models.SET_NULL,
        null=True,
        related_name='interactions'
    )
    model_used = models.CharField(max_length=100, blank=True)
    
    # Token usage
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)
    
    # Timing
    latency_ms = models.PositiveIntegerField(default=0)
    
    # Quality/feedback
    user_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text='User rating 1-5'
    )
    user_feedback = models.TextField(blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('error', 'Error'),
            ('filtered', 'Filtered'),
        ],
        default='success'
    )
    error_message = models.TextField(blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'AI interaction'
        verbose_name_plural = 'AI interactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['capability', 'created_at']),
        ]
    
    def __str__(self):
        return f'{self.interaction_type} - {self.capability} ({self.created_at})'


class AgentRun(models.Model):
    """
    Tracks individual agent execution runs.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    agent = models.ForeignKey(
        AIAgent,
        on_delete=models.CASCADE,
        related_name='runs'
    )
    
    # Trigger info
    trigger_type = models.CharField(max_length=20)
    trigger_event = models.JSONField(default=dict, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    
    # Results
    actions_taken = models.JSONField(
        default=list,
        help_text='List of actions the agent took'
    )
    items_processed = models.PositiveIntegerField(default=0)
    
    # Error info
    error_message = models.TextField(blank=True)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'agent run'
        verbose_name_plural = 'agent runs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.agent.display_name} run ({self.status})'

