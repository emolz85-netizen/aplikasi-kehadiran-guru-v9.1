from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health, name="health"),
    path("manifest.json", views.manifest, name="manifest"),
    path("service-worker.js", views.service_worker, name="service_worker"),
    path("login/", auth_views.LoginView.as_view(template_name="attendance/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("profil/", views.profile_page, name="profile_page"),
    path("dashboard-admin/", views.admin_dashboard, name="admin_dashboard"),
    path("peta-kehadiran/", views.attendance_map, name="attendance_map"),
    path("rekod/<str:action>/", views.record_attendance, name="record_attendance"),
    path("cuti/", views.leave_page, name="leave_page"),
    path("tugas-rasmi/", views.duty_page, name="duty_page"),
    path("laporan/", views.report_page, name="report_page"),
    path("laporan/excel/", views.export_excel, name="export_excel"),
    path("laporan/pdf/", views.export_pdf, name="export_pdf"),
    path("import-guru/", views.import_teachers, name="import_teachers"),
]
