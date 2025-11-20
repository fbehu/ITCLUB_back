[1mdiff --git a/.gitignore b/.gitignore[m
[1mindex 07d4b53..c13fd07 100755[m
[1m--- a/.gitignore[m
[1m+++ b/.gitignore[m
[36m@@ -162,7 +162,6 @@[m [mcython_debug/[m
 #  option (not recommended) you can uncomment the following to ignore the entire idea folder.[m
 .idea/[m
 main.txt[m
[31m-media/users_image/[m
 venv/[m
 db.sqlite3[m
 .env[m
[36m@@ -170,4 +169,3 @@[m [mdb.sqlite3[m
 *.pyc[m
 __pycache__/[m
 [m
[31m-media/[m
[1mdiff --git a/apps/users/admin.py b/apps/users/admin.py[m
[1mindex 759fbd1..f43343a 100755[m
[1m--- a/apps/users/admin.py[m
[1m+++ b/apps/users/admin.py[m
[36m@@ -9,7 +9,7 @@[m [mclass UserAdmin(BaseUserAdmin):[m
     form = CustomUserChangeForm[m
     add_form = CustomUserCreationForm[m
 [m
[31m-    list_display = ('username', 'phone_number', 'email', 'is_active', 'is_staff')[m
[32m+[m[32m    list_display = ('uuid', 'username', 'phone_number', 'email', 'is_active', 'is_staff')[m
     list_filter = ('is_staff', 'is_superuser', 'is_active', 'role')[m
 [m
     fieldsets = ([m
[1mdiff --git a/apps/users/serializers.py b/apps/users/serializers.py[m
[1mindex dae4b2f..ae510e3 100755[m
[1m--- a/apps/users/serializers.py[m
[1m+++ b/apps/users/serializers.py[m
[36m@@ -1,9 +1,12 @@[m
[32m+[m[32mimport os[m
[32m+[m[32mimport mimetypes[m
[32m+[m[32mimport base64[m
[32m+[m[32mfrom django.conf import settings[m
 from rest_framework import serializers[m
 from django.contrib.auth import authenticate[m
 from .models import User[m
 from drf_extra_fields.fields import Base64ImageField[m
 from rest_framework_simplejwt.tokens import RefreshToken[m
[31m-import base64[m
 [m
 [m
 def create_custom_jwt_for_user(user):[m
[36m@@ -38,6 +41,7 @@[m [mclass ImageToBase64Field(serializers.ImageField):[m
 #  USER SERIALIZER[m
 # ============================[m
 class UserSerializer(serializers.ModelSerializer):[m
[32m+[m[32m    image_qrkod = serializers.SerializerMethodField()[m
 [m
     class Meta:[m
         model = User[m
[36m@@ -61,6 +65,60 @@[m [mclass UserSerializer(serializers.ModelSerializer):[m
             "updated_at",[m
         ][m
 [m
[32m+[m[32m    def get_image_qrkod(self, obj):[m
[32m+[m[32m        """[m
[32m+[m[32m        Return base64 data URI for QR image:[m
[32m+[m[32m        - Prefer file in MEDIA_ROOT/qrcodesall whose filename starts with obj.uuid (e.g. ITC100.png)[m
[32m+[m[32m        - Fallback to obj.image_qrkod (ImageField) if present[m
[32m+[m[32m        - Return None if no image available[m
[32m+[m[32m        """[m
[32m+[m[32m        # prefer uuid-based file lookup[m
[32m+[m[32m        uuid_val = getattr(obj, "uuid", None)[m
[32m+[m[32m        qr_dir = os.path.join(settings.MEDIA_ROOT, "qrcodesall")[m
[32m+[m
[32m+[m[32m        def _encode_file(path):[m
[32m+[m[32m            try:[m
[32m+[m[32m                with open(path, "rb") as f:[m
[32m+[m[32m                    data = f.read()[m
[32m+[m[32m                mime, _ = mimetypes.guess_type(path)[m
[32m+[m[32m                if not mime:[m
[32m+[m[32m                    mime = "application/octet-stream"[m
[32m+[m[32m                b64 = base64.b64encode(data).decode("utf-8")[m
[32m+[m[32m                return f"data:{mime};base64,{b64}"[m
[32m+[m[32m            except Exception:[m
[32m+[m[32m                return None[m
[32m+[m
[32m+[m[32m        if uuid_val:[m
[32m+[m[32m            try:[m
[32m+[m[32m                for fname in os.listdir(qr_dir):[m
[32m+[m[32m                    if fname.startswith(str(uuid_val)):[m
[32m+[m[32m                        full = os.path.join(qr_dir, fname)[m
[32m+[m[32m                        if os.path.isfile(full):[m
[32m+[m[32m                            return _encode_file(full)[m
[32m+[m[32m            except FileNotFoundError:[m
[32m+[m[32m                pass  # qrcodesall folder not present[m
[32m+[m
[32m+[m[32m        # fallback: use image_qrkod ImageField on the model if set[m
[32m+[m[32m        image_field = getattr(obj, "image_qrkod", None)[m
[32m+[m[32m        if image_field:[m
[32m+[m[32m            try:[m
[32m+[m[32m                path = image_field.path[m
[32m+[m[32m                if os.path.isfile(path):[m
[32m+[m[32m                    return _encode_file(path)[m
[32m+[m[32m            except Exception:[m
[32m+[m[32m                # image_field may be a URL-only field or missing file[m
[32m+[m[32m                try:[m
[32m+[m[32m                    # try to resolve by MEDIA_ROOT + name[m
[32m+[m[32m                    name = getattr(image_field, "name", None)[m
[32m+[m[32m                    if name:[m
[32m+[m[32m                        path = os.path.join(settings.MEDIA_ROOT, name)[m
[32m+[m[32m                        if os.path.isfile(path):[m
[32m+[m[32m                            return _encode_file(path)[m
[32m+[m[32m                except Exception:[m
[32m+[m[32m                    pass[m
[32m+[m
[32m+[m[32m        return None[m
[32m+[m
 [m
 # ============================[m
 #  REGISTER SERIALIZER[m
[1mdiff --git a/config/settings.py b/config/settings.py[m
[1mindex 74bdf4b..4f35965 100755[m
[1m--- a/config/settings.py[m
[1m+++ b/config/settings.py[m
[36m@@ -134,7 +134,7 @@[m [mDATABASES = {[m
 [m
 [m
 # Sqlite uchun sozlama[m
[31m-# DATABASES = {[m
[32m+[m[32m# DATABASES = {[m[41m   [m
 #    'default': {[m
 #        'ENGINE': 'django.db.backends.sqlite3',[m
 #        'NAME': BASE_DIR / 'db.sqlite3',[m
[36m@@ -197,7 +197,6 @@[m [mUSE_TZ = True[m
 [m
 STATIC_URL = '/static/'[m
 STATIC_ROOT = BASE_DIR / 'staticfiles'[m
[31m-[m
 MEDIA_URL = '/media/'[m
 MEDIA_ROOT = BASE_DIR / 'media'[m
 [m
[1mdiff --git a/media/qr_codes/ITC092.png b/media/qr_codes/ITC092.png[m
[1mnew file mode 100644[m
[1mindex 0000000..9ea0197[m
Binary files /dev/null and b/media/qr_codes/ITC092.png differ
[1mdiff --git a/media/qr_codes/ITC097.png b/media/qr_codes/ITC097.png[m
[1mnew file mode 100644[m
[1mindex 0000000..8972539[m
Binary files /dev/null and b/media/qr_codes/ITC097.png differ
[1mdiff --git a/media/qr_codes/photo_2025-11-15_23-31-11.jpg b/media/qr_codes/photo_2025-11-15_23-31-11.jpg[m
[1mnew file mode 100644[m
[1mindex 0000000..889c55c[m
Binary files /dev/null and b/media/qr_codes/photo_2025-11-15_23-31-11.jpg differ
[1mdiff --git a/media/qrcodesall/ITC000.png b/media/qrcodesall/ITC000.png[m
[1mnew file mode 100644[m
[1mindex 0000000..af76910[m
Binary files /dev/null and b/media/qrcodesall/ITC000.png differ
[1mdiff --git a/media/qrcodesall/ITC001.png b/media/qrcodesall/ITC001.png[m
[1mnew file mode 100644[m
[1mindex 0000000..5824e80[m
Binary files /dev/null and b/media/qrcodesall/ITC001.png differ
[1mdiff --git a/media/qrcodesall/ITC002.png b/media/qrcodesall/ITC002.png[m
[1mnew file mode 100644[m
[1mindex 0000000..892ca39[m
Binary files /dev/null and b/media/qrcodesall/ITC002.png differ
[1mdiff --git a/media/qrcodesall/ITC003.png b/media/qrcodesall/ITC003.png[m
[1mnew file mode 100644[m
[1mindex 0000000..6b611ed[m
Binary files /dev/null and b/media/qrcodesall/ITC003.png differ
[1mdiff --git a/media/qrcodesall/ITC004.png b/media/qrcodesall/ITC004.png[m
[1mnew file mode 100644[m
[1mindex 0000000..da13731[m
Binary files /dev/null and b/media/qrcodesall/ITC004.png differ
[1mdiff --git a/media/qrcodesall/ITC005.png b/media/qrcodesall/ITC005.png[m
[1mnew file mode 100644[m
[1mindex 0000000..99c2513[m
Binary files /dev/null and b/media/qrcodesall/ITC005.png differ
[1mdiff --git a/media/qrcodesall/ITC006.png b/media/qrcodesall/ITC006.png[m
[1mnew file mode 100644[m
[1mindex 0000000..0f82b85[m
Binary files /dev/null and b/media/qrcodesall/ITC006.png differ
[1mdiff --git a/media/qrcodesall/ITC007.png b/media/qrcodesall/ITC007.png[m
[1mnew file mode 100644[m
[1mindex 0000000..a1c6679[m
Binary files /dev/null and b/media/qrcodesall/ITC007.png differ
[1mdiff --git a/media/qrcodesall/ITC008.png b/media/qrcodesall/ITC008.png[m
[1mnew file mode 100644[m
[1mindex 0000000..3853e32[m
Binary files /dev/null and b/media/qrcodesall/ITC008.png differ
[1mdiff --git a/media/qrcodesall/ITC009.png b/media/qrcodesall/ITC009.png[m
[1mnew file mode 100644[m
[1mindex 0000000..2f76694[m
Binary files /dev/null and b/media/qrcodesall/ITC009.png differ
[1mdiff --git a/media/qrcodesall/ITC010.png b/media/qrcodesall/ITC010.png[m
[1mnew file mode 100644[m
[1mindex 0000000..5146c99[m
Binary files /dev/null and b/media/qrcodesall/ITC010.png differ
[1mdiff --git a/media/qrcodesall/ITC011.png b/media/qrcodesall/ITC011.png[m
[1mnew file mode 100644[m
[1mindex 0000000..777f3d5[m
Binary files /dev/null and b/media/qrcodesall/ITC011.png differ
[1mdiff --git a/media/qrcodesall/ITC012.png b/media/qrcodesall/ITC012.png[m
[1mnew file mode 100644[m
[1mindex 0000000..e4879fc[m
Binary files /dev/null and b/media/qrcodesall/ITC012.png differ
[1mdiff --git a/media/qrcodesall/ITC013.png b/media/qrcodesall/ITC013.png[m
[1mnew file mode 100644[m
[1mindex 0000000..12101b9[m
Binary files /dev/null and b/media/qrcodesall/ITC013.png differ
[1mdiff --git a/media/qrcodesall/ITC014.png b/media/qrcodesall/ITC014.png[m
[1mnew file mode 100644[m
[1mindex 0000000..64715ff[m
Binary files /dev/null and b/media/qrcodesall/ITC014.png differ
[1mdiff --git a/media/qrcodesall/ITC015.png b/media/qrcodesall/ITC015.png[m
[1mnew file mode 100644[m
[1mindex 0000000..dfd633c[m
Binary files /dev/null and b/media/qrcodesall/ITC015.png differ
[1mdiff --git a/media/qrcodesall/ITC016.png b/media/qrcodesall/ITC016.png[m
[1mnew file mode 100644[m
[1mindex 0000000..b1ba17f[m
Binary files /dev/null and b/media/qrcodesall/ITC016.png differ
[1mdiff --git a/media/qrcodesall/ITC017.png b/media/qrcodesall/ITC017.png[m
[1mnew file mode 100644[m
[1mindex 0000000..ceaa6d2[m
Binary files /dev/null and b/media/qrcodesall/ITC017.png differ
[1mdiff --git a/media/qrcodesall/ITC018.png b/media/qrcodesall/ITC018.png[m
[1mnew file mode 100644[m
[1mindex 0000000..cdbc559[m
Binary files /dev/null and b/media/qrcodesall/ITC018.png differ
[1mdiff --git a/media/qrcodesall/ITC019.png b/media/qrcodesall/ITC019.png[m
[1mnew file mode 100644[m
[1mindex 0000000..1fcde02[m
Binary files /dev/null and b/media/qrcodesall/ITC019.png differ
[1mdiff --git a/media/qrcodesall/ITC020.png b/media/qrcodesall/ITC020.png[m
[1mnew file mode 100644[m
[1mindex 0000000..2e3cebc[m
Binary files /dev/null and b/media/qrcodesall/ITC020.png differ
[1mdiff --git a/media/qrcodesall/ITC021.png b/media/qrcodesall/ITC021.png[m
[1mnew file mode 100644[m
[1mindex 0000000..669f338[m
Binary files /dev/null and b/media/qrcodesall/ITC021.png differ
[1mdiff --git a/media/qrcodesall/ITC022.png b/media/qrcodesall/ITC022.png[m
[1mnew file mode 100644[m
[1mindex 0000000..27cb1e4[m
Binary files /dev/null and b/media/qrcodesall/ITC022.png differ
[1mdiff --git a/media/qrcodesall/ITC023.png b/media/qrcodesall/ITC023.png[m
[1mnew file mode 100644[m
[1mindex 0000000..a7dcbce[m
Binary files /dev/null and b/media/qrcodesall/ITC023.png differ
[1mdiff --git a/media/qrcodesall/ITC024.png b/media/qrcodesall/ITC024.png[m
[1mnew file mode 100644[m
[1mindex 0000000..089af65[m
Binary files /dev/null and b/media/qrcodesall/ITC024.png differ
[1mdiff --git a/media/qrcodesall/ITC025.png b/media/qrcodesall/ITC025.png[m
[1mnew file mode 100644[m
[1mindex 0000000..b13de30[m
Binary files /dev/null and b/media/qrcodesall/ITC025.png differ
[1mdiff --git a/media/qrcodesall/ITC026.png b/media/qrcodesall/ITC026.png[m
[1mnew file mode 100644[m
[1mindex 0000000..8df856d[m
Binary files /dev/null and b/media/qrcodesall/ITC026.png differ
[1mdiff --git a/media/qrcodesall/ITC027.png b/media/qrcodesall/ITC027.png[m
[1mnew file mode 100644[m
[1mindex 0000000..de581bb[m
Binary files /dev/null and b/media/qrcodesall/ITC027.png differ
[1mdiff --git a/media/qrcodesall/ITC028.png b/media/qrcodesall/ITC028.png[m
[1mnew file mode 100644[m
[1mindex 0000000..a3afdb8[m
Binary files /dev/null and b/media/qrcodesall/ITC028.png differ
[1mdiff --git a/media/qrcodesall/ITC029.png b/media/qrcodesall/ITC029.png[m
[1mnew file mode 100644[m
[1mindex 0000000..b943500[m
Binary files /dev/null and b/media/qrcodesall/ITC029.png differ
[1mdiff --git a/media/qrcodesall/ITC030.png b/media/qrcodesall/ITC030.png[m
[1mnew file mode 100644[m
[1mindex 0000000..3394803[m
Binary files /dev/null and b/media/qrcodesall/ITC030.png differ
[1mdiff --git a/media/qrcodesall/ITC031.png b/media/qrcodesall/ITC031.png[m
[1mnew file mode 100644[m
[1mindex 0000000..0f856cc[m
Binary files /dev/null and b/media/qrcodesall/ITC031.png differ
[1mdiff --git a/media/qrcodesall/ITC032.png b/media/qrcodesall/ITC032.png[m
[1mnew file mode 100644[m
[1mindex 0000000..075fa5f[m
Binary files /dev/null and b/media/qrcodesall/ITC032.png differ
[1mdiff --git a/media/qrcodesall/ITC033.png b/media/qrcodesall/ITC033.png[m
[1mnew file mode 100644[m
[1mindex 0000000..51073bb[m
Binary files /dev/null and b/media/qrcodesall/ITC033.png differ
[1mdiff --git a/media/qrcodesall/ITC034.png b/media/qrcodesall/ITC034.png[m
[1mnew file mode 100644[m
[1mindex 0000000..5e942d3[m
Binary files /dev/null and b/media/qrcodesall/ITC034.png differ
[1mdiff --git a/media/qrcodesall/ITC035.png b/media/qrcodesall/ITC035.png[m
[1mnew file mode 100644[m
[1mindex 0000000..af9f948[m
Binary files /dev/null and b/media/qrcodesall/ITC035.png differ
[1mdiff --git a/media/qrcodesall/ITC036.png b/media/qrcodesall/ITC036.png[m
[1mnew file mode 100644[m
[1mindex 0000000..bd9cf97[m
Binary files /dev/null and b/media/qrcodesall/ITC036.png differ
[1mdiff --git a/media/qrcodesall/ITC037.png b/media/qrcodesall/ITC037.png[m
[1mnew file mode 100644[m
[1mindex 0000000..265e97a[m
Binary files /dev/null and b/media/qrcodesall/ITC037.png differ
[1mdiff --git a/media/qrcodesall/ITC038.png b/media/qrcodesall/ITC038.png[m
[1mnew file mode 100644[m
[1mindex 0000000..d1be5ed[m
Binary files /dev/null and b/media/qrcodesall/ITC038.png differ
[1mdiff --git a/media/qrcodesall/ITC039.png b/media/qrcodesall/ITC039.png[m
[1mnew file mode 100644[m
[1mindex 0000000..269324c[m
Binary files /dev/null and b/media/qrcodesall/ITC039.png differ
[1mdiff --git a/media/qrcodesall/ITC040.png b/media/qrcodesall/ITC040.png[m
[1mnew file mode 100644[m
[1mindex 0000000..032f00f[m
Binary files /dev/null and b/media/qrcodesall/ITC040.png differ
[1mdiff --git a/media/qrcodesall/ITC041.png b/media/qrcodesall/ITC041.png[m
[1mnew file mode 100644[m
[1mindex 0000000..4300d0e[m
Binary files /dev/null and b/media/qrcodesall/ITC041.png differ
[1mdiff --git a/media/qrcodesall/ITC042.png b/media/qrcodesall/ITC042.png[m
[1mnew file mode 100644[m
[1mindex 0000000..87167e0[m
Binary files /dev/null and b/media/qrcodesall/ITC042.png differ
[1mdiff --git a/media/qrcodesall/ITC043.png b/media/qrcodesall/ITC043.png[m
[1mnew file mode 100644[m
[1mindex 0000000..02b1f55[m
Binary files /dev/null and b/media/qrcodesall/ITC043.png differ
[1mdiff --git a/media/qrcodesall/ITC044.png b/media/qrcodesall/ITC044.png[m
[1mnew file mode 100644[m
[1mindex 0000000..8f53c42[m
Binary files /dev/null and b/media/qrcodesall/ITC044.png differ
[1mdiff --git a/media/qrcodesall/ITC045.png b/media/qrcodesall/ITC045.png[m
[1mnew file mode 100644[m
[1mindex 0000000..7de90f1[m
Binary files /dev/null and b/media/qrcodesall/ITC045.png differ
[1mdiff --git a/media/qrcodesall/ITC046.png b/media/qrcodesall/ITC046.png[m
[1mnew file mode 100644[m
[1mindex 0000000..e6ca680[m
Binary files /dev/null and b/media/qrcodesall/ITC046.png differ
[1mdiff --git a/media/qrcodesall/ITC047.png b/media/qrcodesall/ITC047.png[m
[1mnew file mode 100644[m
[1mindex 0000000..7412f55[m
Binary files /dev/null and b/media/qrcodesall/ITC047.png differ
[1mdiff --git a/media/qrcodesall/ITC048.png b/media/qrcodesall/ITC048.png[m
[1mnew file mode 100644[m
[1mindex 0000000..a2db30c[m
Binary files /dev/null and b/media/qrcodesall/ITC048.png differ
[1mdiff --git a/media/qrcodesall/ITC049.png b/media/qrcodesall/ITC049.png[m
[1mnew file mode 100644[m
[1mindex 0000000..462fc0b[m
Binary files /dev/null and b/media/qrcodesall/ITC049.png differ
[1mdiff --git a/media/qrcodesall/ITC050.png b/media/qrcodesall/ITC050.png[m
[1mnew file mode 100644[m
[1mindex 0000000..c9ee2a9[m
Binary files /dev/null and b/media/qrcodesall/ITC050.png differ
[1mdiff --git a/media/qrcodesall/ITC051.png b/media/qrcodesall/ITC051.png[m
[1mnew file mode 100644[m
[1mindex 0000000..21e1ff0[m
Binary files /dev/null and b/media/qrcodesall/ITC051.png differ
[1mdiff --git a/media/qrcodesall/ITC052.png b/media/qrcodesall/ITC052.png[m
[1mnew file mode 100644[m
[1mindex 0000000..f9255dc[m
Binary files /dev/null and b/media/qrcodesall/ITC052.png differ
[1mdiff --git a/media/qrcodesall/ITC053.png b/media/qrcodesall/ITC053.png[m
[1mnew file mode 100644[m
[1mindex 0000000..efa4026[m
Binary files /dev/null and b/media/qrcodesall/ITC053.png differ
[1mdiff --git a/media/qrcodesall/ITC054.png b/media/qrcodesall/ITC054.png[m
[1mnew file mode 100644[m
[1mindex 0000000..6103fd8[m
Binary files /dev/null and b/media/qrcodesall/ITC054.png differ
[1mdiff --git a/media/qrcodesall/ITC055.png b/media/qrcodesall/ITC055.png[m
[1mnew file mode 100644[m
[1mindex 0000000..899d9a6[m
Binary files /dev/null and b/media/qrcodesall/ITC055.png differ
[1mdiff --git a/media/qrcodesall/ITC056.png b/media/qrcodesall/ITC056.png[m
[1mnew file mode 100644[m
[1mindex 0000000..e62db05[m
Binary files /dev/null and b/media/qrcodesall/ITC056.png differ
[1mdiff --git a/media/qrcodesall/ITC057.png b/media/qrcodesall/ITC057.png[m
[1mnew file mode 100644[m
[1mindex 0000000..6543ea2[m
Binary files /dev/null and b/media/qrcodesall/ITC057.png differ
[1mdiff --git a/media/qrcodesall/ITC058.png b/media/qrcodesall/ITC058.png[m
[1mnew file mode 100644[m
[1mindex 0000000..a9f3339[m
Binary files /dev/null and b/media/qrcodesall/ITC058.png differ
[1mdiff --git a/media/qrcodesall/ITC059.png b/media/qrcodesall/ITC059.png[m
[1mnew file mode 100644[m
[1mindex 0000000..41c2441[m
Binary files /dev/null and b/media/qrcodesall/ITC059.png differ
[1mdiff --git a/media/qrcodesall/ITC060.png b/media/qrcodesall/ITC060.png[m
[1mnew file mode 100644[m
[1mindex 0000000..851dba6[m
Binary files /dev/null and b/media/qrcodesall/ITC060.png differ
[1mdiff --git a/media/qrcodesall/ITC061.png b/media/qrcodesall/ITC061.png[m
[1mnew file mode 100644[m
[1mindex 0000000..ee9741a[m
Binary files /dev/null and b/media/qrcodesall/ITC061.png differ
[1mdiff --git a/media/qrcodesall/ITC062.png b/media/qrcodesall/ITC062.png[m
[1mnew file mode 100644[m
[1mindex 0000000..dfe202d[m
Binary files /dev/null and b/media/qrcodesall/ITC062.png differ
[1mdiff --git a/media/qrcodesall/ITC063.png b/media/qrcodesall/ITC063.png[m
[1mnew file mode 100644[m
[1mindex 0000000..7b1c3b6[m
Binary files /dev/null and b/media/qrcodesall/ITC063.png differ
[1mdiff --git a/media/qrcodesall/ITC064.png b/media/qrcodesall/ITC064.png[m
[1mnew file mode 100644[m
[1mindex 0000000..dd416a2[m
Binary files /dev/null and b/media/qrcodesall/ITC064.png differ
[1mdiff --git a/media/qrcodesall/ITC065.png b/media/qrcodesall/ITC065.png[m
[1mnew file mode 100644[m
[1mindex 0000000..37425d3[m
Binary files /dev/null and b/media/qrcodesall/ITC065.png differ
[1mdiff --git a/media/qrcodesall/ITC066.png b/media/qrcodesall/ITC066.png[m
[1mnew file mode 100644[m
[1mindex 0000000..e00b1b1[m
Binary files /dev/null and b/media/qrcodesall/ITC066.png differ
[1mdiff --git a/media/qrcodesall/ITC067.png b/media/qrcodesall/ITC067.png[m
[1mnew file mode 100644[m
[1mindex 0000000..df94939[m
Binary files /dev/null and b/media/qrcodesall/ITC067.png differ
[1mdiff --git a/media/qrcodesall/ITC068.png b/media/qrcodesall/ITC068.png[m
[1mnew file mode 100644[m
[1mindex 0000000..e6e72b1[m
Binary files /dev/null and b/media/qrcodesall/ITC068.png differ
[1mdiff --git a/media/qrcodesall/ITC069.png b/media/qrcodesall/ITC069.png[m
[1mnew file mode 100644[m
[1mindex 0000000..75ed5ca[m
Binary files /dev/null and b/media/qrcodesall/ITC069.png differ
[1mdiff --git a/media/qrcodesall/ITC070.png b/media/qrcodesall/ITC070.png[m
[1mnew file mode 100644[m
[1mindex 0000000..e569a38[m
Binary files /dev/null and b/media/qrcodesall/ITC070.png differ
[1mdiff --git a/media/qrcodesall/ITC071.png b/media/qrcodesall/ITC071.png[m
[1mnew file mode 100644[m
[1mindex 0000000..35dba4e[m
Binary files /dev/null and b/media/qrcodesall/ITC071.png differ
[1mdiff --git a/media/qrcodesall/ITC072.png b/media/qrcodesall/ITC072.png[m
[1mnew file mode 100644[m
[1mindex 0000000..55aa047[m
Binary files /dev/null and b/media/qrcodesall/ITC072.png differ
[1mdiff --git a/media/qrcodesall/ITC073.png b/media/qrcodesall/ITC073.png[m
[1mnew file mode 100644[m
[1mindex 0000000..84dc917[m
Binary files /dev/null and b/media/qrcodesall/ITC073.png differ
[1mdiff --git a/media/qrcodesall/ITC074.png b/media/qrcodesall/ITC074.png[m
[1mnew file mode 100644[m
[1mindex 0000000..f0fda73[m
Binary files /dev/null and b/media/qrcodesall/ITC074.png differ
[1mdiff --git a/media/qrcodesall/ITC075.png b/media/qrcodesall/ITC075.png[m
[1mnew file mode 100644[m
[1mindex 0000000..7e67311[m
Binary files /dev/null and b/media/qrcodesall/ITC075.png differ
[1mdiff --git a/media/qrcodesall/ITC076.png b/media/qrcodesall/ITC076.png[m
[1mnew file mode 100644[m
[1mindex 0000000..7a3dfe4[m
Binary files /dev/null and b/media/qrcodesall/ITC076.png differ
[1mdiff --git a/media/qrcodesall/ITC077.png b/media/qrcodesall/ITC077.png[m
[1mnew file mode 100644[m
[1mindex 0000000..d080cf3[m
Binary files /dev/null and b/media/qrcodesall/ITC077.png differ
[1mdiff --git a/media/qrcodesall/ITC078.png b/media/qrcodesall/ITC078.png[m
[1mnew file mode 100644[m
[1mindex 0000000..a47ed43[m
Binary files /dev/null and b/media/qrcodesall/ITC078.png differ
[1mdiff --git a/media/qrcodesall/ITC079.png b/media/qrcodesall/ITC079.png[m
[1mnew file mode 100644[m
[1mindex 0000000..20e89b1[m
Binary files /dev/null and b/media/qrcodesall/ITC079.png differ
[1mdiff --git a/media/qrcodesall/ITC080.png b/media/qrcodesall/ITC080.png[m
[1mnew file mode 100644[m
[1mindex 0000000..f300c1d[m
Binary files /dev/null and b/media/qrcodesall/ITC080.png differ
[1mdiff --git a/media/qrcodesall/ITC081.png b/media/qrcodesall/ITC081.png[m
[1mnew file mode 100644[m
[1mindex 0000000..f018407[m
Binary files /dev/null and b/media/qrcodesall/ITC081.png differ
[1mdiff --git a/media/qrcodesall/ITC082.png b/media/qrcodesall/ITC082.png[m
[1mnew file mode 100644[m
[1mindex 0000000..fbcd833[m
Binary files /dev/null and b/media/qrcodesall/ITC082.png differ
[1mdiff --git a/media/qrcodesall/ITC083.png b/media/qrcodesall/ITC083.png[m
[1mnew file mode 100644[m
[1mindex 0000000..46c8043[m
Binary files /dev/null and b/media/qrcodesall/ITC083.png differ
[1mdiff --git a/media/qrcodesall/ITC084.png b/media/qrcodesall/ITC084.png[m
[1mnew file mode 100644[m
[1mindex 0000000..25f6067[m
Binary files /dev/null and b/media/qrcodesall/ITC084.png differ
[1mdiff --git a/media/qrcodesall/ITC085.png b/media/qrcodesall/ITC085.png[m
[1mnew file mode 100644[m
[1mindex 0000000..8823ac0[m
Binary files /dev/null and b/media/qrcodesall/ITC085.png differ
[1mdiff --git a/media/qrcodesall/ITC086.png b/media/qrcodesall/ITC086.png[m
[1mnew file mode 100644[m
[1mindex 0000000..33070b1[m
Binary files /dev/null and b/media/qrcodesall/ITC086.png differ
[1mdiff --git a/media/qrcodesall/ITC087.png b/media/qrcodesall/ITC087.png[m
[1mnew file mode 100644[m
[1mindex 0000000..c0dd9a9[m
Binary files /dev/null and b/media/qrcodesall/ITC087.png differ
[1mdiff --git a/media/qrcodesall/ITC088.png b/media/qrcodesall/ITC088.png[m
[1mnew file mode 100644[m
[1mindex 0000000..8454edf[m
Binary files /dev/null and b/media/qrcodesall/ITC088.png differ
[1mdiff --git a/media/qrcodesall/ITC089.png b/media/qrcodesall/ITC089.png[m
[1mnew file mode 100644[m
[1mindex 0000000..760a20e[m
Binary files /dev/null and b/media/qrcodesall/ITC089.png differ
[1mdiff --git a/media/qrcodesall/ITC090.png b/media/qrcodesall/ITC090.png[m
[1mnew file mode 100644[m
[1mindex 0000000..5468b4f[m
Binary files /dev/null and b/media/qrcodesall/ITC090.png differ
[1mdiff --git a/media/qrcodesall/ITC091.png b/media/qrcodesall/ITC091.png[m
[1mnew file mode 100644[m
[1mindex 0000000..e524891[m
Binary files /dev/null and b/media/qrcodesall/ITC091.png differ
[1mdiff --git a/media/qrcodesall/ITC092.png b/media/qrcodesall/ITC092.png[m
[1mnew file mode 100644[m
[1mindex 0000000..9ea0197[m
Binary files /dev/null and b/media/qrcodesall/ITC092.png differ
[1mdiff --git a/media/qrcodesall/ITC093.png b/media/qrcodesall/ITC093.png[m
[1mnew file mode 100644[m
[1mindex 0000000..d8e1d71[m
Binary files /dev/null and b/media/qrcodesall/ITC093.png differ
[1mdiff --git a/media/qrcodesall/ITC094.png b/media/qrcodesall/ITC094.png[m
[1mnew file mode 100644[m
[1mindex 0000000..bf9e7bf[m
Binary files /dev/null and b/media/qrcodesall/ITC094.png differ
[1mdiff --git a/media/qrcodesall/ITC095.png b/media/qrcodesall/ITC095.png[m
[1mnew file mode 100644[m
[1mindex 0000000..47fe39e[m
Binary files /dev/null and b/media/qrcodesall/ITC095.png differ
[1mdiff --git a/media/qrcodesall/ITC096.png b/media/qrcodesall/ITC096.png[m
[1mnew file mode 100644[m
[1mindex 0000000..72ed0b8[m
Binary files /dev/null and b/media/qrcodesall/ITC096.png differ
[1mdiff --git a/media/qrcodesall/ITC097.png b/media/qrcodesall/ITC097.png[m
[1mnew file mode 100644[m
[1mindex 0000000..8972539[m
Binary files /dev/null and b/media/qrcodesall/ITC097.png differ
[1mdiff --git a/media/qrcodesall/ITC098.png b/media/qrcodesall/ITC098.png[m
[1mnew file mode 100644[m
[1mindex 0000000..305762f[m
Binary files /dev/null and b/media/qrcodesall/ITC098.png differ
[1mdiff --git a/media/qrcodesall/ITC099.png b/media/qrcodesall/ITC099.png[m
[1mnew file mode 100644[m
[1mindex 0000000..4f2c3e2[m
Binary files /dev/null and b/media/qrcodesall/ITC099.png differ
[1mdiff --git a/media/qrcodesall/ITC100.png b/media/qrcodesall/ITC100.png[m
[1mnew file mode 100644[m
[1mindex 0000000..775af63[m
Binary files /dev/null and b/media/qrcodesall/ITC100.png differ
[1mdiff --git a/media/qrcodesall/ITC101.png b/media/qrcodesall/ITC101.png[m
[1mnew file mode 100644[m
[1mindex 0000000..ed937f3[m
Binary files /dev/null and b/media/qrcodesall/ITC101.png differ
[1mdiff --git a/media/qrcodesall/ITC111.png b/media/qrcodesall/ITC111.png[m
[1mnew file mode 100644[m
[1mindex 0000000..1feca61[m
Binary files /dev/null and b/media/qrcodesall/ITC111.png differ
[1mdiff --git a/media/qrcodesall/ITC121.png b/media/qrcodesall/ITC121.png[m
[1mnew file mode 100644[m
[1mindex 0000000..ac2da53[m
Binary files /dev/null and b/media/qrcodesall/ITC121.png differ
[1mdiff --git a/media/qrcodesall/ITC123.png b/media/qrcodesall/ITC123.png[m
[1mnew file mode 100644[m
[1mindex 0000000..1f6e294[m
Binary files /dev/null and b/media/qrcodesall/ITC123.png differ
[1mdiff --git a/media/qrcodesall/ITC171.png b/media/qrcodesall/ITC171.png[m
[1mnew file mode 100644[m
[1mindex 0000000..8fab284[m
Binary files /dev/null and b/media/qrcodesall/ITC171.png differ
[1mdiff --git a/media/qrcodesall/ITC199.png b/media/qrcodesall/ITC199.png[m
[1mnew file mode 100644[m
[1mindex 0000000..9e8dad0[m
Binary files /dev/null and b/media/qrcodesall/ITC199.png differ
[1mdiff --git a/media/qrcodesall/ITC200.png b/media/qrcodesall/ITC200.png[m
[1mnew file mode 100644[m
[1mindex 0000000..68c5cbd[m
Binary files /dev/null and b/media/qrcodesall/ITC200.png differ
[1mdiff --git a/media/qrcodesall/ITC212.png b/media/qrcodesall/ITC212.png[m
[1mnew file mode 100644[m
[1mindex 0000000..6806055[m
Binary files /dev/null and b/media/qrcodesall/ITC212.png differ
[1mdiff --git a/media/qrcodesall/ITC222.png b/media/qrcodesall/ITC222.png[m
[1mnew file mode 100644[m
[1mindex 0000000..9eef266[m
Binary files /dev/null and b/media/qrcodesall/ITC222.png differ
[1mdiff --git a/media/qrcodesall/ITC234.png b/media/qrcodesall/ITC234.png[m
[1mnew file mode 100644[m
[1mindex 0000000..83f6af7[m
Binary files /dev/null and b/media/qrcodesall/ITC234.png differ
[1mdiff --git a/media/qrcodesall/ITC300.png b/media/qrcodesall/ITC300.png[m
[1mnew file mode 100644[m
[1mindex 0000000..f19cd15[m
Binary files /dev/null and b/media/qrcodesall/ITC300.png differ
[1mdiff --git a/media/qrcodesall/ITC303.png b/media/qrcodesall/ITC303.png[m
[1mnew file mode 100644[m
[1mindex 0000000..f7eb606[m
Binary files /dev/null and b/media/qrcodesall/ITC303.png differ
[1mdiff --git a/media/qrcodesall/ITC321.png b/media/qrcodesall/ITC321.png[m
[1mnew file mode 100644[m
[1mindex 0000000..b89c7cd[m
Binary files /dev/null and b/media/qrcodesall/ITC321.png differ
[1mdiff --git a/media/qrcodesall/ITC333.png b/media/qrcodesall/ITC333.png[m
[1mnew file mode 100644[m
[1mindex 0000000..59c18a8[m
Binary files /dev/null and b/media/qrcodesall/ITC333.png differ
[1mdiff --git a/media/qrcodesall/ITC400.png b/media/qrcodesall/ITC400.png[m
[1mnew file mode 100644[m
[1mindex 0000000..c481c97[m
Binary files /dev/null and b/media/qrcodesall/ITC400.png differ
[1mdiff --git a/media/qrcodesall/ITC404.png b/media/qrcodesall/ITC404.png[m
[1mnew file mode 100644[m
[1mindex 0000000..b6861c8[m
Binary files /dev/null and b/media/qrcodesall/ITC404.png differ
[1mdiff --git a/media/qrcodesall/ITC444.png b/media/qrcodesall/ITC444.png[m
[1mnew file mode 100644[m
[1mindex 0000000..beeb1e3[m
Binary files /dev/null and b/media/qrcodesall/ITC444.png differ
[1mdiff --git a/media/qrcodesall/ITC500.png b/media/qrcodesall/ITC500.png[m
[1mnew file mode 100644[m
[1mindex 0000000..17c6378[m
Binary files /dev/null and b/media/qrcodesall/ITC500.png differ
[1mdiff --git a/media/qrcodesall/ITC505.png b/media/qrcodesall/ITC505.png[m
[1mnew file mode 100644[m
[1mindex 0000000..2639c7e[m
Binary files /dev/null and b/media/qrcodesall/ITC505.png differ
[1mdiff --git a/media/qrcodesall/ITC555.png b/media/qrcodesall/ITC555.png[m
[1mnew file mode 100644[m
[1mindex 0000000..be0e226[m
Binary files /dev/null and b/media/qrcodesall/ITC555.png differ
[1mdiff --git a/media/qrcodesall/ITC600.png b/media/qrcodesall/ITC600.png[m
[1mnew file mode 100644[m
[1mindex 0000000..e64a81f[m
Binary files /dev/null and b/media/qrcodesall/ITC600.png differ
[1mdiff --git a/media/qrcodesall/ITC666.png b/media/qrcodesall/ITC666.png[m
[1mnew file mode 100644[m
[1mindex 0000000..0794a4b[m
Binary files /dev/null and b/media/qrcodesall/ITC666.png differ
[1mdiff --git a/media/qrcodesall/ITC700.png b/media/qrcodesall/ITC700.png[m
[1mnew file mode 100644[m
[1mindex 0000000..ac6b9e0[m
Binary files /dev/null and b/media/qrcodesall/ITC700.png differ
[1mdiff --git a/media/qrcodesall/ITC777.png b/media/qrcodesall/ITC777.png[m
[1mnew file mode 100644[m
[1mindex 0000000..43b9c1f[m
Binary files /dev/null and b/media/qrcodesall/ITC777.png differ
[1mdiff --git a/media/qrcodesall/ITC800.png b/media/qrcodesall/ITC800.png[m
[1mnew file mode 100644[m
[1mindex 0000000..149c96f[m
Binary files /dev/null and b/media/qrcodesall/ITC800.png differ
[1mdiff --git a/media/qrcodesall/ITC888.png b/media/qrcodesall/ITC888.png[m
[1mnew file mode 100644[m
[1mindex 0000000..be89294[m
Binary files /dev/null and b/media/qrcodesall/ITC888.png differ
[1mdiff --git a/media/qrcodesall/ITC900.png b/media/qrcodesall/ITC900.png[m
[1mnew file mode 100644[m
[1mindex 0000000..d757222[m
Binary files /dev/null and b/media/qrcodesall/ITC900.png differ
[1mdiff --git a/media/qrcodesall/ITC909.png b/media/qrcodesall/ITC909.png[m
[1mnew file mode 100644[m
[1mindex 0000000..2147300[m
Binary files /dev/null and b/media/qrcodesall/ITC909.png differ
[1mdiff --git a/media/qrcodesall/ITC999.png b/media/qrcodesall/ITC999.png[m
[1mnew file mode 100644[m
[1mindex 0000000..db1ff6c[m
Binary files /dev/null and b/media/qrcodesall/ITC999.png differ
[1mdiff --git a/media/user_photos/2.jpg b/media/user_photos/2.jpg[m
[1mnew file mode 100644[m
[1mindex 0000000..9bb825e[m
Binary files /dev/null and b/media/user_photos/2.jpg differ
[1mdiff --git a/media/user_photos/65543.jpeg b/media/user_photos/65543.jpeg[m
[1mnew file mode 100644[m
[1mindex 0000000..1e020c3[m
Binary files /dev/null and b/media/user_photos/65543.jpeg differ
[1mdiff --git a/media/user_photos/Screenshot_2025-11-03_09_28_43.png b/media/user_photos/Screenshot_2025-11-03_09_28_43.png[m
[1mnew file mode 100644[m
[1mindex 0000000..f85ff2b[m
Binary files /dev/null and b/media/user_photos/Screenshot_2025-11-03_09_28_43.png differ
[1mdiff --git a/media/user_photos/cyber.jpg b/media/user_photos/cyber.jpg[m
[1mnew file mode 100644[m
[1mindex 0000000..bafd4bf[m
Binary files /dev/null and b/media/user_photos/cyber.jpg differ
[1mdiff --git a/media/user_photos/cyber_FTRmA3m.jpg b/media/user_photos/cyber_FTRmA3m.jpg[m
[1mnew file mode 100644[m
[1mindex 0000000..bafd4bf[m
Binary files /dev/null and b/media/user_photos/cyber_FTRmA3m.jpg differ
[1mdiff --git a/staticfiles/admin/css/autocomplete.css b/staticfiles/admin/css/autocomplete.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/css/base.css b/staticfiles/admin/css/base.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/css/changelists.css b/staticfiles/admin/css/changelists.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/css/dark_mode.css b/staticfiles/admin/css/dark_mode.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/css/dashboard.css b/staticfiles/admin/css/dashboard.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/css/forms.css b/staticfiles/admin/css/forms.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/css/login.css b/staticfiles/admin/css/login.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/css/nav_sidebar.css b/staticfiles/admin/css/nav_sidebar.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/css/responsive.css b/staticfiles/admin/css/responsive.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/css/responsive_rtl.css b/staticfiles/admin/css/responsive_rtl.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/css/rtl.css b/staticfiles/admin/css/rtl.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/css/unusable_password_field.css b/staticfiles/admin/css/unusable_password_field.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/css/vendor/select2/LICENSE-SELECT2.md b/staticfiles/admin/css/vendor/select2/LICENSE-SELECT2.md[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/css/vendor/select2/select2.css b/staticfiles/admin/css/vendor/select2/select2.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/css/vendor/select2/select2.min.css b/staticfiles/admin/css/vendor/select2/select2.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/css/widgets.css b/staticfiles/admin/css/widgets.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/LICENSE b/staticfiles/admin/img/LICENSE[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/README.txt b/staticfiles/admin/img/README.txt[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/calendar-icons.svg b/staticfiles/admin/img/calendar-icons.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/gis/move_vertex_off.svg b/staticfiles/admin/img/gis/move_vertex_off.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/gis/move_vertex_on.svg b/staticfiles/admin/img/gis/move_vertex_on.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/icon-addlink.svg b/staticfiles/admin/img/icon-addlink.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/icon-alert.svg b/staticfiles/admin/img/icon-alert.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/icon-calendar.svg b/staticfiles/admin/img/icon-calendar.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/icon-changelink.svg b/staticfiles/admin/img/icon-changelink.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/icon-clock.svg b/staticfiles/admin/img/icon-clock.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/icon-deletelink.svg b/staticfiles/admin/img/icon-deletelink.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/icon-hidelink.svg b/staticfiles/admin/img/icon-hidelink.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/icon-no.svg b/staticfiles/admin/img/icon-no.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/icon-unknown-alt.svg b/staticfiles/admin/img/icon-unknown-alt.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/icon-unknown.svg b/staticfiles/admin/img/icon-unknown.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/icon-viewlink.svg b/staticfiles/admin/img/icon-viewlink.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/icon-yes.svg b/staticfiles/admin/img/icon-yes.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/inline-delete.svg b/staticfiles/admin/img/inline-delete.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/search.svg b/staticfiles/admin/img/search.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/selector-icons.svg b/staticfiles/admin/img/selector-icons.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/sorting-icons.svg b/staticfiles/admin/img/sorting-icons.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/tooltag-add.svg b/staticfiles/admin/img/tooltag-add.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/img/tooltag-arrowright.svg b/staticfiles/admin/img/tooltag-arrowright.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/SelectBox.js b/staticfiles/admin/js/SelectBox.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/SelectFilter2.js b/staticfiles/admin/js/SelectFilter2.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/actions.js b/staticfiles/admin/js/actions.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/admin/DateTimeShortcuts.js b/staticfiles/admin/js/admin/DateTimeShortcuts.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/admin/RelatedObjectLookups.js b/staticfiles/admin/js/admin/RelatedObjectLookups.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/autocomplete.js b/staticfiles/admin/js/autocomplete.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/calendar.js b/staticfiles/admin/js/calendar.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/cancel.js b/staticfiles/admin/js/cancel.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/change_form.js b/staticfiles/admin/js/change_form.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/core.js b/staticfiles/admin/js/core.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/filters.js b/staticfiles/admin/js/filters.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/inlines.js b/staticfiles/admin/js/inlines.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/jquery.init.js b/staticfiles/admin/js/jquery.init.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/nav_sidebar.js b/staticfiles/admin/js/nav_sidebar.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/popup_response.js b/staticfiles/admin/js/popup_response.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/prepopulate.js b/staticfiles/admin/js/prepopulate.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/prepopulate_init.js b/staticfiles/admin/js/prepopulate_init.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/theme.js b/staticfiles/admin/js/theme.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/unusable_password_field.js b/staticfiles/admin/js/unusable_password_field.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/urlify.js b/staticfiles/admin/js/urlify.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/jquery/LICENSE.txt b/staticfiles/admin/js/vendor/jquery/LICENSE.txt[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/jquery/jquery.js b/staticfiles/admin/js/vendor/jquery/jquery.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/jquery/jquery.min.js b/staticfiles/admin/js/vendor/jquery/jquery.min.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/LICENSE.md b/staticfiles/admin/js/vendor/select2/LICENSE.md[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/af.js b/staticfiles/admin/js/vendor/select2/i18n/af.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/ar.js b/staticfiles/admin/js/vendor/select2/i18n/ar.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/az.js b/staticfiles/admin/js/vendor/select2/i18n/az.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/bg.js b/staticfiles/admin/js/vendor/select2/i18n/bg.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/bn.js b/staticfiles/admin/js/vendor/select2/i18n/bn.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/bs.js b/staticfiles/admin/js/vendor/select2/i18n/bs.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/ca.js b/staticfiles/admin/js/vendor/select2/i18n/ca.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/cs.js b/staticfiles/admin/js/vendor/select2/i18n/cs.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/da.js b/staticfiles/admin/js/vendor/select2/i18n/da.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/de.js b/staticfiles/admin/js/vendor/select2/i18n/de.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/dsb.js b/staticfiles/admin/js/vendor/select2/i18n/dsb.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/el.js b/staticfiles/admin/js/vendor/select2/i18n/el.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/en.js b/staticfiles/admin/js/vendor/select2/i18n/en.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/es.js b/staticfiles/admin/js/vendor/select2/i18n/es.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/et.js b/staticfiles/admin/js/vendor/select2/i18n/et.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/eu.js b/staticfiles/admin/js/vendor/select2/i18n/eu.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/fa.js b/staticfiles/admin/js/vendor/select2/i18n/fa.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/fi.js b/staticfiles/admin/js/vendor/select2/i18n/fi.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/fr.js b/staticfiles/admin/js/vendor/select2/i18n/fr.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/gl.js b/staticfiles/admin/js/vendor/select2/i18n/gl.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/he.js b/staticfiles/admin/js/vendor/select2/i18n/he.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/hi.js b/staticfiles/admin/js/vendor/select2/i18n/hi.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/hr.js b/staticfiles/admin/js/vendor/select2/i18n/hr.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/hsb.js b/staticfiles/admin/js/vendor/select2/i18n/hsb.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/hu.js b/staticfiles/admin/js/vendor/select2/i18n/hu.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/hy.js b/staticfiles/admin/js/vendor/select2/i18n/hy.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/id.js b/staticfiles/admin/js/vendor/select2/i18n/id.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/is.js b/staticfiles/admin/js/vendor/select2/i18n/is.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/it.js b/staticfiles/admin/js/vendor/select2/i18n/it.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/ja.js b/staticfiles/admin/js/vendor/select2/i18n/ja.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/ka.js b/staticfiles/admin/js/vendor/select2/i18n/ka.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/km.js b/staticfiles/admin/js/vendor/select2/i18n/km.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/ko.js b/staticfiles/admin/js/vendor/select2/i18n/ko.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/lt.js b/staticfiles/admin/js/vendor/select2/i18n/lt.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/lv.js b/staticfiles/admin/js/vendor/select2/i18n/lv.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/mk.js b/staticfiles/admin/js/vendor/select2/i18n/mk.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/ms.js b/staticfiles/admin/js/vendor/select2/i18n/ms.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/nb.js b/staticfiles/admin/js/vendor/select2/i18n/nb.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/ne.js b/staticfiles/admin/js/vendor/select2/i18n/ne.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/nl.js b/staticfiles/admin/js/vendor/select2/i18n/nl.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/pl.js b/staticfiles/admin/js/vendor/select2/i18n/pl.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/ps.js b/staticfiles/admin/js/vendor/select2/i18n/ps.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/pt-BR.js b/staticfiles/admin/js/vendor/select2/i18n/pt-BR.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/pt.js b/staticfiles/admin/js/vendor/select2/i18n/pt.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/ro.js b/staticfiles/admin/js/vendor/select2/i18n/ro.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/ru.js b/staticfiles/admin/js/vendor/select2/i18n/ru.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/sk.js b/staticfiles/admin/js/vendor/select2/i18n/sk.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/sl.js b/staticfiles/admin/js/vendor/select2/i18n/sl.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/sq.js b/staticfiles/admin/js/vendor/select2/i18n/sq.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/sr-Cyrl.js b/staticfiles/admin/js/vendor/select2/i18n/sr-Cyrl.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/sr.js b/staticfiles/admin/js/vendor/select2/i18n/sr.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/sv.js b/staticfiles/admin/js/vendor/select2/i18n/sv.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/th.js b/staticfiles/admin/js/vendor/select2/i18n/th.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/tk.js b/staticfiles/admin/js/vendor/select2/i18n/tk.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/tr.js b/staticfiles/admin/js/vendor/select2/i18n/tr.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/uk.js b/staticfiles/admin/js/vendor/select2/i18n/uk.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/vi.js b/staticfiles/admin/js/vendor/select2/i18n/vi.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/zh-CN.js b/staticfiles/admin/js/vendor/select2/i18n/zh-CN.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/i18n/zh-TW.js b/staticfiles/admin/js/vendor/select2/i18n/zh-TW.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/select2.full.js b/staticfiles/admin/js/vendor/select2/select2.full.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/select2/select2.full.min.js b/staticfiles/admin/js/vendor/select2/select2.full.min.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/xregexp/LICENSE.txt b/staticfiles/admin/js/vendor/xregexp/LICENSE.txt[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/xregexp/xregexp.js b/staticfiles/admin/js/vendor/xregexp/xregexp.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/admin/js/vendor/xregexp/xregexp.min.js b/staticfiles/admin/js/vendor/xregexp/xregexp.min.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/README b/staticfiles/drf-yasg/README[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/immutable.js b/staticfiles/drf-yasg/immutable.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/immutable.min.js b/staticfiles/drf-yasg/immutable.min.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/insQ.js b/staticfiles/drf-yasg/insQ.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/insQ.min.js b/staticfiles/drf-yasg/insQ.min.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/redoc-init.js b/staticfiles/drf-yasg/redoc-init.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/redoc-old/LICENSE b/staticfiles/drf-yasg/redoc-old/LICENSE[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/redoc-old/redoc.min.js b/staticfiles/drf-yasg/redoc-old/redoc.min.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/redoc-old/redoc.min.js.map b/staticfiles/drf-yasg/redoc-old/redoc.min.js.map[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/redoc/LICENSE b/staticfiles/drf-yasg/redoc/LICENSE[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/redoc/redoc-logo.png b/staticfiles/drf-yasg/redoc/redoc-logo.png[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/redoc/redoc.min.js b/staticfiles/drf-yasg/redoc/redoc.min.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/redoc/redoc.standalone.js.map b/staticfiles/drf-yasg/redoc/redoc.standalone.js.map[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/style.css b/staticfiles/drf-yasg/style.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/swagger-ui-dist/LICENSE b/staticfiles/drf-yasg/swagger-ui-dist/LICENSE[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/swagger-ui-dist/NOTICE b/staticfiles/drf-yasg/swagger-ui-dist/NOTICE[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/swagger-ui-dist/absolute-path.js b/staticfiles/drf-yasg/swagger-ui-dist/absolute-path.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/swagger-ui-dist/favicon-32x32.png b/staticfiles/drf-yasg/swagger-ui-dist/favicon-32x32.png[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/swagger-ui-dist/index.css b/staticfiles/drf-yasg/swagger-ui-dist/index.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/swagger-ui-dist/index.js b/staticfiles/drf-yasg/swagger-ui-dist/index.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/swagger-ui-dist/oauth2-redirect.html b/staticfiles/drf-yasg/swagger-ui-dist/oauth2-redirect.html[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/swagger-ui-dist/swagger-initializer.js b/staticfiles/drf-yasg/swagger-ui-dist/swagger-initializer.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui-bundle.js b/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui-bundle.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui-bundle.js.map b/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui-bundle.js.map[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle-core.js b/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle-core.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle-core.js.map b/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle-core.js.map[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle.js b/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle.js.map b/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle.js.map[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui-standalone-preset.js b/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui-standalone-preset.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui-standalone-preset.js.map b/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui-standalone-preset.js.map[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui.css b/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui.css.map b/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui.css.map[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui.js.map b/staticfiles/drf-yasg/swagger-ui-dist/swagger-ui.js.map[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/drf-yasg/swagger-ui-init.js b/staticfiles/drf-yasg/swagger-ui-init.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/jazzmin/css/main.css b/staticfiles/jazzmin/css/main.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/jazzmin/img/calendar-icons.svg b/staticfiles/jazzmin/img/calendar-icons.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/jazzmin/img/default-log.svg b/staticfiles/jazzmin/img/default-log.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/jazzmin/img/default.jpg b/staticfiles/jazzmin/img/default.jpg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/jazzmin/img/icon-calendar.svg b/staticfiles/jazzmin/img/icon-calendar.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/jazzmin/img/icon-changelink.svg b/staticfiles/jazzmin/img/icon-changelink.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/jazzmin/img/selector-icons.svg b/staticfiles/jazzmin/img/selector-icons.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/jazzmin/js/change_form.js b/staticfiles/jazzmin/js/change_form.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/jazzmin/js/change_list.js b/staticfiles/jazzmin/js/change_list.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/jazzmin/js/main.js b/staticfiles/jazzmin/js/main.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/jazzmin/js/related-modal.js b/staticfiles/jazzmin/js/related-modal.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/jazzmin/js/ui-builder.js b/staticfiles/jazzmin/js/ui-builder.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/jazzmin/plugins/bootstrap-show-modal/bootstrap-show-modal.min.js b/staticfiles/jazzmin/plugins/bootstrap-show-modal/bootstrap-show-modal.min.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/css/bootstrap-theme.min.css b/staticfiles/rest_framework/css/bootstrap-theme.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/css/bootstrap-theme.min.css.map b/staticfiles/rest_framework/css/bootstrap-theme.min.css.map[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/css/bootstrap-tweaks.css b/staticfiles/rest_framework/css/bootstrap-tweaks.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/css/bootstrap.min.css b/staticfiles/rest_framework/css/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/css/bootstrap.min.css.map b/staticfiles/rest_framework/css/bootstrap.min.css.map[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/css/default.css b/staticfiles/rest_framework/css/default.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/css/font-awesome-4.0.3.css b/staticfiles/rest_framework/css/font-awesome-4.0.3.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/css/prettify.css b/staticfiles/rest_framework/css/prettify.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/docs/css/base.css b/staticfiles/rest_framework/docs/css/base.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/docs/css/highlight.css b/staticfiles/rest_framework/docs/css/highlight.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/docs/css/jquery.json-view.min.css b/staticfiles/rest_framework/docs/css/jquery.json-view.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/docs/img/favicon.ico b/staticfiles/rest_framework/docs/img/favicon.ico[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/docs/img/grid.png b/staticfiles/rest_framework/docs/img/grid.png[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/docs/js/api.js b/staticfiles/rest_framework/docs/js/api.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/docs/js/highlight.pack.js b/staticfiles/rest_framework/docs/js/highlight.pack.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/docs/js/jquery.json-view.min.js b/staticfiles/rest_framework/docs/js/jquery.json-view.min.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/fonts/fontawesome-webfont.eot b/staticfiles/rest_framework/fonts/fontawesome-webfont.eot[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/fonts/fontawesome-webfont.svg b/staticfiles/rest_framework/fonts/fontawesome-webfont.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/fonts/fontawesome-webfont.ttf b/staticfiles/rest_framework/fonts/fontawesome-webfont.ttf[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/fonts/fontawesome-webfont.woff b/staticfiles/rest_framework/fonts/fontawesome-webfont.woff[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/fonts/glyphicons-halflings-regular.eot b/staticfiles/rest_framework/fonts/glyphicons-halflings-regular.eot[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/fonts/glyphicons-halflings-regular.svg b/staticfiles/rest_framework/fonts/glyphicons-halflings-regular.svg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/fonts/glyphicons-halflings-regular.ttf b/staticfiles/rest_framework/fonts/glyphicons-halflings-regular.ttf[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/fonts/glyphicons-halflings-regular.woff b/staticfiles/rest_framework/fonts/glyphicons-halflings-regular.woff[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/fonts/glyphicons-halflings-regular.woff2 b/staticfiles/rest_framework/fonts/glyphicons-halflings-regular.woff2[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/img/glyphicons-halflings-white.png b/staticfiles/rest_framework/img/glyphicons-halflings-white.png[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/img/glyphicons-halflings.png b/staticfiles/rest_framework/img/glyphicons-halflings.png[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/img/grid.png b/staticfiles/rest_framework/img/grid.png[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/js/ajax-form.js b/staticfiles/rest_framework/js/ajax-form.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/js/bootstrap.min.js b/staticfiles/rest_framework/js/bootstrap.min.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/js/coreapi-0.1.1.js b/staticfiles/rest_framework/js/coreapi-0.1.1.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/js/csrf.js b/staticfiles/rest_framework/js/csrf.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/js/default.js b/staticfiles/rest_framework/js/default.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/js/jquery-3.7.1.min.js b/staticfiles/rest_framework/js/jquery-3.7.1.min.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/js/load-ajax-form.js b/staticfiles/rest_framework/js/load-ajax-form.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/rest_framework/js/prettify-min.js b/staticfiles/rest_framework/js/prettify-min.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/adminlte/css/adminlte.min.css b/staticfiles/vendor/adminlte/css/adminlte.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/adminlte/css/adminlte.min.css.map b/staticfiles/vendor/adminlte/css/adminlte.min.css.map[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/adminlte/img/AdminLTELogo.png b/staticfiles/vendor/adminlte/img/AdminLTELogo.png[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/adminlte/img/icons.png b/staticfiles/vendor/adminlte/img/icons.png[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/adminlte/img/user2-160x160.jpg b/staticfiles/vendor/adminlte/img/user2-160x160.jpg[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/adminlte/js/adminlte.min.js b/staticfiles/vendor/adminlte/js/adminlte.min.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/adminlte/js/adminlte.min.js.map b/staticfiles/vendor/adminlte/js/adminlte.min.js.map[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootstrap/js/bootstrap.min.js b/staticfiles/vendor/bootstrap/js/bootstrap.min.js[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootstrap/js/bootstrap.min.js.map b/staticfiles/vendor/bootstrap/js/bootstrap.min.js.map[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/cerulean/bootstrap.min.css b/staticfiles/vendor/bootswatch/cerulean/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/cosmo/bootstrap.min.css b/staticfiles/vendor/bootswatch/cosmo/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/cyborg/bootstrap.min.css b/staticfiles/vendor/bootswatch/cyborg/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/darkly/bootstrap.min.css b/staticfiles/vendor/bootswatch/darkly/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/default/bootstrap.min.css b/staticfiles/vendor/bootswatch/default/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/flatly/bootstrap.min.css b/staticfiles/vendor/bootswatch/flatly/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/journal/bootstrap.min.css b/staticfiles/vendor/bootswatch/journal/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/litera/bootstrap.min.css b/staticfiles/vendor/bootswatch/litera/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/lumen/bootstrap.min.css b/staticfiles/vendor/bootswatch/lumen/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/lux/bootstrap.min.css b/staticfiles/vendor/bootswatch/lux/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/materia/bootstrap.min.css b/staticfiles/vendor/bootswatch/materia/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/minty/bootstrap.min.css b/staticfiles/vendor/bootswatch/minty/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/pulse/bootstrap.min.css b/staticfiles/vendor/bootswatch/pulse/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/sandstone/bootstrap.min.css b/staticfiles/vendor/bootswatch/sandstone/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/simplex/bootstrap.min.css b/staticfiles/vendor/bootswatch/simplex/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/sketchy/bootstrap.min.css b/staticfiles/vendor/bootswatch/sketchy/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/slate/bootstrap.min.css b/staticfiles/vendor/bootswatch/slate/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/solar/bootstrap.min.css b/staticfiles/vendor/bootswatch/solar/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/spacelab/bootstrap.min.css b/staticfiles/vendor/bootswatch/spacelab/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/superhero/bootstrap.min.css b/staticfiles/vendor/bootswatch/superhero/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/united/bootstrap.min.css b/staticfiles/vendor/bootswatch/united/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/bootswatch/yeti/bootstrap.min.css b/staticfiles/vendor/bootswatch/yeti/bootstrap.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/fontawesome-free/css/all.min.css b/staticfiles/vendor/fontawesome-free/css/all.min.css[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/fontawesome-free/webfonts/fa-brands-400.ttf b/staticfiles/vendor/fontawesome-free/webfonts/fa-brands-400.ttf[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/fontawesome-free/webfonts/fa-brands-400.woff2 b/staticfiles/vendor/fontawesome-free/webfonts/fa-brands-400.woff2[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/fontawesome-free/webfonts/fa-regular-400.ttf b/staticfiles/vendor/fontawesome-free/webfonts/fa-regular-400.ttf[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/fontawesome-free/webfonts/fa-regular-400.woff2 b/staticfiles/vendor/fontawesome-free/webfonts/fa-regular-400.woff2[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/fontawesome-free/webfonts/fa-solid-900.ttf b/staticfiles/vendor/fontawesome-free/webfonts/fa-solid-900.ttf[m
[1mold mode 100755[m
[1mnew mode 100644[m
[1mdiff --git a/staticfiles/vendor/fontawesome-free/webfonts/fa-solid-900.woff2 b/static