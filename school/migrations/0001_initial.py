# Generated by Django 4.2.4 on 2023-11-20 05:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Sinflar',
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.FileField(blank=True, null=True, upload_to='uploads/company_logo/%Y_%m_%d')),
                ('begin_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('study_price', models.IntegerField(default=0)),
                ('hostel_price', models.IntegerField(default=0)),
                ('camera_entrance', models.CharField(blank=True, max_length=500, null=True)),
                ('camera_exit', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Lesson_Time',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('begin_time', models.TimeField()),
                ('end_time', models.TimeField()),
            ],
            options={
                'verbose_name_plural': 'Dars soatlari',
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Xonalar',
            },
        ),
        migrations.CreateModel(
            name='Science',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Fanlar',
            },
        ),
        migrations.CreateModel(
            name='Teacher_Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('file_message', models.FileField(blank=True, null=True, upload_to='uploads/message/%Y_%m_%d')),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_lessons', to='accounts.teacher')),
            ],
        ),
        migrations.CreateModel(
            name='TaskForClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_title', models.CharField(max_length=255)),
                ('task_message', models.TextField()),
                ('complete_to_user', models.BooleanField(default=False)),
                ('complete_from_user', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('change_date', models.DateTimeField(auto_now=True)),
                ('begin_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('from_teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasksforclass', to='accounts.teacher')),
                ('to_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='school.class')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_title', models.CharField(max_length=255)),
                ('task_message', models.TextField()),
                ('complete_to_user', models.BooleanField(default=False)),
                ('complete_from_user', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('change_date', models.DateTimeField(auto_now=True)),
                ('begin_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_tasks', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_tasks', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('option1', models.CharField(max_length=255)),
                ('option2', models.CharField(max_length=255)),
                ('option3', models.CharField(max_length=255)),
                ('option4', models.CharField(max_length=255)),
                ('answer', models.CharField(max_length=255)),
                ('science', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='school.science')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='accounts.teacher')),
            ],
        ),
        migrations.CreateModel(
            name='Parent_Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('change_date', models.DateTimeField(auto_now=True)),
                ('admin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='admin_answers', to='accounts.admin')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parent_comments', to='accounts.parent')),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teacher', models.TextField(blank=True, null=True)),
                ('lesson_date', models.CharField(choices=[('MONDAY', 'Dushanba'), ('TUESDAY', 'Seshanba'), ('WEDNESDAY', 'Chorshanba'), ('THURSDAY', 'Payshanba'), ('FRIDAY', 'Juma'), ('SATURDAY', 'Shanba')], default='Dushanba', max_length=10)),
                ('lesson_time', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='school.lesson_time')),
                ('room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='school.room')),
                ('science', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='school.science')),
                ('student_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='school.class')),
            ],
            options={
                'verbose_name_plural': 'Darslar',
                'ordering': ['lesson_time'],
            },
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.IntegerField(choices=[(1, 'Bir'), (2, 'Ikki'), (3, 'Uch'), (4, "To'rt"), (5, 'Besh')], default=1)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='school.lesson')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='accounts.student')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='accounts.teacher')),
            ],
            options={
                'verbose_name_plural': 'Baholar',
            },
        ),
        migrations.AddField(
            model_name='class',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sinflar', to='school.room'),
        ),
        migrations.AddField(
            model_name='class',
            name='teacher',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sinf', to='accounts.teacher'),
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attendance_type', models.CharField(choices=[('SABABLI', 'Sababli'), ('SABABSIZ', 'Sababsiz'), ('KELGAN', 'kelgan')], default='SABABSIZ', max_length=50, verbose_name='davomat turi:')),
                ('date', models.DateField(auto_now_add=True)),
                ('date_enter', models.DateTimeField(blank=True, null=True)),
                ('date_leave', models.DateTimeField(blank=True, null=True)),
                ('reason', models.TextField(blank=True, null=True, verbose_name="sabab(Agar sababli turida bo'lsa):")),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='davomatlar', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Davomatlar',
            },
        ),
    ]
