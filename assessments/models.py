"""
Assessment models for the LXP platform.

Implements:
- Assessment items/questions
- Attempts and responses
- Scoring and feedback
- Mastery tracking
"""

import uuid
from django.conf import settings
from django.db import models


class QuestionType(models.TextChoices):
    """Types of assessment questions."""
    MULTIPLE_CHOICE = 'multiple_choice', 'Multiple Choice'
    MULTIPLE_SELECT = 'multiple_select', 'Multiple Select'
    TRUE_FALSE = 'true_false', 'True/False'
    SHORT_ANSWER = 'short_answer', 'Short Answer'
    LONG_ANSWER = 'long_answer', 'Long Answer/Essay'
    MATCHING = 'matching', 'Matching'
    ORDERING = 'ordering', 'Ordering/Sequencing'
    FILL_BLANK = 'fill_blank', 'Fill in the Blank'
    NUMERIC = 'numeric', 'Numeric'
    FILE_UPLOAD = 'file_upload', 'File Upload'


class Assessment(models.Model):
    """
    An assessment containing multiple questions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic info
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    
    # Associated activity
    activity = models.ForeignKey(
        'content.Activity',
        on_delete=models.CASCADE,
        related_name='assessments'
    )
    
    # Assessment settings
    time_limit_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Time limit in minutes (null = no limit)'
    )
    max_attempts = models.PositiveIntegerField(
        default=0,
        help_text='Maximum number of attempts (0 = unlimited)'
    )
    passing_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=70.00,
        help_text='Minimum score to pass (percentage)'
    )
    
    # Randomization
    randomize_questions = models.BooleanField(default=False)
    randomize_choices = models.BooleanField(default=False)
    questions_to_show = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Number of questions to show (null = all)'
    )
    
    # Feedback settings
    show_correct_answers = models.BooleanField(default=True)
    show_feedback = models.BooleanField(default=True)
    show_score_immediately = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Ownership
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assessments_created'
    )
    
    class Meta:
        verbose_name = 'assessment'
        verbose_name_plural = 'assessments'
        ordering = ['title']
    
    def __str__(self):
        return self.title
    
    @property
    def question_count(self):
        """Return the number of questions."""
        return self.questions.count()
    
    @property
    def total_points(self):
        """Return the total points available."""
        return sum(q.points for q in self.questions.all())


class Question(models.Model):
    """
    A single question within an assessment.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Parent assessment
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    
    # Question content
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.MULTIPLE_CHOICE
    )
    text = models.TextField(help_text='The question text')
    explanation = models.TextField(
        blank=True,
        help_text='Explanation shown after answering'
    )
    
    # For rich content (images, etc.)
    media_url = models.URLField(max_length=500, blank=True)
    
    # Scoring
    points = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    partial_credit = models.BooleanField(
        default=False,
        help_text='Allow partial credit for partially correct answers'
    )
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    # Learning outcome mapping
    outcome_tags = models.JSONField(
        default=list,
        blank=True,
        help_text='Learning outcomes this question assesses'
    )
    
    # Question bank tagging
    difficulty = models.CharField(
        max_length=10,
        choices=[
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('hard', 'Hard'),
        ],
        default='medium'
    )
    tags = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'question'
        verbose_name_plural = 'questions'
        ordering = ['order']
    
    def __str__(self):
        return f'{self.assessment.title} - Q{self.order + 1}'


class Choice(models.Model):
    """
    A choice/option for a multiple choice or multiple select question.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Parent question
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    
    # Choice content
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    
    # Optional: partial points for this choice
    points = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Points for selecting this choice (for partial credit)'
    )
    
    # Feedback for this specific choice
    feedback = models.TextField(
        blank=True,
        help_text='Feedback shown when this choice is selected'
    )
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'choice'
        verbose_name_plural = 'choices'
        ordering = ['order']
    
    def __str__(self):
        return f'{self.question} - Choice {self.order + 1}'


class AssessmentAttempt(models.Model):
    """
    A user's attempt at an assessment.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Who and what
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assessment_attempts'
    )
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    
    # Optional: attempt within a specific enrollment
    enrollment = models.ForeignKey(
        'content.Enrollment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assessment_attempts'
    )
    
    # Attempt number
    attempt_number = models.PositiveIntegerField(default=1)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('in_progress', 'In Progress'),
            ('submitted', 'Submitted'),
            ('graded', 'Graded'),
            ('timed_out', 'Timed Out'),
        ],
        default='in_progress'
    )
    
    # Scoring
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    score_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    passed = models.BooleanField(null=True, blank=True)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    
    # Grading
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attempts_graded'
    )
    feedback = models.TextField(blank=True)
    
    # Questions shown (if randomized)
    questions_shown = models.JSONField(
        default=list,
        blank=True,
        help_text='IDs of questions shown in this attempt'
    )
    
    class Meta:
        verbose_name = 'assessment attempt'
        verbose_name_plural = 'assessment attempts'
        ordering = ['-started_at']
    
    def __str__(self):
        return f'{self.user.email} - {self.assessment.title} (Attempt {self.attempt_number})'


class QuestionResponse(models.Model):
    """
    A user's response to a single question.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Links
    attempt = models.ForeignKey(
        AssessmentAttempt,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    
    # Response data (flexible JSON to handle different question types)
    response_data = models.JSONField(
        default=dict,
        help_text='User response data'
    )
    # For text responses
    text_response = models.TextField(blank=True)
    # For file uploads
    file_url = models.URLField(max_length=500, blank=True)
    
    # Scoring
    points_earned = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    is_correct = models.BooleanField(null=True, blank=True)
    
    # Feedback
    feedback = models.TextField(blank=True)
    ai_feedback = models.TextField(
        blank=True,
        help_text='AI-generated feedback'
    )
    
    # Timestamps
    answered_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'question response'
        verbose_name_plural = 'question responses'
        unique_together = ['attempt', 'question']
        ordering = ['question__order']
    
    def __str__(self):
        return f'{self.attempt.user.email} - {self.question}'


class MasteryEstimate(models.Model):
    """
    Tracks a user's mastery level for a specific learning outcome.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mastery_estimates'
    )
    
    # What this mastery is for
    outcome_tag = models.CharField(
        max_length=255,
        db_index=True,
        help_text='Learning outcome identifier'
    )
    
    # Optional: scoped to a specific community
    community = models.ForeignKey(
        'communities.Community',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='mastery_estimates'
    )
    
    # Mastery level (0-100)
    mastery_level = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Confidence in the estimate (0-100)'
    )
    
    # History
    assessment_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of assessments contributing to this estimate'
    )
    last_assessment_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'mastery estimate'
        verbose_name_plural = 'mastery estimates'
        unique_together = ['user', 'outcome_tag', 'community']
        ordering = ['-mastery_level']
    
    def __str__(self):
        return f'{self.user.email} - {self.outcome_tag}: {self.mastery_level}%'

