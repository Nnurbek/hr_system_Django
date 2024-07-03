from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import EmployeeProfile, Notification, Attendance, WorkSession
from .forms import EmployeeProfileForm, NotificationForm, UserCreationForm, UserForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpResponse
import csv
from django.utils.dateparse import parse_datetime
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_employee_list(request):
    employees = EmployeeProfile.objects.all()
    return render(request, 'hr_system/admin_employee_list.html', {'employees': employees})

@login_required
def employee_list(request):
    employees = EmployeeProfile.objects.all()
    if request.user.is_superuser:
        return render(request, 'hr_system/admin_employee_list.html', {'employees': employees})
    else:
        return render(request, 'hr_system/employee_list.html', {'employees': employees})
@login_required
def profile_view(request):
    profile, created = EmployeeProfile.objects.get_or_create(user=request.user, defaults={
        'position': 'Unknown',
        'total_hours_worked': 0,
        'total_earnings': 0,
    })
    notifications = Notification.objects.filter(recipient=request.user, read=False)
    work_sessions = WorkSession.objects.filter(user=request.user)
    has_active_session = WorkSession.objects.filter(user=request.user, end_time__isnull=True).exists()
    active_session = WorkSession.objects.filter(user=request.user, end_time__isnull=True).first()
    return render(request, 'hr_system/profile.html', {
        'profile': profile,
        'notifications': notifications,
        'work_sessions': work_sessions,
        'has_active_session': has_active_session,
        'active_session': active_session
    })



@login_required
def profile_edit(request):
    user = request.user
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile_view')
    else:
        form = UserForm(instance=user)
    return render(request, 'hr_system/profile_edit.html', {'form': form})
@user_passes_test(is_admin)
def admin_profile_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(EmployeeProfile, user=user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile.total_hours_worked = request.POST.get('total_hours_worked')
        profile.total_earnings = request.POST.get('total_earnings')
        if user_form.is_valid():
            user = user_form.save(commit=False)
            password = request.POST.get('password')
            if password:
                user.set_password(password)
            user.save()
            profile.save()
            return redirect('admin_employee_list')
    else:
        user_form = UserForm(instance=user)
    return render(request, 'hr_system/profile_edit.html', {
        'user': user,
        'user_form': user_form,
        'is_admin': True,
        'profile': profile
    })



@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(recipient=request.user)
    return render(request, 'hr_system/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    notification.read = True
    notification.save()
    return redirect('notifications_view')

@user_passes_test(is_admin)
def create_notification(request):
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_employee_list')
    else:
        form = NotificationForm()
    return render(request, 'hr_system/create_notification.html', {'form': form})

@user_passes_test(is_admin)
def mark_attendance(request, user_id, status):
    user = get_object_or_404(User, id=user_id)
    date = timezone.now().date()
    attendance, created = Attendance.objects.get_or_create(user=user, date=date, defaults={'status': status})
    if not created:
        attendance.status = status
        attendance.save()
    return redirect('admin_employee_list')

@user_passes_test(is_admin)
def generate_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employee_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Username', 'Position', 'Total Hours Worked', 'Total Earnings'])

    employees = EmployeeProfile.objects.all()
    for employee in employees:
        writer.writerow([employee.user.username, employee.position, employee.total_hours_worked, employee.total_earnings])

    return response

@login_required
def start_work(request):
    if not WorkSession.objects.filter(user=request.user, end_time__isnull=True).exists():
        WorkSession.objects.create(user=request.user, start_time=timezone.now())
    return redirect('profile_view')

@login_required
def end_work(request):
    if request.user.is_superuser:
        return redirect('admin_employee_list')
    session = WorkSession.objects.filter(user=request.user, end_time__isnull=True).first()
    if session:
        session.end_time = timezone.now()
        session.save()
         
        profile = get_object_or_404(EmployeeProfile, user=request.user)
        session_duration = session.duration()
        profile.total_hours_worked += session_duration
        profile.total_earnings += session_duration * profile.hourly_rate
        profile.save()
    return redirect('profile_view')



@user_passes_test(is_admin)
def view_work_sessions(request, user_id):
    user = get_object_or_404(User, id=user_id)
    work_sessions = WorkSession.objects.filter(user=user)
    return render(request, 'hr_system/view_work_sessions.html', {'user': user, 'work_sessions': work_sessions, 'current_page': 'work_sessions'})


@user_passes_test(is_admin)
def edit_work_session(request, session_id):
    session = get_object_or_404(WorkSession, id=session_id)
    if request.method == 'POST':
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')

        start_time = parse_datetime(start_time_str)
        end_time = parse_datetime(end_time_str)
        
        old_duration = session.duration()
        
        session.start_time = start_time
        session.end_time = end_time
        session.save()
        
        profile = get_object_or_404(EmployeeProfile, user=session.user)
        
        new_duration = session.duration()
        profile.total_hours_worked += new_duration - old_duration
        profile.total_earnings += (new_duration - old_duration) * profile.hourly_rate
        profile.save()
        
        return redirect('view_work_sessions', user_id=session.user.id)
    return render(request, 'hr_system/edit_work_session.html', {'session': session})

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            if user.is_superuser:
                return redirect('admin_employee_list')
            else:
                return redirect('profile_view')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


@user_passes_test(is_admin)
def add_employee(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        profile_form = EmployeeProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password1'])
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('admin_employee_list')  # Перенаправление на список сотрудников
        else:
            print(user_form.errors)
            print(profile_form.errors)
    else:
        user_form = UserCreationForm()
        profile_form = EmployeeProfileForm()
    return render(request, 'hr_system/add_employee.html', {'user_form': user_form, 'profile_form': profile_form})


@user_passes_test(is_admin)
def delete_employee(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('admin_employee_list')

def logout_view(request):
    logout(request)
    return redirect('login')

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.db.models import F, ExpressionWrapper, fields, Sum
from .models import EmployeeProfile, WorkSession, User


@user_passes_test(is_admin)
def admin_report(request):
    employees = EmployeeProfile.objects.all()
    report_data = []

    for employee in employees:
        total_hours = WorkSession.objects.filter(user=employee.user).aggregate(
            total_duration=Sum(
                ExpressionWrapper(F('end_time') - F('start_time'), output_field=fields.DurationField())
            )
        )['total_duration']
        
        total_hours_in_hours = total_hours.total_seconds() / 3600 if total_hours else 0
        total_earnings = total_hours_in_hours * employee.hourly_rate
        report_data.append({
            'employee': employee,
            'total_hours': total_hours_in_hours,
            'total_earnings': total_earnings,
        })

    return render(request, 'hr_system/admin_report.html', {'report_data': report_data})
from .models import WorkSession
from django.db.models import Q

def admin_employee_detail(request):
    query = request.GET.get('q')
    if query:
        work_sessions = WorkSession.objects.select_related('user', 'user__employeeprofile').filter(
            Q(user_username_icontains=query) |
            Q(user_employeeprofileposition_icontains=query)
        )
    else:
        work_sessions = WorkSession.objects.select_related('user', 'user__employeeprofile').all()

    context = {
        'work_sessions': work_sessions,
        'query': query,
    }
    return render(request, 'hr_system/admin_employee_detail.html',context)