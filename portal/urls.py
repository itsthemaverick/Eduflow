# ==========================================
# PROJECT JHEP NGO PORTAL - URL ROUTING (PORTAL APP)
# ==========================================
# Maps web browser endpoints to corresponding Django view handler functions.

from django.urls import path
from . import views

urlpatterns = [
    # --------------------------------------
    # 1. PUBLIC & AUTHENTICATION ROUTES
    # --------------------------------------
    path('', views.landing_view, name='landing'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # --------------------------------------
    path('dashboard/', views.teacher_dashboard_view, name='my_dashboard'),
    path('teacher/<int:teacher_id>/', views.teacher_dashboard_view, name='teacher_dashboard'),
    path('teacher/<int:teacher_id>/profile/', views.teacher_profile_view, name='teacher_profile'),
    path('lesson/<int:lesson_id>/', views.lesson_detail_view, name='lesson_detail'),
    
    # Progress Toggles
    path('lesson/<int:lesson_id>/toggle-content/<int:content_id>/', views.toggle_content_completion, name='toggle_content_completion'),
    path('lesson/<int:lesson_id>/toggle-completion/', views.toggle_lesson_completion, name='toggle_lesson_completion'),

    # --------------------------------------
    # 3. ADMINISTRATIVE CONTROL PANEL ROUTES
    # --------------------------------------
    path('admin-panel/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-panel/admins/add/', views.admin_add_admin, name='admin_add_admin'),
    path('admin-panel/admins/<int:teacher_id>/edit/', views.admin_edit_admin, name='admin_edit_admin'),
    path('admin-panel/admins/<int:teacher_id>/delete/', views.admin_delete_admin, name='admin_delete_admin'),
    path('admin-panel/teachers/add/', views.admin_add_teacher, name='admin_add_teacher'),
    path('admin-panel/teachers/<int:teacher_id>/edit/', views.admin_edit_teacher, name='admin_edit_teacher'),
    path('admin-panel/teachers/<int:teacher_id>/set-password/', views.admin_set_teacher_password, name='admin_set_teacher_password'),
    path('admin-panel/teachers/<int:teacher_id>/delete/', views.admin_delete_teacher, name='admin_delete_teacher'),
    path('admin-panel/teachers/<int:teacher_id>/assign/', views.admin_update_assignments, name='admin_assign_lessons'),
    path('admin-panel/lessons/create/', views.admin_create_lesson, name='admin_create_lesson'),
    path('admin-panel/lessons/<int:lesson_id>/add-resource/', views.admin_add_lesson_resource, name='admin_add_lesson_resource'),
    path('admin-panel/lessons/<int:lesson_id>/delete/', views.admin_delete_lesson, name='admin_delete_lesson'),

    # Partner Schools Management
    path('admin-panel/partner-schools/add/', views.admin_add_partner_school, name='admin_add_partner_school'),
    path('admin-panel/partner-schools/<int:school_id>/edit/', views.admin_edit_partner_school, name='admin_edit_partner_school'),
    path('admin-panel/partner-schools/<int:school_id>/delete/', views.admin_delete_partner_school, name='admin_delete_partner_school'),

    # Reviews Management
    path('admin-panel/reviews/add/', views.admin_add_review, name='admin_add_review'),
    path('admin-panel/reviews/<int:review_id>/edit/', views.admin_edit_review, name='admin_edit_review'),
    path('admin-panel/reviews/<int:review_id>/delete/', views.admin_delete_review, name='admin_delete_review'),
]
