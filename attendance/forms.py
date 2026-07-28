from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from .models import LeaveRequest, OfficialDuty, SchoolHoliday


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]
        labels = {"username": "Nama pengguna", "email": "E-mel"}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get("instance")
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = "Mesti unik. Huruf, nombor dan simbol @/./+/-/_ dibenarkan."

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        query = User.objects.filter(username__iexact=username)
        if self.user:
            query = query.exclude(pk=self.user.pk)
        if query.exists():
            raise forms.ValidationError("Nama pengguna ini sudah digunakan.")
        return username


class MalayPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Kata laluan lama", widget=forms.PasswordInput)
    new_password1 = forms.CharField(label="Kata laluan baharu", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Sahkan kata laluan baharu", widget=forms.PasswordInput)

    def clean_new_password1(self):
        value = self.cleaned_data.get("new_password1")
        if value:
            password_validation.validate_password(value, self.user)
        return value


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["leave_type", "start_date", "end_date", "reason", "attachment"]
        labels = {
            "leave_type": "Jenis cuti",
            "start_date": "Tarikh mula",
            "end_date": "Tarikh akhir",
            "reason": "Sebab / catatan",
            "attachment": "Dokumen sokongan (pilihan)",
        }
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "reason": forms.Textarea(attrs={"rows": 4, "placeholder": "Nyatakan sebab permohonan cuti"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["attachment"].help_text = "PDF atau gambar surat/dokumen sokongan."

    def clean(self):
        data = super().clean()
        start, end = data.get("start_date"), data.get("end_date")
        if start and end and end < start:
            self.add_error("end_date", "Tarikh akhir tidak boleh lebih awal daripada tarikh mula.")
        if self.user and start and end:
            overlap = LeaveRequest.objects.filter(
                user=self.user,
                status__in=["MENUNGGU", "DILULUSKAN"],
                start_date__lte=end,
                end_date__gte=start,
            )
            if self.instance.pk:
                overlap = overlap.exclude(pk=self.instance.pk)
            if overlap.exists():
                raise forms.ValidationError("Anda sudah mempunyai permohonan cuti bagi tarikh yang bertindih.")
        return data


class LeaveReviewForm(forms.Form):
    admin_note = forms.CharField(
        label="Ulasan pentadbir",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Catatan kelulusan atau sebab penolakan"}),
    )


class OfficialDutyForm(forms.ModelForm):
    class Meta:
        model = OfficialDuty
        fields = ["title", "location", "start_date", "end_date", "description"]
        widgets = {"start_date": forms.DateInput(attrs={"type": "date"}), "end_date": forms.DateInput(attrs={"type": "date"}), "description": forms.Textarea(attrs={"rows": 4})}


class TeacherImportForm(forms.Form):
    file = forms.FileField(label="Fail Excel (.xlsx)")
    default_password = forms.CharField(label="Kata laluan awal", min_length=8, widget=forms.PasswordInput)


class PasswordRecoveryRequestForm(forms.Form):
    username = forms.CharField(label="Nama pengguna", max_length=150)


class QRPasswordSetForm(forms.Form):
    new_password1 = forms.CharField(label="Kata laluan baharu", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Sahkan kata laluan baharu", widget=forms.PasswordInput)

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        data = super().clean()
        p1, p2 = data.get("new_password1"), data.get("new_password2")
        if p1 and p2 and p1 != p2:
            self.add_error("new_password2", "Kata laluan tidak sepadan.")
        if p1:
            password_validation.validate_password(p1, self.user)
        return data


class PasswordRecoveryConfirmForm(forms.Form):
    username = forms.CharField(label="Nama pengguna", max_length=150)
    code = forms.CharField(label="Kod pemulihan 6 digit", min_length=6, max_length=6)
    new_password1 = forms.CharField(label="Kata laluan baharu", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Sahkan kata laluan baharu", widget=forms.PasswordInput)

    def clean(self):
        data = super().clean()
        p1, p2 = data.get("new_password1"), data.get("new_password2")
        if p1 and p2 and p1 != p2:
            self.add_error("new_password2", "Kata laluan tidak sepadan.")
        if p1:
            password_validation.validate_password(p1)
        return data
