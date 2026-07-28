import base64
import io
import math
import calendar
from datetime import time, datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import connection
from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.urls import reverse

from .forms import LeaveRequestForm, OfficialDutyForm, TeacherImportForm, ProfileForm, MalayPasswordChangeForm, PasswordRecoveryRequestForm, PasswordRecoveryConfirmForm, QRPasswordSetForm
from .models import Attendance, LeaveRequest, OfficialDuty, TeacherProfile, SchoolSettings, SchoolHoliday, AccountActivity, PasswordRecoveryRequest

def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return JsonResponse({"status": "ok", "database": "connected", "version": "9.1.006QR"})
    except Exception:
        return JsonResponse({"status": "error", "database": "unavailable", "version": "9.1.006QR"}, status=503)

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
const CACHE = "kehadiran-v9-1-006qr";
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
    teachers = User.objects.filter(is_active=True, is_staff=False).order_by("first_name", "username")
    records = Attendance.objects.filter(date=today).select_related("user").order_by("check_in")

    attended_ids = set(records.filter(check_in__isnull=False).values_list("user_id", flat=True))
    leave_ids = set(LeaveRequest.objects.filter(
        status="DILULUSKAN", start_date__lte=today, end_date__gte=today
    ).values_list("user_id", flat=True))
    duty_ids = set(OfficialDuty.objects.filter(
        status="DILULUSKAN", start_date__lte=today, end_date__gte=today
    ).values_list("user_id", flat=True))

    total = teachers.count()
    attended = len(attended_ids)
    late = records.filter(check_in__isnull=False, status="LEWAT").count()
    on_leave = teachers.filter(id__in=leave_ids).count()
    on_duty = teachers.filter(id__in=duty_ids).count()
    excused_ids = leave_ids | duty_ids
    absent = teachers.exclude(id__in=attended_ids | excused_ids)
    percentage = round((attended / total * 100), 1) if total else 0

    # Statistik tujuh hari terakhir untuk graf ringkas tanpa pustaka luaran.
    weekly_stats = []
    max_week_count = 1
    for offset in range(6, -1, -1):
        day = today - timezone.timedelta(days=offset)
        count = Attendance.objects.filter(date=day, check_in__isnull=False).count()
        max_week_count = max(max_week_count, count)
        weekly_stats.append({"date": day, "count": count})
    for item in weekly_stats:
        item["height"] = round((item["count"] / max_week_count) * 100)

    school = SchoolSettings.load()
    today_holiday = SchoolHoliday.objects.filter(date=today, is_active=True).first()
    target_in, target_out = school.times_for_date(today)

    return render(request, "attendance/admin_dashboard.html", {
        "today": today,
        "school": school,
        "target_in": target_in,
        "target_out": target_out,
        "today_holiday": today_holiday,
        "total": total,
        "attended": attended,
        "late": late,
        "on_leave": on_leave,
        "on_duty": on_duty,
        "absent": absent,
        "percentage": percentage,
        "records": records,
        "weekly_stats": weekly_stats,
        "pending_leave": LeaveRequest.objects.filter(status="MENUNGGU").count(),
        "pending_duty": OfficialDuty.objects.filter(status="MENUNGGU").count(),
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
def attendance_map(request):
    today = timezone.localdate()
    selected_date = today
    raw_date = request.GET.get("date", "").strip()
    if raw_date:
        try:
            selected_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        except ValueError:
            messages.warning(request, "Format tarikh tidak sah. Tarikh hari ini digunakan.")

    teacher_id = request.GET.get("teacher", "").strip()
    status = request.GET.get("status", "").strip().upper()
    records = Attendance.objects.filter(
        date=selected_date, check_in__isnull=False
    ).select_related("user").order_by("check_in")

    if teacher_id.isdigit():
        records = records.filter(user_id=int(teacher_id))
    if status in {"HADIR", "LEWAT"}:
        records = records.filter(status=status)

    markers = []
    for rec in records:
        name = rec.user.get_full_name() or rec.user.username
        if rec.check_in_lat is not None and rec.check_in_lng is not None:
            markers.append({
                "type": "Masuk",
                "name": name,
                "lat": rec.check_in_lat,
                "lng": rec.check_in_lng,
                "time": timezone.localtime(rec.check_in).strftime("%H:%M:%S") if rec.check_in else "—",
                "status": rec.get_status_display(),
                "accuracy": round(rec.check_in_accuracy, 1) if rec.check_in_accuracy is not None else None,
                "distance": round(rec.distance_in_m, 1) if rec.distance_in_m is not None else None,
                "device": rec.check_in_device or "Peranti tidak direkod",
                "google_url": f"https://www.google.com/maps?q={rec.check_in_lat},{rec.check_in_lng}",
            })
        if rec.check_out_lat is not None and rec.check_out_lng is not None:
            markers.append({
                "type": "Keluar",
                "name": name,
                "lat": rec.check_out_lat,
                "lng": rec.check_out_lng,
                "time": timezone.localtime(rec.check_out).strftime("%H:%M:%S") if rec.check_out else "—",
                "status": rec.get_status_display(),
                "accuracy": round(rec.check_out_accuracy, 1) if rec.check_out_accuracy is not None else None,
                "distance": round(rec.distance_out_m, 1) if rec.distance_out_m is not None else None,
                "device": rec.check_out_device or "Peranti tidak direkod",
                "google_url": f"https://www.google.com/maps?q={rec.check_out_lat},{rec.check_out_lng}",
            })

    User = get_user_model()
    teachers = User.objects.filter(is_active=True, is_staff=False).order_by("first_name", "username")
    school = SchoolSettings.load()
    return render(request, "attendance/attendance_map.html", {
        "school": school,
        "selected_date": selected_date,
        "selected_teacher": teacher_id,
        "selected_status": status,
        "teachers": teachers,
        "records": records,
        "markers": markers,
    })

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


def password_recovery_request(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = PasswordRecoveryRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"].strip()
        User = get_user_model()
        user = User.objects.filter(username__iexact=username, is_active=True).first()
        if user:
            existing = PasswordRecoveryRequest.objects.filter(user=user, status__in=["MENUNGGU", "DILULUSKAN"]).first()
            if not existing:
                PasswordRecoveryRequest.objects.create(user=user)
                AccountActivity.objects.create(user=user, action="Minta reset kata laluan", details="Permintaan dihantar kepada pentadbir")
        messages.success(request, "Permintaan telah dihantar. Hubungi pentadbir sekolah untuk mengimbas QR reset.")
        return redirect("password_recovery_status")
    return render(request, "attendance/password_recovery_request.html", {"form": form})


def password_recovery_status(request):
    return render(request, "attendance/password_recovery_status.html")


def password_recovery_confirm(request):
    """Fallback manual-code recovery for devices that cannot scan QR."""
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = PasswordRecoveryConfirmForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"].strip()
        User = get_user_model()
        user = User.objects.filter(username__iexact=username, is_active=True).first()
        recovery = None
        if user:
            recovery = PasswordRecoveryRequest.objects.filter(user=user, status="DILULUSKAN").order_by("-approved_at").first()
        valid = bool(recovery and recovery.expires_at and recovery.expires_at > timezone.now() and check_password(form.cleaned_data["code"], recovery.code_hash))
        if not valid:
            messages.error(request, "Kod tidak sah, telah tamat tempoh atau belum diluluskan.")
        else:
            user.set_password(form.cleaned_data["new_password1"])
            user.save()
            recovery.status = "SELESAI"
            recovery.used_at = timezone.now()
            recovery.code_display = ""
            recovery.save(update_fields=["status", "used_at", "code_display"])
            AccountActivity.objects.create(user=user, action="Reset kata laluan", details="Kata laluan dipulihkan menggunakan kod pentadbir")
            messages.success(request, "Kata laluan berjaya ditukar. Sila log masuk.")
            return redirect("login")
    return render(request, "attendance/password_recovery_confirm.html", {"form": form})


def password_recovery_qr_scan(request, pk, code):
    """Validate the short-lived QR and authorize a one-time password change."""
    if request.user.is_authenticated:
        return redirect("dashboard")
    recovery = get_object_or_404(PasswordRecoveryRequest.objects.select_related("user"), pk=pk)
    valid = (
        recovery.status == "DILULUSKAN"
        and recovery.expires_at
        and recovery.expires_at > timezone.now()
        and check_password(code, recovery.code_hash)
    )
    if not valid:
        return render(request, "attendance/password_recovery_qr_invalid.html", status=400)
    request.session["password_recovery_qr_id"] = recovery.pk
    request.session.set_expiry(15 * 60)
    return redirect("password_recovery_qr_set")


def password_recovery_qr_set(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    recovery_id = request.session.get("password_recovery_qr_id")
    recovery = PasswordRecoveryRequest.objects.select_related("user").filter(pk=recovery_id).first()
    valid = bool(recovery and recovery.status == "DILULUSKAN" and recovery.expires_at and recovery.expires_at > timezone.now())
    if not valid:
        request.session.pop("password_recovery_qr_id", None)
        return render(request, "attendance/password_recovery_qr_invalid.html", status=400)

    form = QRPasswordSetForm(request.POST or None, user=recovery.user)
    if request.method == "POST" and form.is_valid():
        recovery.user.set_password(form.cleaned_data["new_password1"])
        recovery.user.save()
        recovery.status = "SELESAI"
        recovery.used_at = timezone.now()
        recovery.code_display = ""
        recovery.save(update_fields=["status", "used_at", "code_display"])
        AccountActivity.objects.create(
            user=recovery.user,
            action="Reset kata laluan QR",
            details="Kata laluan dipulihkan melalui QR pentadbir",
        )
        request.session.pop("password_recovery_qr_id", None)
        messages.success(request, "Kata laluan berjaya ditukar. Sila log masuk.")
        return redirect("login")
    return render(request, "attendance/password_recovery_qr_set.html", {"form": form, "recovery": recovery})


@user_passes_test(lambda u: u.is_staff)
def password_recovery_admin(request):
    import qrcode
    items = list(PasswordRecoveryRequest.objects.select_related("user", "approved_by")[:100])
    now = timezone.now()
    for item in items:
        item.qr_data_uri = ""
        item.qr_url = ""
        if item.status == "DILULUSKAN" and item.code_display and item.expires_at and item.expires_at > now:
            item.qr_url = request.build_absolute_uri(
                reverse("password_recovery_qr_scan", args=[item.pk, item.code_display])
            )
            image = qrcode.make(item.qr_url)
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            item.qr_data_uri = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
    return render(request, "attendance/password_recovery_admin.html", {"items": items})


@require_POST
@user_passes_test(lambda u: u.is_staff)
def password_recovery_approve(request, pk):
    import secrets
    item = get_object_or_404(PasswordRecoveryRequest.objects.select_related("user"), pk=pk)
    code = f"{secrets.randbelow(1000000):06d}"
    item.status = "DILULUSKAN"
    item.code_hash = make_password(code)
    item.code_display = code
    item.expires_at = timezone.now() + timedelta(minutes=15)
    item.approved_at = timezone.now()
    item.approved_by = request.user
    item.used_at = None
    item.save()
    AccountActivity.objects.create(user=item.user, action="QR reset diluluskan", details=f"Diluluskan oleh {request.user.username}")
    messages.success(request, f"QR reset untuk {item.user.username} telah dijana dan sah selama 15 minit.")
    return redirect("password_recovery_admin")


@require_POST
@user_passes_test(lambda u: u.is_staff)
def password_recovery_reject(request, pk):
    item = PasswordRecoveryRequest.objects.get(pk=pk)
    item.status="DITOLAK"; item.code_display=""; item.save(update_fields=["status","code_display"])
    messages.success(request, "Permintaan ditolak.")
    return redirect("password_recovery_admin")
