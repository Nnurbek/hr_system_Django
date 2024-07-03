from django.urls import path
from . import views

urlpatterns = [
    path('employees/', views.employee_list, name='employee_list'),
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('admin/employees/', views.admin_employee_list, name='admin_employee_list'),
    path('admin/profile/edit/<int:user_id>/', views.admin_profile_edit, name='admin_profile_edit'),
    path('admin/attendance/mark/<int:user_id>/<str:status>/', views.mark_attendance, name='mark_attendance'),
    path('admin/reports/generate/', views.generate_report, name='generate_report'),
    path('start_work/', views.start_work, name='start_work'),
    path('end_work/', views.end_work, name='end_work'),
    path('admin/work_sessions/<int:user_id>/', views.view_work_sessions, name='view_work_sessions'),
    path('admin/work_session/edit/<int:session_id>/', views.edit_work_session, name='edit_work_session'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin/employee/add/', views.add_employee, name='add_employee'),
    path('admin/employee/delete/<int:user_id>/', views.delete_employee, name='delete_employee'),
    path('notifications/', views.notifications_view, name='notifications_view'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('notifications/create/', views.create_notification, name='create_notification'),
    path('admin/report/', views.admin_report, name='admin_report'),
    path('admin/employee-detail/', views.admin_employee_detail, name='admin_employee_detail'),
]
