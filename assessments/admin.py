"""
Admin configuration for the assessments app.
"""
from django.contrib import admin

from .models import (
    Assessment, Question, Choice, AssessmentAttempt,
    QuestionResponse, MasteryEstimate
)


class ChoiceInline(admin.TabularInline):
    """Inline for choices within a question."""
    model = Choice
    extra = 4


class QuestionInline(admin.TabularInline):
    """Inline for questions within an assessment."""
    model = Question
    extra = 1
    show_change_link = True


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    """Admin configuration for assessments."""
    
    list_display = ('title', 'activity', 'question_count', 'passing_score', 'max_attempts', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')
    raw_id_fields = ('activity', 'created_by')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin configuration for questions."""
    
    list_display = ('assessment', 'question_type', 'points', 'difficulty', 'order')
    list_filter = ('question_type', 'difficulty')
    search_fields = ('text', 'assessment__title')
    raw_id_fields = ('assessment',)
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    """Admin configuration for choices."""
    
    list_display = ('question', 'text', 'is_correct', 'order')
    list_filter = ('is_correct',)
    search_fields = ('text', 'question__text')
    raw_id_fields = ('question',)


@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    """Admin configuration for assessment attempts."""
    
    list_display = ('user', 'assessment', 'attempt_number', 'status', 'score_percent', 'passed', 'started_at')
    list_filter = ('status', 'passed')
    search_fields = ('user__email', 'assessment__title')
    raw_id_fields = ('user', 'assessment', 'enrollment', 'graded_by')


@admin.register(QuestionResponse)
class QuestionResponseAdmin(admin.ModelAdmin):
    """Admin configuration for question responses."""
    
    list_display = ('attempt', 'question', 'points_earned', 'is_correct', 'answered_at')
    list_filter = ('is_correct',)
    search_fields = ('attempt__user__email', 'question__text')
    raw_id_fields = ('attempt', 'question')


@admin.register(MasteryEstimate)
class MasteryEstimateAdmin(admin.ModelAdmin):
    """Admin configuration for mastery estimates."""
    
    list_display = ('user', 'outcome_tag', 'community', 'mastery_level', 'confidence', 'updated_at')
    list_filter = ('outcome_tag',)
    search_fields = ('user__email', 'outcome_tag')
    raw_id_fields = ('user', 'community')

