# hr_system/admin.py
from django.contrib import admin
from .models import EmployeeProfile, Notification, Attendance

admin.site.register(EmployeeProfile)
admin.site.register(Notification)
admin.site.register(Attendance)
