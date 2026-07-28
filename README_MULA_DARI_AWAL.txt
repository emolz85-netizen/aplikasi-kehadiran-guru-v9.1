SISTEM KEHADIRAN GURU V9 FINAL
==============================

STRUKTUR WAJIB DI GITHUB
------------------------
attendance/
config/
static/
templates/
manage.py
render.yaml
requirements.txt
runtime.txt

Jangan gunakan butang "choose your files" untuk memilih kandungan folder
secara satu-satu kerana GitHub boleh meratakan struktur folder.

CARA PALING SELAMAT UPLOAD
--------------------------
1. Cipta repository GitHub kosong.
2. Buka File Explorer dan folder APLIKASI_KEHADIRAN_GURU_V9_FINAL.
3. Pilih SEMUA item termasuk folder attendance, config, static dan templates.
4. SERET (drag and drop) semuanya terus ke kotak upload GitHub.
5. Sebelum Commit, pastikan GitHub memaparkan laluan folder seperti:
   attendance/models.py
   config/settings.py
   templates/attendance/login.html
   static/attendance/style.css
6. Klik Commit changes.

DEPLOY RENDER
-------------
1. Pastikan database lama kehadiran-guru-db masih Available.
2. Salin Internal Database URL.
3. Render > New > Blueprint.
4. Sambungkan repository V9 Final.
5. Isi:
   DATABASE_URL = Internal Database URL
   SCHOOL_LATITUDE = koordinat sekolah
   SCHOOL_LONGITUDE = koordinat sekolah
   ADMIN_USERNAME = admin
   ADMIN_PASSWORD = kata laluan kuat
   ADMIN_EMAIL = e-mel admin
   TEACHER_USERNAME = guru
   TEACHER_PASSWORD = kata laluan guru
   TEACHER_EMAIL = e-mel guru
6. Deploy Blueprint.

SEMAKAN
-------
https://kehadiran-guru-v9-final.onrender.com/health/

Keputusan yang betul:
{"status":"ok","database":"connected","version":"9-final"}

CATATAN PENTING
---------------
- Media swafoto pada pelan Render Free mungkin tidak kekal selepas restart.
- PostgreSQL menyimpan data rekod secara berterusan selagi database aktif.
- Database percuma Render mempunyai tarikh luput mengikut paparan akaun anda.
