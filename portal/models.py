# ==========================================
# PROJECT JHEP NGO PORTAL - DJANGO MODELS
# ==========================================
# This file defines the database schema and object relational mappings (ORM)
# for Teachers, Lessons, Content Items, Progress Tracking, and Audit Login Logs.

from django.db import models
from django.utils import timezone

# ------------------------------------------
# 1. TEACHER PROFILE MODEL
# ------------------------------------------
class Teacher(models.Model):
    """
    Represents an educator in the NGO rural school network.
    Stores professional credentials, school region assignment, and system role.
    """
    username = models.CharField(max_length=50, unique=True, help_text="Unique identifier for portal login")
    password = models.CharField(max_length=128, default="teacher123", help_text="User portal login password")
    name = models.CharField(max_length=100, help_text="Full display name of the educator")
    email = models.EmailField(unique=True, help_text="Official contact email address")
    school_region = models.CharField(max_length=100, help_text="Assigned school district or geographic community region")
    subject_specialty = models.CharField(max_length=100, help_text="Primary domain expertise (e.g., Mathematics, Science)")
    joined_date = models.DateField(default=timezone.now, help_text="Date educator joined the NGO learning network")
    avatar = models.URLField(default="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=200", help_text="URL to profile avatar image")
    role = models.CharField(max_length=20, default="Teacher", choices=[('Teacher', 'Teacher'), ('Admin', 'Admin')], help_text="System access privilege role")

    @property
    def assigned_lesson_ids(self):
        """Returns a set of lesson IDs assigned to this teacher."""
        return set(self.assignments.values_list('lesson_id', flat=True))

    def __str__(self):
        return f"{self.name} ({self.school_region})"

    class Meta:
        ordering = ['name']


# ------------------------------------------
# 2. EDUCATIONAL LESSON MODEL
# ------------------------------------------
class Lesson(models.Model):
    """
    Represents an educational curriculum unit uploaded by administrators.
    Contains metadata, subject classification, and media resources.
    """
    title = models.CharField(max_length=200, help_text="Title of the educational module")
    subject = models.CharField(max_length=100, help_text="Academic discipline category (e.g., Mathematics, Physics, English)")
    grade = models.CharField(max_length=50, help_text="Target student grade level (e.g., Grade 6, Grade 8)")
    duration = models.CharField(max_length=50, default="45 min", help_text="Estimated delivery or study time")
    summary = models.TextField(help_text="Detailed overview of learning objectives and key topics covered")
    thumbnail = models.URLField(help_text="Cover image asset URL")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.subject} ({self.grade})"

    class Meta:
        ordering = ['-created_at']


# ------------------------------------------
# 3. LESSON CONTENT ITEM MODEL
# ------------------------------------------
class LessonContent(models.Model):
    """
    Represents individual multimedia items or resources contained within a Lesson.
    Supports Videos, PDF Worksheets, Quizzes, and Interactive Slides.
    """
    CONTENT_TYPES = [
        ('video', 'Video Lecture'),
        ('pdf', 'PDF Worksheet / Guide'),
        ('quiz', 'Interactive Quiz'),
        ('interactive', 'Slide Deck / Presentation'),
    ]

    lesson = models.ForeignKey(Lesson, related_name='contents', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, help_text="Resource display title")
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='video')
    url = models.URLField(help_text="Direct link to hosted video, PDF document, or interactive media")
    description = models.TextField(blank=True, help_text="Instructions or summary for this content item")
    order = models.PositiveIntegerField(default=1, help_text="Display sequence order within the lesson")

    def __str__(self):
        return f"[{self.get_content_type_display()}] {self.title}"

    class Meta:
        ordering = ['order']


# ------------------------------------------
# 4. TEACHER LESSON ASSIGNMENT & PROGRESS
# ------------------------------------------
class TeacherLessonAssignment(models.Model):
    """
    Tracks teacher-lesson assignments and progress completion metrics.
    Stores completed content item IDs in JSON field for granular tracking.
    """
    teacher = models.ForeignKey(Teacher, related_name='assignments', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='teacher_assignments', on_delete=models.CASCADE)
    completed = models.BooleanField(default=False, help_text="Status flag indicating full lesson completion")
    completed_content_ids = models.JSONField(default=list, blank=True, help_text="List of completed content item IDs")
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('teacher', 'lesson')

    def __str__(self):
        status = "Completed" if self.completed else "In Progress"
        return f"{self.teacher.name} -> {self.lesson.title} ({status})"


# ------------------------------------------
# 5. AUDIT LOGIN HISTORY LOG
# ------------------------------------------
class LoginHistory(models.Model):
    """
    Records security audit events whenever a user authenticates in the portal.
    """
    username = models.CharField(max_length=50)
    user_role = models.CharField(max_length=20)
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.CharField(max_length=45, default="127.0.0.1")
    status = models.CharField(max_length=20, default="Success")

    def __str__(self):
        return f"{self.username} ({self.user_role}) logged in at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-timestamp']


# ------------------------------------------
# 6. PARTNER SCHOOL MODEL
# ------------------------------------------
class PartnerSchool(models.Model):
    """
    Represents a partner school or rural educational institute collaborating with Project Jhep.
    """
    name = models.CharField(max_length=200, help_text="Official name of the partner school")
    location = models.CharField(max_length=150, help_text="District, region, or state")
    logo_url = models.URLField(default="https://images.unsplash.com/photo-1580582932707-520aed937b7b?auto=format&fit=crop&q=80&w=200", help_text="URL to school logo or photo")
    students_impacted = models.CharField(max_length=50, default="300+ Students", help_text="e.g. 450+ Students")
    description = models.TextField(blank=True, help_text="Brief summary of collaboration or school background")
    is_active = models.BooleanField(default=True, help_text="Whether to display on the public landing page")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.location})"

    class Meta:
        ordering = ['name']


# ------------------------------------------
# 7. EDUCATOR REVIEWS & TESTIMONIALS MODEL
# ------------------------------------------
class Review(models.Model):
    """
    Represents testimonials and reviews from teachers and headmasters.
    """
    author_name = models.CharField(max_length=100, help_text="Full name of reviewer")
    author_role = models.CharField(max_length=100, help_text="Designation/Role, e.g. Grade 8 Science Educator")
    school_name = models.CharField(max_length=150, blank=True, help_text="Associated school or district")
    author_avatar = models.URLField(default="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=200", help_text="URL to avatar photo")
    rating = models.PositiveIntegerField(default=5, help_text="Star rating out of 5")
    content = models.TextField(help_text="Detailed review or quote from the educator")
    is_active = models.BooleanField(default=True, help_text="Whether to display in the landing page carousel")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author_name} ({self.author_role}) - {self.rating} Stars"

    class Meta:
        ordering = ['-created_at']

