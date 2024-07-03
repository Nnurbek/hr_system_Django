 
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    total_hours_worked = models.FloatField(default=0)
    total_earnings = models.FloatField(default=0)
    hourly_rate = models.FloatField(default=0)

    def __str__(self):
        return self.user.username

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for {self.recipient.username} - {self.message[:20]}'

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])

    def __str__(self):
        return f"Attendance for {self.user.username} on {self.date}"

class WorkSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    def duration(self):
        if self.end_time:
            return round((self.end_time - self.start_time).total_seconds() / 3600, 2)
        return 0

    def __str__(self):
        return f"Work session for {self.user.username} from {self.start_time} to {self.end_time}"
