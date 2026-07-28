import base64
import io
import math
import calendar
from datetime import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import connection
from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import LeaveRequestForm, OfficialDutyForm, TeacherImportForm, ProfileForm, MalayPasswordChangeForm
from .models import Attendance, LeaveRequest, OfficialDuty, TeacherProfile, SchoolSettings, SchoolHoliday, AccountActivity

def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return JsonResponse({"status": "ok", "database": "connected", "version": "9.1.003"})
    except Exception:
        return JsonResponse({"status": "error", "database": "unavailable", "version": "9.1.003"}, status=503)

def manifest(request):
    return JsonResponse({
        "name": f"Sistem Kehadiran Guru {settings.SCHOOL_NAME}",
        "short_name": "Kehadiran",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#e5e7eb",
        "theme_color": "#4b5563",
    })

def service_worker(request):
    script = '''
const CACHE = "kehadiran-v9-1-003";
self.addEventListener("install", e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(["/","/login/"]))));
self.addEventListener("fetch", e => e.respondWith(fetch(e.request).catch(() => caches.match(e.request))));
'''
    return HttpResponse(script, content_type="application/javascript")



def get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def describe_device(user_agent):
    ua = (user_agent or "").lower()
    if "iphone" in ua:
        platform = "iPhone"
    elif "ipad" in ua:
        platform = "iPad"
    elif "android" in ua:
        platform = "Android"
    elif "windows" in ua:
        platform = "Windows"
    elif "macintosh" in ua or "mac os" in ua:
        platform = "macOS"
    elif "linux" in ua:
        platform = "Linux"
    else:
        platform = "Peranti tidak dikenal pasti"

    if "edg/" in ua:
        browser = "Edge"
    elif "chrome/" in ua and "edg/" not in ua:
        browser = "Chrome"
    elif "firefox/" in ua:
        browser = "Firefox"
    elif "safari/" in ua and "chrome/" not in ua:
        browser = "Safari"
    else:
        browser = "Pelayar tidak dikenal pasti"
    return f"{platform} · {browser}"

def haversine_m(lat1, lon1, lat2, lon2):
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2-lat1)
    dl = math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return r * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

@login_required
def dashboard(request):
    today = timezone.localdate()
    today_holiday = SchoolHoliday.objects.filter(date=today, is_active=True).first()
    record = Attendance.objects.filter(user=request.user, date=today).first()
    month_records = Attendance.objects.filter(
        user=request.user,
        date__year=today.year,
        date__month=today.month,
    )
    leave_days = set()
    for item in LeaveRequest.objects.filter(
        user=request.user, status="DILULUSKAN",
        start_date__lte=today.replace(day=calendar.monthrange(today.year, today.month)[1]),
        end_date__gte=today.replace(day=1),
    ):
        day = max(item.start_date, today.replace(day=1))
        last = min(item.end_date, today.replace(day=calendar.monthrange(today.year, today.month)[1]))
        while day <= last:
            leave_days.add(day)
            day += timezone.timedelta(days=1)

    duty_days = set()
    for item in OfficialDuty.objects.filter(
        user=request.user, status="DILULUSKAN",
        start_date__lte=today.replace(day=calendar.monthrange(today.year, today.month)[1]),
        end_date__gte=today.replace(day=1),
    ):
        day = max(item.start_date, today.replace(day=1))
        last = min(item.end_date, today.replace(day=calendar.monthrange(today.year, today.month)[1]))
        while day <= last:
            duty_days.add(day)
            day += timezone.timedelta(days=1)

    holiday_days = {item.date: item.name for item in SchoolHoliday.objects.filter(
        is_active=True, date__year=today.year, date__month=today.month
    )}

    records_by_day = {r.date.day: r for r in month_records}
    month_calendar = []
    for week in calendar.Calendar(firstweekday=0).monthdatescalendar(today.year, today.month):
        row = []
        for day in week:
            state = "outside"
            label = ""
            if day.month == today.month:
                state = "empty"
                if day in holiday_days:
                    state, label = "holiday", holiday_days[day]
                elif day in leave_days:
                    state, label = "leave", "Cuti"
                elif day in duty_days:
                    state, label = "duty", "Tugas rasmi"
                elif day.day in records_by_day:
                    rec = records_by_day[day.day]
                    state = "late" if rec.status == "LEWAT" else "present"
                    label = rec.get_status_display()
                elif day.weekday() >= 5:
                    state, label = "weekend", "Hujung minggu"
                elif day < today:
                    state, label = "absent", "Tiada rekod"
            row.append({"date": day, "day": day.day, "state": state, "label": label})
        month_calendar.append(row)

    school = SchoolSettings.load()
    target_in, target_out = school.times_for_date(today)
    week_start = today - timezone.timedelta(days=today.weekday())
    week_records = Attendance.objects.filter(
        user=request.user,
        date__gte=week_start,
        date__lte=today,
        check_in__isnull=False,
    )
    today_status = "Belum daftar masuk"
    today_status_class = "pending"
    if record and record.check_out:
        today_status = "Selesai daftar keluar"
        today_status_class = "complete"
    elif record and record.check_in:
        today_status = "Sudah daftar masuk"
        today_status_class = "active"

    return render(request, "attendance/dashboard.html", {
        "record": record,
        "today": today,
        "month_count": month_records.count(),
        "late_count": month_records.filter(status="LEWAT").count(),
        "school": school,
        "target_in": target_in,
        "target_out": target_out,
        "month_calendar": month_calendar,
        "month_name": today.strftime("%B %Y"),
        "today_holiday": today_holiday,
        "week_count": week_records.count(),
        "today_status": today_status,
        "today_status_class": today_status_class,
    })

@login_required
@require_POST
def record_attendance(request, action):
    if action not in {"masuk", "keluar"}:
        return JsonResponse({"ok": False, "message": "Tindakan tidak sah."}, status=400)

    try:
        lat = float(request.POST["latitude"])
        lng = float(request.POST["longitude"])
        accuracy = float(request.POST.get("accuracy", 9999))
    except (KeyError, ValueError):
        return JsonResponse({"ok": False, "message": "Lokasi GPS tidak sah."}, status=400)

    school = SchoolSettings.load()
    if accuracy > school.max_gps_accuracy_meters:
        return JsonResponse({
            "ok": False,
            "message": f"Ketepatan GPS masih lemah ({accuracy:.0f} m). Cuba Segarkan GPS sehingga {school.max_gps_accuracy_meters} m atau lebih baik."
        }, status=400)

    distance = haversine_m(lat, lng, school.latitude, school.longitude)
    if distance > school.radius_meters:
        return JsonResponse({
            "ok": False,
            "message": f"Anda berada {distance:.1f} m dari sekolah. Had ialah {school.radius_meters} m."
        }, status=403)

    today = timezone.localdate()
    holiday = SchoolHoliday.objects.filter(date=today, is_active=True).first()
    if holiday:
        return JsonResponse({
            "ok": False,
            "message": f"Hari ini ialah {holiday.name}. Kehadiran tidak diperlukan."
        }, status=403)
    if today.weekday() >= 5:
        return JsonResponse({
            "ok": False,
            "message": "Hari ini ialah hujung minggu. Kehadiran tidak diperlukan."
        }, status=403)
    now = timezone.now()
    rec, _ = Attendance.objects.get_or_create(user=request.user, date=today)
    selfie = request.FILES.get("selfie")
    user_agent = request.META.get("HTTP_USER_AGENT", "")[:2000]
    device = describe_device(user_agent)
    client_ip = get_client_ip(request)

    if action == "masuk":
        if rec.check_in:
            return JsonResponse({"ok": False, "message": "Rekod masuk sudah dibuat."}, status=400)
        rec.check_in = now
        rec.check_in_lat = lat
        rec.check_in_lng = lng
        rec.check_in_accuracy = accuracy
        rec.distance_in_m = distance
        rec.selfie_in = selfie
        rec.check_in_ip = client_ip
        rec.check_in_device = device
        rec.check_in_user_agent = user_agent
        target_in, _ = school.times_for_date(today)
        rec.status = "LEWAT" if timezone.localtime(now).time() > target_in else "HADIR"
    else:
        if not rec.check_in:
            return JsonResponse({"ok": False, "message": "Sila rekod masuk dahulu."}, status=400)
        if rec.check_out:
            return JsonResponse({"ok": False, "message": "Rekod keluar sudah dibuat."}, status=400)
        rec.check_out = now
        rec.check_out_lat = lat
        rec.check_out_lng = lng
        rec.check_out_accuracy = accuracy
        rec.distance_out_m = distance
        rec.selfie_out = selfie
        rec.check_out_ip = client_ip
        rec.check_out_device = device
        rec.check_out_user_agent = user_agent

    rec.save()
    return JsonResponse({"ok": True, "message": f"Berjaya. Jarak {distance:.1f} m, ketepatan GPS {accuracy:.0f} m."})

@login_required
def profile_page(request):
    profile_form = ProfileForm(instance=request.user, prefix="profile")
    password_form = MalayPasswordChangeForm(request.user, prefix="password")

    if request.method == "POST":
        if "save_profile" in request.POST:
            old_username = request.user.username
            profile_form = ProfileForm(request.POST, instance=request.user, prefix="profile")
            if profile_form.is_valid():
                user = profile_form.save()
                AccountActivity.objects.create(
                    user=user,
                    action="Kemas kini profil",
                    details=f"Nama pengguna: {old_username} → {user.username}",
                )
                messages.success(request, "Profil berjaya dikemas kini.")
                return redirect("profile_page")
        elif "change_password" in request.POST:
            password_form = MalayPasswordChangeForm(request.user, request.POST, prefix="password")
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                AccountActivity.objects.create(user=user, action="Tukar kata laluan")
                messages.success(request, "Kata laluan berjaya ditukar.")
                return redirect("profile_page")

    activities = AccountActivity.objects.filter(user=request.user)[:10]
    return render(request, "attendance/profile.html", {
        "profile_form": profile_form,
        "password_form": password_form,
        "activities": activities,
    })


@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    today = timezone.localdate()
    User = get_user_model()
    teachers = User.objects.filter(is_active=True, is_staff=False)
    records = Attendance.objects.filter(date=today).select_related("user")
    attended_ids = records.filter(check_in__isnull=False).values_list("user_id", flat=True)
    total = teachers.count()
    attended = records.filter(check_in__isnull=False).count()
    late = records.filter(status="LEWAT").count()
    absent = teachers.exclude(id__in=attended_ids)
    percentage = round((attended / total * 100), 1) if total else 0
    return render(request, "attendance/admin_dashboard.html", {
        "today": today, "total": total, "attended": attended, "late": late,
        "absent": absent, "percentage": percentage, "records": records,
    })


@login_required
def leave_page(request):
    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, "Permohonan cuti dihantar.")
            return redirect("leave_page")
    else:
        form = LeaveRequestForm()
    return render(request, "attendance/leave.html", {
        "form": form,
        "items": LeaveRequest.objects.filter(user=request.user),
    })

@login_required
def duty_page(request):
    if request.method == "POST":
        form = OfficialDutyForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, "Permohonan tugas rasmi dihantar.")
            return redirect("duty_page")
    else:
        form = OfficialDutyForm()
    return render(request, "attendance/duty.html", {
        "form": form,
        "items": OfficialDuty.objects.filter(user=request.user),
    })

@login_required
def report_page(request):
    return render(request, "attendance/report.html", {
        "records": Attendance.objects.filter(user=request.user)[:100],
    })

@login_required
def export_excel(request):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Kehadiran"
    ws.append(["Tarikh", "Masuk", "Keluar", "Status", "Jarak Masuk", "Jarak Keluar"])
    for r in Attendance.objects.filter(user=request.user).order_by("-date"):
        ws.append([
            str(r.date),
            timezone.localtime(r.check_in).strftime("%H:%M:%S") if r.check_in else "",
            timezone.localtime(r.check_out).strftime("%H:%M:%S") if r.check_out else "",
            r.get_status_display(),
            round(r.distance_in_m or 0, 1),
            round(r.distance_out_m or 0, 1),
        ])
    output = io.BytesIO()
    wb.save(output)
    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="laporan_kehadiran.xlsx"'
    return response

@login_required
def export_pdf(request):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    output = io.BytesIO()
    c = canvas.Canvas(output, pagesize=A4)
    _, height = A4
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height - 45, f"Laporan Kehadiran - {settings.SCHOOL_NAME}")
    c.setFont("Helvetica", 9)
    y = height - 75
    for r in Attendance.objects.filter(user=request.user).order_by("-date")[:150]:
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 9)
            y = height - 50
        masuk = timezone.localtime(r.check_in).strftime("%H:%M") if r.check_in else "-"
        keluar = timezone.localtime(r.check_out).strftime("%H:%M") if r.check_out else "-"
        c.drawString(40, y, f"{r.date}   Masuk: {masuk}   Keluar: {keluar}   {r.get_status_display()}")
        y -= 16
    c.save()
    output.seek(0)
    return FileResponse(output, as_attachment=True, filename="laporan_kehadiran.pdf")

@user_passes_test(lambda u: u.is_staff)
def import_teachers(request):
    result = None
    if request.method == "POST":
        form = TeacherImportForm(request.POST, request.FILES)
        if form.is_valid():
            from openpyxl import load_workbook
            wb = load_workbook(form.cleaned_data["file"], data_only=True)
            ws = wb.active
            headers = {str(c.value).strip().lower(): i for i, c in enumerate(ws[1]) if c.value}
            required = ["nama pengguna", "nama penuh", "emel", "no. staf", "jawatan"]
            missing = [h for h in required if h not in headers]
            if missing:
                messages.error(request, "Lajur tiada: " + ", ".join(missing))
            else:
                User = get_user_model()
                created = updated = 0
                for row in ws.iter_rows(min_row=2, values_only=True):
                    username = str(row[headers["nama pengguna"]] or "").strip()
                    full_name = str(row[headers["nama penuh"]] or "").strip()
                    if not username or not full_name:
                        continue
                    user, is_new = User.objects.get_or_create(username=username)
                    parts = full_name.split(maxsplit=1)
                    user.first_name = parts[0]
                    user.last_name = parts[1] if len(parts) > 1 else ""
                    user.email = str(row[headers["emel"]] or "").strip()
                    if is_new:
                        user.set_password(form.cleaned_data["default_password"])
                        created += 1
                    else:
                        updated += 1
                    user.save()
                    profile, _ = TeacherProfile.objects.get_or_create(user=user)
                    profile.staff_id = str(row[headers["no. staf"]] or "").strip()
                    profile.position = str(row[headers["jawatan"]] or "").strip()
                    profile.save()
                result = {"created": created, "updated": updated}
                messages.success(request, "Import guru selesai.")
    else:
        form = TeacherImportForm()
    return render(request, "attendance/import_teachers.html", {"form": form, "result": result})
