# ==========================================
# PROJECT JHEP NGO PORTAL - VIEWS HANDLER
# ==========================================
# Contains controller functions and request handlers for Landing,
# Authentication, Teacher Dashboard, Lesson Viewer, and Admin Control Panel.

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Teacher, Lesson, LessonContent, TeacherLessonAssignment, LoginHistory, PartnerSchool, Review
from .seed import seed_database

# ------------------------------------------
# HELPER: Ensure Database is Seeded on First Request
# ------------------------------------------
def _ensure_seeded():
    """Auto-seeds initial records if table is empty."""
    seed_database()


# ------------------------------------------
# HELPER: Check Session Auth & Role
# ------------------------------------------
def get_current_user(request):
    """Retrieves current logged-in user dict or None from request session."""
    return request.session.get('user', None)


# ------------------------------------------
# 1. LANDING PAGE VIEW
# ------------------------------------------
def landing_view(request):
    """
    Renders public home portal featuring NGO mission stats, featured modules,
    and system access call-to-actions.
    """
    _ensure_seeded()
    user = get_current_user(request)

    teachers = Teacher.objects.filter(role='Teacher')
    lessons = Lesson.objects.all()
    
    # Calculate Portal Metrics
    total_teachers = teachers.count()
    total_lessons = lessons.count()
    total_contents = LessonContent.objects.count()
    today_logins = LoginHistory.objects.filter(timestamp__date=timezone.now().date()).count()

    stats = {
        'total_teachers': total_teachers,
        'total_lessons': total_lessons,
        'total_content_files': total_contents,
        'today_logins': today_logins,
    }

    partner_schools = PartnerSchool.objects.filter(is_active=True)
    reviews = Review.objects.filter(is_active=True)

    context = {
        'user': user,
        'stats': stats,
        'featured_lessons': lessons[:6],
        'partner_schools': partner_schools,
        'reviews': reviews,
        'page': 'landing'
    }
    return render(request, 'portal/landing.html', context)


# ------------------------------------------
# 2. LOGIN VIEW (Teacher & Admin)
# ------------------------------------------
def login_view(request):
    """
    Handles authentication for Teachers and Administrators.
    Validates credentials and writes audit history record.
    """
    _ensure_seeded()
    user = get_current_user(request)

    # Redirect if already logged in
    if user:
        if user['role'] == 'Admin':
            return redirect('admin_dashboard')
        return redirect('teacher_dashboard', teacher_id=user['id'])

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        role = request.POST.get('role', 'Teacher').strip()

        # Check credentials in Teacher model
        teacher = Teacher.objects.filter(username__iexact=username, role=role).first()

        if teacher:
            # Validate user password
            if password == teacher.password:
                # Security: Cycle session key to prevent Session Fixation attacks
                request.session.cycle_key()

                # Save session user object
                user_data = {
                    'id': teacher.id,
                    'username': teacher.username,
                    'name': teacher.name,
                    'role': teacher.role,
                    'avatar': teacher.avatar,
                    'school_region': teacher.school_region,
                    'subject_specialty': teacher.subject_specialty,
                }
                request.session['user'] = user_data

                # Create Audit Log
                LoginHistory.objects.create(
                    username=teacher.username,
                    user_role=teacher.role,
                    timestamp=timezone.now(),
                    ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
                    status='Success'
                )

                messages.success(request, f"Welcome back, {teacher.name}!")
                if teacher.role == 'Admin':
                    return redirect('admin_dashboard')
                return redirect('teacher_dashboard', teacher_id=teacher.id)

        # Authentication Failed
        LoginHistory.objects.create(
            username=username if username else "Unknown",
            user_role=role,
            timestamp=timezone.now(),
            ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1'),
            status='Failed'
        )
        messages.error(request, "Invalid username or password. Please try again.")

    return render(request, 'portal/login.html', {'page': 'login'})


# ------------------------------------------
# 3. LOGOUT VIEW
# ------------------------------------------
def logout_view(request):
    """Clears user session and redirects back to public portal home."""
    request.session.flush()
    messages.info(request, "You have been logged out safely.")
    return redirect('landing')


# ------------------------------------------
# 4. TEACHER DASHBOARD VIEW
# ------------------------------------------
def teacher_dashboard_view(request, teacher_id=None):
    """
    Renders personalized dashboard for educators showing assigned lessons,
    completion metrics, subject filters, and progress statistics.
    """
    _ensure_seeded()
    user = get_current_user(request)

    if not user:
        messages.warning(request, "Please log in to access the educator dashboard.")
        return redirect('login')

    # Default to current logged-in user if teacher_id not provided or if viewing own
    if teacher_id:
        teacher = get_object_or_404(Teacher, id=teacher_id)
        # Security: Enforce authorization check (Teachers can only view their own dashboard)
        if user['role'] != 'Admin' and teacher.id != user['id']:
            messages.warning(request, "Access restricted to your assigned dashboard.")
            return redirect('teacher_dashboard', teacher_id=user['id'])
    else:
        teacher = get_object_or_404(Teacher, id=user['id'])

    # Fetch assigned lessons and progress records
    assignments = TeacherLessonAssignment.objects.filter(teacher=teacher).select_related('lesson')
    assigned_lessons = [a.lesson for a in assignments]

    # Map progress state for easy template access
    progress_map = {}
    completed_count = 0
    for a in assignments:
        progress_map[a.lesson.id] = {
            'completed': a.completed,
            'completed_content_ids': a.completed_content_ids or [],
            'last_accessed': a.last_accessed
        }
        if a.completed:
            completed_count += 1

    total_assigned = len(assigned_lessons)
    completion_percentage = int((completed_count / total_assigned * 100)) if total_assigned > 0 else 0

    # Search & Filter handling
    subject_filter = request.GET.get('subject', 'All')
    search_query = request.GET.get('q', '').strip().lower()

    filtered_lessons = []
    for l in assigned_lessons:
        matches_subject = (subject_filter == 'All') or (l.subject == subject_filter)
        matches_search = not search_query or (search_query in l.title.lower() or search_query in l.summary.lower())
        if matches_subject and matches_search:
            filtered_lessons.append(l)

    # Unique subjects for filter buttons
    all_subjects = list(set([l.subject for l in assigned_lessons]))

    context = {
        'user': user,
        'teacher': teacher,
        'assigned_lessons': filtered_lessons,
        'all_assigned_count': total_assigned,
        'progress_map': progress_map,
        'completed_count': completed_count,
        'completion_percentage': completion_percentage,
        'all_subjects': all_subjects,
        'selected_subject': subject_filter,
        'search_query': search_query,
        'page': 'teacher_dashboard'
    }
    return render(request, 'portal/teacher_dashboard.html', context)


# ------------------------------------------
# 5. LESSON VIEWER & CONTENT DETAIL
# ------------------------------------------
def lesson_detail_view(request, lesson_id):
    """
    Renders detailed interactive lesson unit with multimedia resources
    (videos, slides, PDF guides) and content completion toggles.
    Requires authentication.
    """
    _ensure_seeded()
    user = get_current_user(request)

    if not user:
        messages.warning(request, "Authentication required. Please log in to preview or access lesson content.")
        return redirect('login')

    lesson = get_object_or_404(Lesson, id=lesson_id)
    contents = lesson.contents.all()

    active_content_id = request.GET.get('active_content')
    active_content = None
    if active_content_id:
        try:
            active_content = contents.filter(id=int(active_content_id)).first()
        except (ValueError, TypeError):
            active_content = None
    if not active_content:
        active_content = contents.first()

    assignment = None
    completed_content_ids = []
    is_lesson_completed = False

    if user and user.get('role') == 'Teacher':
        teacher = Teacher.objects.filter(id=user.get('id')).first()
        if teacher:
            assignment, _ = TeacherLessonAssignment.objects.get_or_create(
                teacher=teacher,
                lesson=lesson,
                defaults={'completed': False, 'completed_content_ids': []}
            )
            completed_content_ids = assignment.completed_content_ids or []
            is_lesson_completed = assignment.completed

    context = {
        'user': user,
        'lesson': lesson,
        'contents': contents,
        'active_content': active_content,
        'assignment': assignment,
        'completed_content_ids': completed_content_ids,
        'is_lesson_completed': is_lesson_completed,
        'page': 'lesson_viewer'
    }
    return render(request, 'portal/lesson_detail.html', context)


# ------------------------------------------
# 6. TOGGLE CONTENT ITEM COMPLETION
# ------------------------------------------
def toggle_content_completion(request, lesson_id, content_id):
    """
    Toggles completion status for an individual content item (e.g., video watched)
    and recalculates overall lesson completion.
    """
    user = get_current_user(request)
    if not user or user['role'] != 'Teacher':
        return HttpResponseForbidden("Teacher login required.")

    teacher = get_object_or_404(Teacher, id=user['id'])
    lesson = get_object_or_404(Lesson, id=lesson_id)

    assignment, _ = TeacherLessonAssignment.objects.get_or_create(
        teacher=teacher,
        lesson=lesson,
        defaults={'completed': False, 'completed_content_ids': []}
    )

    ids = assignment.completed_content_ids or []
    if content_id in ids:
        ids.remove(content_id)
    else:
        ids.append(content_id)

    assignment.completed_content_ids = ids
    
    # Auto-complete lesson if all contents are checked
    total_contents = lesson.contents.count()
    if total_contents > 0 and len(ids) >= total_contents:
        assignment.completed = True
    elif len(ids) < total_contents:
        assignment.completed = False

    assignment.save()

    messages.success(request, "Progress updated!")
    return redirect('lesson_detail', lesson_id=lesson_id)


# ------------------------------------------
# 7. TOGGLE FULL LESSON COMPLETION
# ------------------------------------------
def toggle_lesson_completion(request, lesson_id):
    """Toggles macro completion flag for a lesson."""
    user = get_current_user(request)
    if not user or user['role'] != 'Teacher':
        return HttpResponseForbidden("Teacher login required.")

    teacher = get_object_or_404(Teacher, id=user['id'])
    lesson = get_object_or_404(Lesson, id=lesson_id)

    assignment, _ = TeacherLessonAssignment.objects.get_or_create(
        teacher=teacher,
        lesson=lesson,
        defaults={'completed': False, 'completed_content_ids': []}
    )

    assignment.completed = not assignment.completed
    assignment.save()

    messages.success(request, f"Lesson completion set to {'Completed' if assignment.completed else 'In Progress'}.")
    
    # Redirect back to caller (dashboard or detail view)
    next_url = request.META.get('HTTP_REFERER', None)
    if next_url:
        return redirect(next_url)
    return redirect('teacher_dashboard', teacher_id=teacher.id)


# ------------------------------------------
# 8. ADMIN CONTROL PANEL VIEW
# ------------------------------------------
def admin_dashboard_view(request):
    """
    Renders administrative control dashboard for curriculum officers.
    Includes educator list, lesson catalog manager, statistics, and audit logs.
    """
    _ensure_seeded()
    user = get_current_user(request)

    if not user or user['role'] != 'Admin':
        messages.error(request, "Administrator privileges required.")
        return redirect('login')

    teachers = Teacher.objects.filter(role='Teacher').order_by('name')
    admins = Teacher.objects.filter(role='Admin').order_by('name')
    lessons = Lesson.objects.all().order_by('-created_at')
    login_logs = LoginHistory.objects.all()[:30]
    partner_schools = PartnerSchool.objects.all().order_by('-created_at')
    reviews = Review.objects.all().order_by('-created_at')

    # Overall system metrics
    stats = {
        'total_teachers': teachers.count(),
        'total_admins': admins.count(),
        'total_lessons': lessons.count(),
        'total_content_files': LessonContent.objects.count(),
        'active_assignments': TeacherLessonAssignment.objects.count(),
        'completed_assignments': TeacherLessonAssignment.objects.filter(completed=True).count(),
        'today_logins': LoginHistory.objects.filter(timestamp__date=timezone.now().date()).count(),
        'total_partner_schools': partner_schools.count(),
        'total_reviews': reviews.count(),
    }

    context = {
        'user': user,
        'teachers': teachers,
        'admins': admins,
        'lessons': lessons,
        'login_logs': login_logs,
        'partner_schools': partner_schools,
        'reviews': reviews,
        'stats': stats,
        'page': 'admin_panel'
    }
    return render(request, 'portal/admin_panel.html', context)


# ------------------------------------------
# 8b. ADMIN: ADD NEW ADMINISTRATOR
# ------------------------------------------
@csrf_exempt
def admin_add_admin(request):
    """Creates a new Administrator profile in the NGO network."""
    user = get_current_user(request)
    if not user or user['role'] != 'Admin':
        return HttpResponseForbidden("Administrator privileges required.")

    if request.method != 'POST':
        return HttpResponseForbidden("POST request required.")

    name = request.POST.get('name', '').strip()
    username = request.POST.get('username', '').strip().lower()
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '').strip() or "adminpassword"
    school_region = request.POST.get('school_region', '').strip() or "Central Admin HQ"
    subject_specialty = request.POST.get('subject_specialty', '').strip() or "System Administrator"

    if name and username and email:
        if Teacher.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken.")
        elif Teacher.objects.filter(email=email).exists():
            messages.error(request, f"Email '{email}' is already registered to another account.")
        else:
            try:
                Teacher.objects.create(
                    name=name,
                    username=username,
                    email=email,
                    password=password,
                    school_region=school_region,
                    subject_specialty=subject_specialty,
                    joined_date=timezone.now().date(),
                    role='Admin'
                )
                messages.success(request, f"Administrator profile '{name}' (@{username}) created successfully!")
            except Exception as e:
                messages.error(request, f"Could not create administrator profile: {str(e)}")
    else:
        messages.error(request, "Please fill in all required fields (Name, Username, Email).")

    return redirect('admin_dashboard')


# ------------------------------------------
# 8c. ADMIN: EDIT & DELETE ADMINISTRATOR
# ------------------------------------------
@csrf_exempt
def admin_edit_admin(request, teacher_id):
    """Updates an existing administrator profile."""
    user = get_current_user(request)
    if not user or user['role'] != 'Admin':
        return HttpResponseForbidden("Administrator privileges required.")

    if request.method != 'POST':
        return HttpResponseForbidden("POST request required.")

    admin_obj = get_object_or_404(Teacher, id=teacher_id, role='Admin')
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '').strip()
    school_region = request.POST.get('school_region', '').strip()
    subject_specialty = request.POST.get('subject_specialty', '').strip()

    if name and email:
        if Teacher.objects.filter(email=email).exclude(id=admin_obj.id).exists():
            messages.error(request, f"Email '{email}' is already registered to another account.")
        else:
            admin_obj.name = name
            admin_obj.email = email
            if password:
                admin_obj.password = password
            if school_region:
                admin_obj.school_region = school_region
            if subject_specialty:
                admin_obj.subject_specialty = subject_specialty
            try:
                admin_obj.save()
                messages.success(request, f"Updated administrator profile for '{admin_obj.name}'.")
            except Exception as e:
                messages.error(request, f"Could not update administrator profile: {str(e)}")
    else:
        messages.error(request, "Name and Email are required.")

    return redirect('admin_dashboard')


@csrf_exempt
def admin_delete_admin(request, teacher_id):
    """Removes an administrator account from the portal."""
    user = get_current_user(request)
    if not user or user['role'] != 'Admin':
        return HttpResponseForbidden("Administrator privileges required.")

    if request.method != 'POST':
        return HttpResponseForbidden("POST request required.")

    admin_obj = get_object_or_404(Teacher, id=teacher_id, role='Admin')

    if user and user.get('id') == admin_obj.id:
        messages.error(request, "You cannot delete your own administrator account while logged in.")
        return redirect('admin_dashboard')

    name = admin_obj.name
    admin_obj.delete()
    messages.success(request, f"Administrator account for '{name}' was successfully deleted.")
    return redirect('admin_dashboard')


# ------------------------------------------
# 9. ADMIN: ADD NEW TEACHER
# ------------------------------------------
@csrf_exempt
def admin_add_teacher(request):
    """Creates a new Teacher profile in the NGO network."""
    user = get_current_user(request)
    if not user or user['role'] != 'Admin':
        return HttpResponseForbidden("Administrator privileges required.")

    if request.method != 'POST':
        return HttpResponseForbidden("POST request required.")

    name = request.POST.get('name', '').strip()
    username = request.POST.get('username', '').strip().lower()
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '').strip() or "teacher123"
    school_region = request.POST.get('school_region', '').strip()
    subject_specialty = request.POST.get('subject_specialty', '').strip()

    if name and username and email:
        if Teacher.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken.")
        elif Teacher.objects.filter(email=email).exists():
            messages.error(request, f"Email '{email}' is already registered to another account.")
        else:
            try:
                Teacher.objects.create(
                    name=name,
                    username=username,
                    email=email,
                    password=password,
                    school_region=school_region or "District HQ",
                    subject_specialty=subject_specialty or "General",
                    joined_date=timezone.now().date(),
                    role='Teacher'
                )
                messages.success(request, f"Teacher profile '{name}' added successfully with assigned password!")
            except Exception as e:
                messages.error(request, f"Could not create teacher profile: {str(e)}")
    else:
        messages.error(request, "Please fill in all required fields.")

    return redirect('admin_dashboard')


# ------------------------------------------
# 10. ADMIN: EDIT & DELETE TEACHER
# ------------------------------------------
@csrf_exempt
def admin_edit_teacher(request, teacher_id):
    """Updates an existing teacher profile in the NGO network."""
    user = get_current_user(request)
    if not user or user['role'] != 'Admin':
        return HttpResponseForbidden("Administrator privileges required.")

    if request.method != 'POST':
        return HttpResponseForbidden("POST request required.")

    teacher = get_object_or_404(Teacher, id=teacher_id)
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '').strip()
    school_region = request.POST.get('school_region', '').strip()
    subject_specialty = request.POST.get('subject_specialty', '').strip()

    if name and email:
        if Teacher.objects.filter(email=email).exclude(id=teacher.id).exists():
            messages.error(request, f"Email '{email}' is already registered to another account.")
        else:
            teacher.name = name
            teacher.email = email
            if password:
                teacher.password = password
            if school_region:
                teacher.school_region = school_region
            if subject_specialty:
                teacher.subject_specialty = subject_specialty
            try:
                teacher.save()
                messages.success(request, f"Updated profile and security settings for '{teacher.name}'.")
            except Exception as e:
                messages.error(request, f"Could not update profile: {str(e)}")
    else:
        messages.error(request, "Name and Email are required.")

    return redirect('admin_dashboard')


@csrf_exempt
def admin_set_teacher_password(request, teacher_id):
    """Allows Administrator to directly view and set password for a Teacher profile."""
    user = get_current_user(request)
    if not user or user['role'] != 'Admin':
        return HttpResponseForbidden("Administrator privileges required.")

    if request.method != 'POST':
        return HttpResponseForbidden("POST request required.")

    teacher = get_object_or_404(Teacher, id=teacher_id)
    new_password = request.POST.get('password', '').strip()

    if new_password:
        teacher.password = new_password
        teacher.save()
        messages.success(request, f"Password for educator '{teacher.name}' (@{teacher.username}) updated successfully!")
    else:
        messages.error(request, "Password cannot be empty.")

    next_url = request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('admin_dashboard')


@csrf_exempt
def admin_delete_teacher(request, teacher_id):
    """Removes a teacher account from the portal."""
    user = get_current_user(request)
    if not user or user['role'] != 'Admin':
        return HttpResponseForbidden("Administrator privileges required.")

    if request.method != 'POST':
        return HttpResponseForbidden("POST request required.")

    teacher = get_object_or_404(Teacher, id=teacher_id)
    name = teacher.name
    teacher.delete()
    messages.success(request, f"Educator profile for '{name}' was successfully deleted.")
    return redirect('admin_dashboard')


# ------------------------------------------
# 11. ADMIN: CREATE LESSON MODULE
# ------------------------------------------
@csrf_exempt
def admin_create_lesson(request):
    """Creates a new educational lesson module and attached media resources."""
    user = get_current_user(request)
    if not user or user['role'] != 'Admin':
        return HttpResponseForbidden("Administrator privileges required.")

    if request.method != 'POST':
        return HttpResponseForbidden("POST request required.")

    title = request.POST.get('title', '').strip()
    subject = request.POST.get('subject', '').strip()
    grade = request.POST.get('grade', '').strip()
    duration = request.POST.get('duration', '45 mins').strip()
    summary = request.POST.get('summary', '').strip()
    thumbnail = request.POST.get('thumbnail', '').strip()
    
    content_title = request.POST.get('content_title', '').strip()
    content_type = request.POST.get('content_type', 'video').strip()
    content_url = request.POST.get('content_url', '').strip()

    if title and subject and grade:
        lesson = Lesson.objects.create(
            title=title,
            subject=subject,
            grade=grade,
            duration=duration,
            summary=summary or "Comprehensive curriculum module for classroom delivery.",
            thumbnail=thumbnail or "https://images.unsplash.com/photo-1509228468518-180dd4864904?auto=format&fit=crop&q=80&w=600"
        )

        # Create primary content item if provided
        if content_title and content_url:
            LessonContent.objects.create(
                lesson=lesson,
                title=content_title,
                content_type=content_type,
                url=content_url,
                description="Primary learning resource",
                order=1
            )

        messages.success(request, f"Lesson '{title}' created successfully!")
    else:
        messages.error(request, "Title, Subject, and Grade are required.")

    return redirect('admin_dashboard')


# ------------------------------------------
# 12. ADMIN: DELETE & MANAGE LESSON RESOURCES
# ------------------------------------------
@csrf_exempt
def admin_add_lesson_resource(request, lesson_id):
    """Adds a new content resource item to an existing lesson module."""
    user = get_current_user(request)
    if not user or user['role'] != 'Admin':
        return HttpResponseForbidden("Administrator privileges required.")

    if request.method != 'POST':
        return HttpResponseForbidden("POST request required.")

    lesson = get_object_or_404(Lesson, id=lesson_id)
    title = request.POST.get('content_title', '').strip()
    content_type = request.POST.get('content_type', 'video').strip()
    url = request.POST.get('content_url', '').strip()
    description = request.POST.get('description', 'Supplementary classroom material.').strip()

    if title and url:
        current_count = lesson.contents.count()
        LessonContent.objects.create(
            lesson=lesson,
            title=title,
            content_type=content_type,
            url=url,
            description=description,
            order=current_count + 1
        )
        messages.success(request, f"Attached '{title}' to lesson '{lesson.title}'.")
    else:
        messages.error(request, "Resource Title and URL are required.")

    return redirect('admin_dashboard')


@csrf_exempt
def admin_delete_lesson(request, lesson_id):
    """Deletes a lesson module from system catalog."""
    user = get_current_user(request)
    if not user or user['role'] != 'Admin':
        return HttpResponseForbidden("Administrator privileges required.")

    if request.method != 'POST':
        return HttpResponseForbidden("POST request required.")

    lesson = get_object_or_404(Lesson, id=lesson_id)
    title = lesson.title
    lesson.delete()
    messages.success(request, f"Lesson module '{title}' was successfully deleted from catalog.")
    return redirect('admin_dashboard')


# ------------------------------------------
# 13. ADMIN: UPDATE TEACHER LESSON ASSIGNMENTS
# ------------------------------------------
@csrf_exempt
def admin_update_assignments(request, teacher_id):
    """Updates lesson assignments for a specific teacher."""
    user = get_current_user(request)
    if not user or user['role'] != 'Admin':
        return HttpResponseForbidden("Administrator privileges required.")

    if request.method != 'POST':
        return HttpResponseForbidden("POST request required.")

    teacher = get_object_or_404(Teacher, id=teacher_id)
    selected_lesson_ids = request.POST.getlist('lessons')
    
    # Clear existing assignments
    TeacherLessonAssignment.objects.filter(teacher=teacher).delete()

    # Re-assign selected lessons
    for lid in selected_lesson_ids:
        lesson = Lesson.objects.get(id=lid)
        TeacherLessonAssignment.objects.create(
            teacher=teacher,
            lesson=lesson,
            completed=False,
            completed_content_ids=[]
        )

    messages.success(request, f"Assigned {len(selected_lesson_ids)} lessons to {teacher.name}.")
    return redirect('admin_dashboard')


# ------------------------------------------
# 14. TEACHER PROFILE MODAL / VIEW
# ------------------------------------------
def teacher_profile_view(request, teacher_id):
    """Renders teacher modal / detail information page. Requires authentication."""
    _ensure_seeded()
    user = get_current_user(request)

    if not user:
        messages.warning(request, "Authentication required. Please log in to view educator profiles.")
        return redirect('login')

    teacher = get_object_or_404(Teacher, id=teacher_id)
    assignments = TeacherLessonAssignment.objects.filter(teacher=teacher).select_related('lesson')
    assigned_lessons = [a.lesson for a in assignments]
    
    # Audit log privacy: Only show detailed login logs to Admin or the account owner
    teacher_logs = []
    if user and (user.get('role') == 'Admin' or user.get('id') == teacher.id):
        teacher_logs = LoginHistory.objects.filter(username=teacher.username)[:15]

    context = {
        'user': user,
        'teacher': teacher,
        'assigned_lessons': assigned_lessons,
        'teacher_logs': teacher_logs,
        'page': 'teacher_profile'
    }
    return render(request, 'portal/teacher_profile.html', context)


# ------------------------------------------
# 15. ADMIN: PARTNER SCHOOL MANAGEMENT
# ------------------------------------------
@csrf_exempt
def admin_add_partner_school(request):
    """Creates a new partner school entry."""
    user = get_current_user(request)
    if not user or user['role'] != 'Admin':
        return HttpResponseForbidden("Administrator privileges required.")

    if request.method != 'POST':
        return HttpResponseForbidden("POST request required.")

    name = request.POST.get('name', '').strip()
    location = request.POST.get('location', '').strip()
    logo_url = request.POST.get('logo_url', '').strip() or "https://images.unsplash.com/photo-1580582932707-520aed937b7b?auto=format&fit=crop&q=80&w=300"
    students_impacted = request.POST.get('students_impacted', '').strip() or "300+ Students"
    description = request.POST.get('description', '').strip()
    is_active = request.POST.get('is_active') in ['on', 'true', '1']

    if name and location:
        PartnerSchool.objects.create(
            name=name,
            location=location,
            logo_url=logo_url,
            students_impacted=students_impacted,
            description=description,
            is_active=is_active
        )
        messages.success(request, f"Partner school '{name}' registered successfully.")
    else:
        messages.error(request, "School Name and Location are required.")

    return redirect('admin_dashboard')


@csrf_exempt
def admin_edit_partner_school(request, school_id):
    """Updates an existing partner school entry."""
    user = get_current_user(request)
    if not user or user['role'] != 'Admin':
        return HttpResponseForbidden("Administrator privileges required.")

    if request.method != 'POST':
        return HttpResponseForbidden("POST request required.")

    school = get_object_or_404(PartnerSchool, id=school_id)
    name = request.POST.get('name', '').strip()
    location = request.POST.get('location', '').strip()
    logo_url = request.POST.get('logo_url', '').strip()
    students_impacted = request.POST.get('students_impacted', '').strip()
    description = request.POST.get('description', '').strip()
    is_active = request.POST.get('is_active') in ['on', 'true', '1']

    if name and location:
        school.name = name
        school.location = location
        if logo_url:
            school.logo_url = logo_url
        if students_impacted:
            school.students_impacted = students_impacted
        school.description = description
        school.is_active = is_active
        school.save()
        messages.success(request, f"Updated partner school '{school.name}'.")
    else:
        messages.error(request, "School Name and Location are required.")

    return redirect('admin_dashboard')


@csrf_exempt
def admin_delete_partner_school(request, school_id):
    """Deletes a partner school entry."""
    user = get_current_user(request)
    if not user or user['role'] != 'Admin':
        return HttpResponseForbidden("Administrator privileges required.")

    if request.method != 'POST':
        return HttpResponseForbidden("POST request required.")

    school = get_object_or_404(PartnerSchool, id=school_id)
    name = school.name
    school.delete()
    messages.success(request, f"Partner school '{name}' was removed.")
    return redirect('admin_dashboard')


# ------------------------------------------
# 16. ADMIN: REVIEWS & TESTIMONIALS MANAGEMENT
# ------------------------------------------
@csrf_exempt
def admin_add_review(request):
    """Creates a new educator review/testimonial."""
    user = get_current_user(request)
    if not user or user['role'] != 'Admin':
        return HttpResponseForbidden("Administrator privileges required.")

    if request.method != 'POST':
        return HttpResponseForbidden("POST request required.")

    author_name = request.POST.get('author_name', '').strip()
    author_role = request.POST.get('author_role', '').strip()
    school_name = request.POST.get('school_name', '').strip()
    author_avatar = request.POST.get('author_avatar', '').strip() or "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=200"
    try:
        rating = int(request.POST.get('rating', 5))
    except ValueError:
        rating = 5
    content = request.POST.get('content', '').strip()
    is_active = request.POST.get('is_active') in ['on', 'true', '1']

    if author_name and content:
        Review.objects.create(
            author_name=author_name,
            author_role=author_role,
            school_name=school_name,
            author_avatar=author_avatar,
            rating=rating,
            content=content,
            is_active=is_active
        )
        messages.success(request, f"Review by '{author_name}' added successfully.")
    else:
        messages.error(request, "Author Name and Review Content are required.")

    return redirect('admin_dashboard')


@csrf_exempt
def admin_edit_review(request, review_id):
    """Updates an existing educator review."""
    user = get_current_user(request)
    if not user or user['role'] != 'Admin':
        return HttpResponseForbidden("Administrator privileges required.")

    if request.method != 'POST':
        return HttpResponseForbidden("POST request required.")

    review = get_object_or_404(Review, id=review_id)
    author_name = request.POST.get('author_name', '').strip()
    author_role = request.POST.get('author_role', '').strip()
    school_name = request.POST.get('school_name', '').strip()
    author_avatar = request.POST.get('author_avatar', '').strip()
    try:
        rating = int(request.POST.get('rating', 5))
    except ValueError:
        rating = 5
    content = request.POST.get('content', '').strip()
    is_active = request.POST.get('is_active') in ['on', 'true', '1']

    if author_name and content:
        review.author_name = author_name
        review.author_role = author_role
        review.school_name = school_name
        if author_avatar:
            review.author_avatar = author_avatar
        review.rating = rating
        review.content = content
        review.is_active = is_active
        review.save()
        messages.success(request, f"Updated review by '{review.author_name}'.")
    else:
        messages.error(request, "Author Name and Review Content are required.")

    return redirect('admin_dashboard')


@csrf_exempt
def admin_delete_review(request, review_id):
    """Deletes an educator review."""
    user = get_current_user(request)
    if not user or user['role'] != 'Admin':
        return HttpResponseForbidden("Administrator privileges required.")

    if request.method != 'POST':
        return HttpResponseForbidden("POST request required.")

    review = get_object_or_404(Review, id=review_id)
    author_name = review.author_name
    review.delete()
    messages.success(request, f"Review by '{author_name}' was removed.")
    return redirect('admin_dashboard')

