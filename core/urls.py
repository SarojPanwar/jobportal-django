from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("jobs/", views.job_list, name="job_list"),
    path("jobs/<int:job_id>/", views.job_detail, name="job_detail"),

    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("dashboard/", views.dashboard, name="dashboard"),

    path("apply/<int:job_id>/", views.apply_job, name="apply_job"),

    path("post-job/", views.post_job, name="post_job"),
    path("edit-job/<int:job_id>/", views.edit_job, name="edit_job"),
    path("delete-job/<int:job_id>/", views.delete_job, name="delete_job"),
    path("job-applications/<int:job_id>/", views.job_applications, name="job_applications"),
    path("update-status/<int:app_id>/<str:status>/", views.update_status, name="update_status"),

    path("admin-panel/delete-user/<int:user_id>/", views.admin_delete_user, name="admin_delete_user"),
    path("admin-panel/toggle-job/<int:job_id>/", views.admin_toggle_job, name="admin_toggle_job"),
]
