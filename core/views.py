from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import role_required
from .forms import ApplicationForm, JobForm, LoginForm, RegisterForm
from .models import Application, Job, User

VALID_STATUSES = ("Pending", "Reviewed", "Accepted", "Rejected")

CATEGORY_ICONS = {
    "Technology": "laptop", "Marketing": "megaphone", "Design": "palette",
    "Finance": "cash-coin", "Healthcare": "heart-pulse", "Education": "book",
    "Sales": "graph-up-arrow", "Engineering": "gear", "HR": "person-badge",
    "Management": "diagram-3",
}


# ─── PUBLIC ROUTES ────────────────────────────────────────────────────────

def index(request):
    recent_jobs = Job.objects.filter(is_active=True)[:6]
    stats = {
        "jobs": Job.objects.filter(is_active=True).count(),
        "employers": User.objects.filter(role="employer").count(),
        "seekers": User.objects.filter(role="seeker").count(),
        "apps": Application.objects.count(),
    }
    categories = (
        Job.objects.filter(is_active=True)
        .values("category")
        .annotate(cnt=Count("id"))
        .order_by("-cnt")[:8]
    )
    categories = list(categories)
    for c in categories:
        c["icon"] = CATEGORY_ICONS.get(c["category"], "briefcase")

    return render(request, "core/index.html", {
        "recent_jobs": recent_jobs, "stats": stats, "categories": categories,
    })


def job_list(request):
    keyword = request.GET.get("keyword", "").strip()
    location = request.GET.get("location", "").strip()
    category = request.GET.get("category", "").strip()
    job_type = request.GET.get("job_type", "").strip()

    jobs = Job.objects.filter(is_active=True)
    if keyword:
        jobs = jobs.filter(
            Q(title__icontains=keyword) | Q(description__icontains=keyword) | Q(company__icontains=keyword)
        )
    if location:
        jobs = jobs.filter(location__icontains=location)
    if category:
        jobs = jobs.filter(category=category)
    if job_type:
        jobs = jobs.filter(job_type=job_type)

    categories = Job.objects.filter(is_active=True).values_list("category", flat=True).distinct()

    return render(request, "core/jobs.html", {
        "jobs": jobs, "categories": categories,
        "keyword": keyword, "location": location, "category": category, "job_type": job_type,
    })


def job_detail(request, job_id):
    job = Job.objects.filter(id=job_id, is_active=True).first()
    if not job:
        messages.error(request, "Job not found.")
        return redirect("core:job_list")

    already_applied = False
    if request.user.is_authenticated and request.user.role == "seeker":
        already_applied = Application.objects.filter(job=job, seeker=request.user).exists()

    return render(request, "core/job_detail.html", {"job": job, "already_applied": already_applied})


# ─── AUTH ROUTES ──────────────────────────────────────────────────────────

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            User.objects.create(
                username=data["username"],
                email=data["email"],
                password=make_password(data["password"]),
                role=data["role"],
                company=data.get("company", ""),
            )
            messages.success(request, "Registration successful! Please login.")
            return redirect("core:login")
        for err_list in form.errors.values():
            for err in err_list:
                messages.error(request, err)
        return redirect("core:register")

    return render(request, "core/register.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].strip()
            password = form.cleaned_data["password"]
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect("core:dashboard")
        messages.error(request, "Invalid email or password.")

    return render(request, "core/login.html")


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("core:index")


# ─── DASHBOARD ────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    user = request.user

    if user.role == "seeker":
        applications = (
            Application.objects.filter(seeker=user)
            .select_related("job")
            .order_by("-applied_at")
        )
        counts = {
            "pending": applications.filter(status="Pending").count(),
            "accepted": applications.filter(status="Accepted").count(),
            "reviewed": applications.filter(status="Reviewed").count(),
        }
        return render(request, "core/dashboard_seeker.html", {
            "applications": applications, "counts": counts,
        })

    elif user.role == "employer":
        jobs = Job.objects.filter(employer=user).order_by("-created_at")
        total_apps = Application.objects.filter(job__employer=user).count()
        active_count = jobs.filter(is_active=True).count()
        return render(request, "core/dashboard_employer.html", {
            "jobs": jobs, "total_apps": total_apps, "active_count": active_count,
        })

    elif user.role == "admin":
        users = User.objects.all().order_by("-date_joined")
        jobs = Job.objects.select_related("employer").order_by("-created_at")
        apps = Application.objects.select_related("job", "seeker").order_by("-applied_at")
        stats = {
            "users": users.count(),
            "jobs": jobs.count(),
            "apps": apps.count(),
            "employers": users.filter(role="employer").count(),
            "seekers": users.filter(role="seeker").count(),
        }
        return render(request, "core/dashboard_admin.html", {
            "users": users, "jobs": jobs, "apps": apps, "stats": stats,
            "statuses": VALID_STATUSES,
        })

    return redirect("core:index")


# ─── SEEKER ROUTES ────────────────────────────────────────────────────────

@login_required
@role_required("seeker")
def apply_job(request, job_id):
    job = Job.objects.filter(id=job_id, is_active=True).first()
    if not job:
        messages.error(request, "Job not found or no longer active.")
        return redirect("core:job_list")

    if Application.objects.filter(job=job, seeker=request.user).exists():
        messages.info(request, "You have already applied for this job.")
        return redirect("core:job_detail", job_id=job_id)

    if request.method == "POST":
        form = ApplicationForm(request.POST)
        if form.is_valid():
            Application.objects.create(
                job=job, seeker=request.user,
                cover_letter=form.cleaned_data.get("cover_letter", "").strip(),
            )
            messages.success(request, "Application submitted successfully!")
            return redirect("core:dashboard")

    return render(request, "core/apply.html", {"job": job})


# ─── EMPLOYER ROUTES ──────────────────────────────────────────────────────

@login_required
@role_required("employer")
def post_job(request):
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect("core:dashboard")
        for err_list in form.errors.values():
            for err in err_list:
                messages.error(request, err)

    return render(request, "core/post_job.html")


@login_required
@role_required("employer")
def edit_job(request, job_id):
    job = Job.objects.filter(id=job_id, employer=request.user).first()
    if not job:
        messages.error(request, "Job not found.")
        return redirect("core:dashboard")

    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect("core:dashboard")

    job_types = [c[0] for c in Job.JobType.choices]
    categories = [
        "Technology", "Marketing", "Design", "Finance", "Healthcare",
        "Education", "Sales", "Engineering", "HR", "Management", "Other",
    ]
    return render(request, "core/edit_job.html", {
        "job": job, "job_types": job_types, "categories": categories,
    })


@login_required
@role_required("employer", "admin")
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    job.is_active = False
    job.save(update_fields=["is_active"])
    messages.info(request, "Job removed.")
    return redirect("core:dashboard")


@login_required
@role_required("employer")
def job_applications(request, job_id):
    job = Job.objects.filter(id=job_id, employer=request.user).first()
    if not job:
        messages.error(request, "Unauthorized.")
        return redirect("core:dashboard")

    apps = Application.objects.filter(job=job).select_related("seeker").order_by("-applied_at")
    return render(request, "core/job_applications.html", {"job": job, "applications": apps})


@login_required
@role_required("employer", "admin")
def update_status(request, app_id, status):
    if status not in VALID_STATUSES:
        messages.error(request, "Invalid status.")
        return redirect("core:dashboard")
    application = get_object_or_404(Application, id=app_id)
    application.status = status
    application.save(update_fields=["status"])
    messages.success(request, f"Application marked as {status}.")
    referrer = request.META.get("HTTP_REFERER")
    return redirect(referrer or "core:dashboard")


# ─── ADMIN ROUTES ─────────────────────────────────────────────────────────

@login_required
@role_required("admin")
def admin_delete_user(request, user_id):
    if user_id == request.user.id:
        messages.error(request, "Cannot delete yourself.")
        return redirect("core:dashboard")
    User.objects.filter(id=user_id).delete()
    messages.info(request, "User deleted.")
    return redirect("core:dashboard")


@login_required
@role_required("admin")
def admin_toggle_job(request, job_id):
    job = Job.objects.filter(id=job_id).first()
    if job:
        job.is_active = not job.is_active
        job.save(update_fields=["is_active"])
        messages.info(request, "Job status toggled.")
    return redirect("core:dashboard")
