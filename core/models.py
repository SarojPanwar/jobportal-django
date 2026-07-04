from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model.
    Adds `role` (seeker / employer / admin) and `company`
    (used only for employer accounts) on top of Django's
    built-in auth fields (username, email, password, etc).
    """

    class Role(models.TextChoices):
        SEEKER = "seeker", "Job Seeker"
        EMPLOYER = "employer", "Employer"
        ADMIN = "admin", "Admin"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.SEEKER)
    company = models.CharField(max_length=150, blank=True, null=True)

    # Login is done by email in this project (see core.backends.EmailBackend)
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username


class Job(models.Model):
    class JobType(models.TextChoices):
        FULL_TIME = "Full-time", "Full-time"
        PART_TIME = "Part-time", "Part-time"
        REMOTE = "Remote", "Remote"
        CONTRACT = "Contract", "Contract"
        INTERNSHIP = "Internship", "Internship"

    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=150)
    location = models.CharField(max_length=150)
    category = models.CharField(max_length=100)
    salary = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    job_type = models.CharField(max_length=20, choices=JobType.choices, default=JobType.FULL_TIME)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} @ {self.company}"

    @property
    def job_type_slug(self):
        return self.job_type.replace(" ", "-").lower()


class Application(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        REVIEWED = "Reviewed", "Reviewed"
        ACCEPTED = "Accepted", "Accepted"
        REJECTED = "Rejected", "Rejected"

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-applied_at"]
        constraints = [
            models.UniqueConstraint(fields=["job", "seeker"], name="unique_job_seeker_application")
        ]

    def __str__(self):
        return f"{self.seeker} -> {self.job}"
