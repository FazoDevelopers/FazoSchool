# Generated by Django 4.2.4 on 2023-11-20 05:08

import accounts.models
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('image', models.FileField(blank=True, null=True, upload_to=accounts.models.UserProfile.user_avatar_path, verbose_name='Avatar uchun surat:')),
                ('middle_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Otasini ismi:')),
                ('type_user', models.CharField(blank=True, max_length=255, null=True, verbose_name='User turi:')),
                ('unique_number', models.PositiveIntegerField(unique=True)),
            ],
            options={
                'verbose_name_plural': 'Foydalanuvchilar',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('salary', models.IntegerField(default=0, verbose_name='Oylik maosh:')),
            ],
            options={
                'verbose_name_plural': 'Adminlar',
            },
        ),
        migrations.CreateModel(
            name='Employer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('salary', models.IntegerField(default=0, verbose_name='Oylik maosh:')),
                ('position', models.CharField(max_length=255, verbose_name='Lavozim:')),
            ],
            options={
                'verbose_name_plural': 'Xodimlar',
            },
        ),
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': 'Ota ona',
            },
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='nomi:')),
                ('path', models.CharField(blank=True, max_length=255, null=True)),
                ('slug', models.SlugField(blank=True, editable=False, null=True)),
            ],
            options={
                'verbose_name_plural': 'Adminlarga ruxsatnomalar',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_card', models.CharField(max_length=50)),
                ('date_of_admission', models.DateField(blank=True, null=True)),
                ('id_card_parents', models.FileField(blank=True, null=True, upload_to=accounts.models.Student.student_id_card_parents_path, verbose_name='Ota-ona pasporti nusxasi:')),
                ('picture_3x4', models.FileField(blank=True, null=True, upload_to=accounts.models.Student.student_picture_3x4_path, verbose_name='3x4 rasm:')),
                ('school_tab', models.FileField(blank=True, null=True, upload_to=accounts.models.Student.student_school_tab_path, verbose_name='Maktabdan Tabel asli 2-11-sinflar uchun:')),
                ('medical_book', models.FileField(blank=True, null=True, upload_to=accounts.models.Student.student_medical_book_path, verbose_name='Tibbiy Daftarcha (086):')),
                ('hostel', models.BooleanField(default=False)),
                ('discount', models.IntegerField(default=0)),
                ('discount_month', models.IntegerField(default=0)),
                ('discount_type', models.CharField(blank=True, choices=[('GRANT_FULL', 'GRANT_FULL'), ('GRANT_MONTH', 'GRANT_MONTH'), ('EMPLOYER_CHILDREN', 'EMPLOYER_CHILDREN'), ('FAMILY_CHILDREN', 'FAMILY_CHILDREN')], max_length=20, null=True)),
            ],
            options={
                'verbose_name_plural': "O'quvchilar",
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_card', models.CharField(blank=True, max_length=50, null=True, verbose_name='Pasport seriya raqami:')),
                ('date_of_employment', models.DateField(blank=True, null=True, verbose_name='Ishga kirgan sanasi:')),
                ('gender', models.CharField(choices=[('MALE', 'Erkak'), ('FEMALE', 'Ayol')], max_length=255, verbose_name='Jinsi:')),
                ('address', models.CharField(blank=True, max_length=400, null=True, verbose_name='Manzili:')),
                ('experience', models.CharField(blank=True, choices=[('HIGH_CATEGORY', 'Oliy toifa'), ('FIRST_CATEGORY', '1-toifa'), ('SECOND_CATEGORY', '2-toifa')], max_length=255, null=True, verbose_name='Tajriba:')),
                ('language_certificate', models.CharField(blank=True, choices=[('TESOL', 'Tesol'), ('CELTA', 'Celta'), ('IELTS6', 'IELTS 6+'), ('CEFRB2', 'CEFR B2+')], max_length=255, null=True, verbose_name='Til sertifikati:')),
                ('language_certificate_file', models.FileField(blank=True, null=True, upload_to=accounts.models.Teacher.teacher_language_certificate_path, verbose_name='Til sertifikati fayl shakli:')),
                ('lens', models.FileField(blank=True, null=True, upload_to=accounts.models.Teacher.teacher_lens_path, verbose_name='Obyektivka:')),
                ('id_card_photo', models.FileField(blank=True, null=True, upload_to=accounts.models.Teacher.teacher_id_card_photo_path, verbose_name='Pasport nusxasi:')),
                ('survey', models.FileField(blank=True, null=True, upload_to=accounts.models.Teacher.teacher_survey_path, verbose_name="So'rovnoma:")),
                ('biography', models.FileField(blank=True, null=True, upload_to=accounts.models.Teacher.teacher_biography_path, verbose_name='Tarjimai xol:')),
                ('medical_book', models.FileField(blank=True, null=True, upload_to=accounts.models.Teacher.teacher_medical_book_path, verbose_name='Tibbiy Daftarcha (086):')),
                ('picture_3x4', models.FileField(blank=True, null=True, upload_to=accounts.models.Teacher.teacher_picture_3x4_path, verbose_name='3x4 rasm:')),
                ('completed_salary', models.BooleanField(default=False)),
                ('lessons_file', models.FileField(blank=True, null=True, upload_to=accounts.models.Teacher.lessons_file_path, verbose_name='dars jadvali:')),
            ],
            options={
                'verbose_name_plural': "O'qituvchilar",
            },
        ),
        migrations.CreateModel(
            name='Type_of_Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='nomi:')),
                ('slug', models.SlugField(blank=True, editable=False, null=True)),
            ],
            options={
                'verbose_name_plural': 'Adminlar toifasi',
            },
        ),
    ]
