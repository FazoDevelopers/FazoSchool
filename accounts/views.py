from django.contrib.auth import get_user_model
from myconf.conf import get_model,get_type_name_field
from myconf import conf
from rest_framework.viewsets import ModelViewSet
from . import serializers
from rest_framework.response import Response
from django.db import models
from rest_framework import status
from django.db.models.signals import post_delete
from django.dispatch import receiver
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.http import FileResponse
from conf import permissions
from rest_framework.permissions import IsAuthenticated

# Create your views here.
def global_update(self, request, *args, **kwargs):
    queryset = self.filter_queryset(self.get_queryset())
    instance = self.get_object()
    data = request.data
    if data.get('user.username',False):
        queryset = queryset.filter(user__username=data['user.username'])
        if len(queryset)!=True:
            instance.user.username=data['user.username']
            instance.user.save()
    # HARDCODE
    if self.request.user.is_authenticated:
        if self.request.user.type_user and self.request.user.admin.types.title=="Tasischi":
            password=data.get('user.password',False)
            if password:
                instance.user.set_password(password)
                instance.user.save()
    if type(data.get('user.image')) not in [str,type(None)]:
        user_data = {
            'first_name': data.get('user.first_name'),
            'last_name': data.get('user.last_name'),
            'middle_name': data.get('user.middle_name'),
            'type_user': data.get('user.type_user'),
            'image': data.get('user.image'),
        }
    else:
        user_data = {
            'first_name': data.get('user.first_name'),
            'last_name': data.get('user.last_name'),
            'middle_name': data.get('user.middle_name'),
            'type_user': data.get('user.type_user'),
        }
    user_serializer = serializers.UserSerializer(instance=instance.user, data=user_data, partial=True)
    user_serializer.is_valid(raise_exception=True)
    user_serializer.update(instance.user,user_data)
    model=kwargs['model']
    types=kwargs['types']
    file_fields = get_type_name_field(model,types)
    del_key=['user.username']
    my_dict=request.data.dict()
    for key in my_dict.keys():
        if key in file_fields:
            if type(data[key])==str:
                del_key.append(key)
    for item in del_key:
        my_dict.pop(item)
    many_to_many_fields = get_type_name_field(model,models.ManyToManyField)
    for i in many_to_many_fields:
        items=dict(request.data).get(i,False)
        if items:
            items=[eval(i) for i in items]
            my_dict[i]=items
    serializer = self.get_serializer(instance, data=my_dict, partial=True)
    serializer.is_valid(raise_exception=True)
    self.perform_update(serializer)
    return serializer

class UserView(ModelViewSet):
    queryset=get_user_model().objects.all()
    serializer_class=serializers.UserSerializer
    permission_classes=[permissions.TasischiPermission]

    def get_user(self):
        from django.contrib.auth.models import AnonymousUser
        if type(self.request.user)==AnonymousUser:
            return "AnonymousUser"
        return self.request.user

    @action(detail=False, methods=['GET'],permission_classes=[permissions.TasischiOrManagerOrAdminPermission])
    def check_username_exists(self, request):
        username = request.query_params.get('username')
        if not username or len(username)<13:
            return Response({"error": "Username parameter is missing."}, status=status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(username__endswith=username[1:]).exists()
        if user_exists:
            return Response({"exists": True}, status=status.HTTP_200_OK)
        else:
            return Response({"exists": False}, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['GET'],permission_classes=[IsAuthenticated])
    def to_tasks_users(self, request):
        from school import serializers as schoolser
        instance = self.get_user()
        tasks=instance.to_tasks.all().filter(complete_to_user=True)
        context=self.get_serializer_context()
        serializer=schoolser.TaskSerializer(tasks,many=True,context=context)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'],permission_classes=[IsAuthenticated])
    def get_salaries(self, request):
        from myconf.conf import get_model
        from myconf import conf
        from finance import serializers as finser
        instance = self.get_user()
        salaries=get_model(conf.EXPENSE).objects.filter(user=instance)
        serializer=finser.ExpenseSerializer(salaries,many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'],permission_classes=[IsAuthenticated])
    def me(self, request):
        user=self.get_user()
        if user!="AnonymousUser":
            print(user.is_active)
            match user.type_user:
                case 'admin':
                    user=user.admin
                    self.serializer_class=serializers.MeAdminSerializer
                case 'teacher':
                    user=user.teacher
                    self.serializer_class=serializers.TeacherSerializer
                case 'employer':
                    user=user.employer
                    self.serializer_class=serializers.EmployerSerializer
                case 'student':
                    user=user.student
                    self.serializer_class=serializers.StudentSerializer
                case 'parent':
                    user=user.parent
                    self.serializer_class=serializers.ParentSerializer
            serializer=self.get_serializer(user,many=False)
            return Response(serializer.data)
        return Response({"user":user})

    @action(detail=False, methods=['GET'],permission_classes=[IsAuthenticated])
    def get_my_attendances(self, request):
        from school.serializers import AttendanceSerializer
        instance = self.get_user()
        attendances=get_model(conf.ATTENDANCE).objects.filter(user=instance)
        serializer=AttendanceSerializer(attendances,many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'],permission_classes=[IsAuthenticated])
    def get_user_attendances(self, request,pk=None):
        from school.serializers import AttendanceSerializer
        instance = self.get_object()
        attendances=get_model(conf.ATTENDANCE).objects.filter(user=instance)
        serializer=AttendanceSerializer(attendances,many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'],permission_classes=[permissions.TasischiOrManagerOrAdminPermission])
    def change_status(self, request,pk=None):
        status=True if request.GET.get("status") == 'true' else False
        if status and self.get_user().admin.types.slug!="tasischi":
            return Response({"error":"you has't permission"})
        user=self.get_object()
        if status==False and user.type_user=='student':
            # Bu yerda student statusi false bo'lganda log saqlaydi!!!
            get_model(conf.STUDENT_LOG).objects.create(
                student=user.student,
                author=self.get_user()
            )
        user.is_active=status
        user.save()
        return Response({"message":"success"})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success":"true"},status=status.HTTP_200_OK)

class Type_of_Admin_View(ModelViewSet):
    queryset=get_model(conf.TYPE_OF_ADMIN).objects.all()
    serializer_class=serializers.Type_of_Admin_Serializer
    permission_classes=[permissions.TasischiOrManagerPermission]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success":"true"},status=status.HTTP_200_OK)

class Permission_View(ModelViewSet):
    queryset=get_model(conf.PERMISSION).objects.all()
    serializer_class=serializers.Permission_Serializer
    permission_classes=[permissions.TasischiOrManagerPermission]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success":"true"},status=status.HTTP_200_OK)

@receiver(post_delete, sender=get_model(conf.ADMIN))
def delete_admin(sender, instance, **kwargs):
    if hasattr(instance, 'user'):
        instance.user.delete()
@receiver(post_delete, sender=get_model(conf.TEACHER))
def delete_teacher(sender, instance, **kwargs):
    if hasattr(instance, 'user'):
        instance.user.delete()
@receiver(post_delete, sender=get_model(conf.EMPLOYER))
def delete_employer(sender, instance, **kwargs):
    if hasattr(instance, 'user'):
        instance.user.delete()
@receiver(post_delete, sender=get_model(conf.STUDENT))
def delete_student(sender, instance, **kwargs):
    if hasattr(instance, 'user'):
        instance.user.delete()
@receiver(post_delete, sender=get_model(conf.PARENT))
def delete_parent(sender, instance, **kwargs):
    if hasattr(instance, 'user'):
        instance.user.delete()

class Admin_View(ModelViewSet):
    queryset=get_model(conf.ADMIN).objects.all()
    serializer_class=serializers.AdminSerializer
    permission_classes=[permissions.TasischiOrManagerPermission]

    def update(self, request, *args, **kwargs):
        serializer=global_update(self, request, *args, **kwargs,model=conf.ADMIN,types=models.FileField)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success":"true"},status=status.HTTP_200_OK)

class Teacher_View(ModelViewSet):
    queryset=get_model(conf.TEACHER).objects.all()
    serializer_class=serializers.TeacherSerializer
    permission_classes=[permissions.TasischiOrManagerOrAdminPermission]

    def get_user(self):
        from django.contrib.auth.models import AnonymousUser
        if type(self.request.user)==AnonymousUser:
            return "AnonymousUser"
        return self.request.user
    def get_teacher(self):
        from django.contrib.auth.models import AnonymousUser
        if type(self.request.user)!=AnonymousUser:
            if hasattr(self.request.user,'teacher'):
                return self.request.user.teacher
            return "ItIsNotTeacher"
        return "AnonymousUser"
    
    @action(detail=False, methods=['GET'])
    def teachers_for_class(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        teachers=[]
        for teacher in queryset:
            if hasattr(teacher,'sinf')!=True:
                serializer = self.get_serializer(teacher, many=False)
                teachers.append(serializer.data)
        return Response(teachers)
    
    @action(detail=False, methods=['POST'],permission_classes=[permissions.TeacherPermission])
    def add_lesson_with_file(self, request):
        uploaded_file = request.data.get('lesson_table_file')
        if not uploaded_file:
            return Response({"error": "No file was uploaded."}, status=status.HTTP_400_BAD_REQUEST)
        instance=self.get_teacher()
        instance.lessons_file=uploaded_file
        instance.save()
        return Response({"message": "success"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'],permission_classes=[permissions.TeacherPermission])
    def add_lesson_theme(self, request):
        instance=self.get_teacher()
        message = request.data.get('message')
        uploaded_file = request.data.get('file_message')
        if uploaded_file:
            get_model(conf.TEACHER_LESSON).objects.create(teacher=instance,message=message,file_message=uploaded_file)
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        get_model(conf.TEACHER_LESSON).objects.create(teacher=instance,message=message)
        return Response({"message": "success"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'],permission_classes=[permissions.TeacherPermission])
    def get_task_to_class(self, request):
        from school import serializers
        instance=self.get_teacher()
        tasks=get_model(conf.TASK_FOR_CLASS).objects.filter(from_teacher=instance)
        serializer=serializers.TaskForClassSerializer(data=tasks,many=True,context=self.get_serializer_context())
        return Response(serializer.data)

    @action(detail=False, methods=['POST'],permission_classes=[permissions.TeacherPermission])
    def add_task_to_class(self, request):
        from school import serializers
        instance=self.get_teacher()
        data=request.data
        data["from_teacher"]=instance.id
        context=self.get_serializer_context()
        serializer=serializers.TaskForClassSerializer(data=data,context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "success","data":serializer.data}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['PUT'],permission_classes=[permissions.TeacherPermission])
    def update_task_to_class(self, request,pk=None):
        from school import serializers
        instance=self.get_teacher()
        data=request.data
        task=get_model(conf.TASK_FOR_CLASS).objects.get(id=pk)
        data["from_teacher"]=instance.id
        context=self.get_serializer_context()
        serializer=serializers.TaskForClassSerializer(task,data=data,context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "success","data":serializer.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'],permission_classes=[permissions.TeacherPermission])
    def delete_task_to_class(self, request,pk=None):
        get_model(conf.TASK_FOR_CLASS).objects.get(id=pk).delete()
        return Response({"message": "success"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'],permission_classes=[permissions.TeacherPermission])
    def get_lesson_themes(self, request):
        from school.serializers import Teacher_LessonSerializer
        instance=self.get_teacher()
        lesson_themes=get_model(conf.TEACHER_LESSON).objects.filter(teacher=instance)
        context=self.get_serializer_context()
        serializer=Teacher_LessonSerializer(lesson_themes,many=True,context=context)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'],permission_classes=[permissions.TeacherPermission])
    def get_lesson_with_file_url(self, request):
        instance = self.get_teacher()
        file_url = request.build_absolute_uri(instance.lessons_file.url)
        return Response({"lesson_table": file_url}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'],permission_classes=[permissions.TeacherPermission])
    def get_lesson_with_file(self, request):
        instance = self.get_teacher()
        file_path = instance.lessons_file.path
        response = FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{instance.lessons_file.name}"'
        return response

    @action(detail=False, methods=['GET'],permission_classes=[permissions.TeacherPermission])
    def get_class_of_teacher(self, request):
        from school.serializers import ClassForTeacherSerializer
        instance = self.get_teacher()
        if hasattr(instance, 'sinf'):
            sinf = instance.sinf
            serializer=ClassForTeacherSerializer(sinf,many=False)
            return Response({"class":serializer.data})
        return Response({"class": None}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer=global_update(self, request, *args, **kwargs,model=conf.TEACHER,types=models.FileField)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success":"true"},status=status.HTTP_200_OK)

class Employer_View(ModelViewSet):
    queryset=get_model(conf.EMPLOYER).objects.all()
    serializer_class=serializers.EmployerSerializer
    permission_classes=[permissions.TasischiOrManagerOrAdminPermission]

    def update(self, request, *args, **kwargs):
        serializer=global_update(self, request, *args, **kwargs,model=conf.EMPLOYER,types=models.FileField)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success":"true"},status=status.HTTP_200_OK)

class Student_View(ModelViewSet):
    queryset=get_model(conf.STUDENT).objects.filter(user__is_active=True)
    serializer_class=serializers.StudentSerializer
    permission_classes=[permissions.TasischiOrManagerOrAdminPermission]

    def get_user(self):
        from django.contrib.auth.models import AnonymousUser
        if type(self.request.user)==AnonymousUser:
            return "AnonymousUser"
        return self.request.user
    
    def get_student(self):
        from django.contrib.auth.models import AnonymousUser
        if type(self.request.user)!=AnonymousUser:
            if hasattr(self.request.user,'student'):
                return self.request.user.student
            return "ItIsNotStudent"
        return "AnonymousUser"

    @action(detail=False, methods=['GET'],permission_classes=[permissions.TasischiOrManagerOrAdminPermission|permissions.ParentPermission])
    def get_students_for_parent(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        students=[]
        for student in queryset:
            if len(student.parents.all())==0:
                serializer = self.get_serializer(student, many=False)
                students.append(serializer.data)
        return Response(students)
    
    # student statistika begin

    @action(detail=False, methods=['GET'],permission_classes=[permissions.TasischiOrManagerOrAdminPermission])
    def get_all_statistics(self, request):
        from django.utils import timezone

        queryset = self.filter_queryset(self.get_queryset())
        current_date = timezone.now()
        data={}

        # added_students
        added_students=queryset.filter(user__date_joined__month=current_date.month,user__is_active=True)
        data["added_students"]={
            "added_students_count":added_students.count(),
            "added_students":self.get_serializer(added_students,many=True).data
        }

        # deleted_students
        deleted_students=queryset.filter(deleted_student__created_date__month=current_date.month)
        data["deleted_students"]={
            "deleted_students_count":deleted_students.count(),
            "deleted_students":self.get_serializer(deleted_students,many=True).data
        }

        # indebted_students
        indebted_students=queryset.filter(debts__paid=False)
        data["indebted_students"]={
            "indebted_students_count":indebted_students.count(),
            "indebted_students":self.get_serializer(indebted_students,many=True).data
        }

        discount_students=queryset.filter(discounts__created_date__year=current_date.year,discounts__created_date__month=current_date.month,discounts__is_active=True)
 
        data["discount_students"]={
            "discount_students_count":discount_students.count(),
            "discount_students":self.get_serializer(discount_students,many=True).data
        }

        return Response(data)

    # Bu oy nechta o'quvchi qo'shilgani
    @action(detail=False, methods=['GET'],permission_classes=[permissions.TasischiOrManagerOrAdminPermission])
    def get_added_students(self, request):
        from django.utils import timezone
        queryset = self.filter_queryset(self.get_queryset())
        current_date = timezone.now()
        added_students=queryset.filter(user__date_joined__month=current_date.month,user__is_active=True)

        return Response({
            "added_students_count":added_students.count(),
            "added_students":self.get_serializer(added_students,many=True).data
        })
    
    # Bu oy nechta o'quvchi o'chirilgani
    @action(detail=False, methods=['GET'],permission_classes=[permissions.TasischiOrManagerOrAdminPermission])
    def get_deleted_students(self, request):
        from django.utils import timezone
        queryset = self.filter_queryset(self.get_queryset())
        current_date = timezone.now()
        deleted_students=queryset.filter(deleted_student__created_date__month=current_date.month)
        return Response({
            "deleted_students_count":deleted_students.count(),
            "deleted_students":self.get_serializer(deleted_students,many=True).data
        })
    
    # Bu nechta o'quvchi qarzdorligi 
    @action(detail=False, methods=['GET'],permission_classes=[permissions.TasischiOrManagerOrAdminPermission])
    def get_indebted_students(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        # for instance in queryset:
        #     debts=get_model(conf.STUDENT_DEBT).objects.filter(
        #         student=instance,
        #         paid=False,
        #     )
        indebted_students=queryset.filter(debts__paid=False)

        return Response({
            "indebted_students_count":indebted_students.count(),
            "indebted_students":self.get_serializer(indebted_students,many=True).data
        })

    # Bu nechta o'quvchi qarzdorligi 
    @action(detail=False, methods=['GET'],permission_classes=[permissions.TasischiOrManagerOrAdminPermission])
    def get_discount_students(self, request):
        from django.utils import timezone
        queryset = self.filter_queryset(self.get_queryset())
        current_date = timezone.now()
        discount_students=queryset.filter(discounts__created_date__year=current_date.year,discounts__created_date__month=current_date.month,discounts__is_active=True)
 
        return Response({
            "discount_students_count":discount_students.count(),
            "discount_students":self.get_serializer(discount_students,many=True).data
        })

    # student statistika end

    @action(detail=False, methods=['POST'])
    def add_student_with_excel(self, request):
        uploaded_file = request.data.get('students_table')

        if not uploaded_file:
            return Response({"error": "No file was uploaded."}, status=status.HTTP_400_BAD_REQUEST)
        allowed_extensions = ['xls', 'xlsx']
        file_name = uploaded_file.name
        file_extension = file_name.split('.')[-1].lower()

        if not any(file_extension == ext for ext in allowed_extensions):
            return Response({"error": "Invalid file extension."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "success"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'],permission_classes=[permissions.StudentPermission])
    def student_debts(self, request):
        instance = self.get_student()
        from finance import serializers as finserializer
        from django.core.exceptions import ValidationError

        paid = request.GET.get('paid')
        filter_conditions = {}
        if paid is not None:
            filter_conditions['paid'] = str(paid).capitalize()
        try:
            debts=get_model(conf.STUDENT_DEBT).objects.filter(student=instance,**filter_conditions)
        except ValidationError:
            return Response({"error":"Noto'g'ri qiymat"})
        context=self.get_serializer_context()
        serializer=finserializer.StudentGetDebtSerializer(debts,many=True,context=context)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'],permission_classes=[permissions.StudentPermission])
    def student_pays(self, request):
        instance = self.get_student()
        from finance import serializers as finserializer
        debts=get_model(conf.INCOME).objects.filter(student=instance)
        context=self.get_serializer_context()
        serializer=finserializer.InComeGetSerializer(debts,many=True,context=context)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'],permission_classes=[permissions.StudentPermission])
    def get_student_attendances(self, request):
        from school.serializers import AttendanceSerializer
        instance = self.get_user()
        attendances=get_model(conf.ATTENDANCE).objects.filter(user=instance)
        context=self.get_serializer_context()
        serializer=AttendanceSerializer(attendances,many=True,context=context)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'],permission_classes=[permissions.StudentPermission])
    def student_grades(self, request):
        from school import serializers as schoolser
        instance = self.get_student()
        grades=instance.grades.all()
        serializer=schoolser.Grade_Serializer(grades,many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'],permission_classes=[permissions.StudentPermission])
    def student_tasks(self, request):
        from school import serializers as schoolser
        instance = self.get_student()
        tasks=instance.class_of_school.tasks.all()
        context=self.get_serializer_context()
        serializer=schoolser.TaskForClassSerializer(tasks,many=True,context=context)
        return Response(serializer.data)
    
    

    @action(detail=False, methods=['GET'],permission_classes=[permissions.StudentPermission])
    def get_lessons_of_student(self, request, pk=None):
        from school.serializers import Lesson_Serializer
        instance = self.get_student().class_of_school
        lessons=get_model(conf.LESSON).objects.filter(student_class=instance)
        serializer=Lesson_Serializer(lessons,many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        serializer=global_update(self, request, *args, **kwargs,model=conf.STUDENT,types=models.FileField)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success":"true"},status=status.HTTP_200_OK)

class StudentLog_View(ModelViewSet):
    queryset=get_model(conf.STUDENT_LOG).objects.all()
    serializer_class=serializers.StudentLog_Serializer
    permission_classes=[permissions.TasischiOrManagerOrAdminPermission]

class StudentDiscount_View(ModelViewSet):
    queryset=get_model(conf.STUDENT_DISCOUNT).objects.all()
    serializer_class=serializers.StudentDiscount_Serializer
    permission_classes=[permissions.TasischiOrManagerOrAdminPermission]

class Parent_View(ModelViewSet):
    queryset=get_model(conf.PARENT).objects.all()
    serializer_class=serializers.ParentSerializer
    permission_classes=[permissions.TasischiOrManagerOrAdminPermission]

    def update(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        instance = self.get_object()
        user=request.data['user']
        if user.get('username',False):
            queryset = queryset.filter(user__username=user['username'])
            if len(queryset)!=True:
                instance.user.username=user['username']
                instance.user.save()
        del user['username']
        user_data = {
                'first_name': user.get('first_name'),
                'last_name': user.get('last_name'),
                'middle_name': user.get('middle_name'),
                'type_user': user.get('type_user'),
            }
        user_serializer = serializers.UserSerializer(instance=instance.user, data=user_data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.update(instance.user,user_data)
        del request.data['user']
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def get_user(self):
        from django.contrib.auth.models import AnonymousUser
        if type(self.request.user)==AnonymousUser:
            return "AnonymousUser"
        return self.request.user

    def get_parent(self):
        from django.contrib.auth.models import AnonymousUser
        if type(self.request.user)!=AnonymousUser:
            if hasattr(self.request.user,'parent'):
                return self.request.user.parent
            return "ItIsNotParent"
        return "AnonymousUser"

    def get_children(self):
        parent=self.get_parent()
        if hasattr(parent,"children"):
            return parent.children.all()
        return 'ItHasNotChildren'

    @action(detail=False, methods=['GET'],permission_classes=[permissions.ParentPermission])
    def get_children_list(self, request):
        from .serializers import StudentSerializer
        children=self.get_children()
        if children!="ItHasNotChildren":
            context=self.get_serializer_context()
            serializer=StudentSerializer(children,many=True,context=context)
            return Response(serializer.data)
        return Response(children)

    @action(detail=False, methods=['GET'],permission_classes=[permissions.ParentPermission])
    def children_debts(self, request):
        children=self.get_children()
        if children!="ItHasNotChildren":
            data=[]
            for instance in children:
                from finance import serializers as finserializer
                from django.core.exceptions import ValidationError

                paid = request.GET.get('paid')
                filter_conditions = {}
                if paid is not None:
                    filter_conditions['paid'] = str(paid).capitalize()
                try:
                    debts=get_model(conf.STUDENT_DEBT).objects.filter(student=instance,**filter_conditions)
                except ValidationError:
                    return Response({"error":"Noto'g'ri qiymat"})
                context=self.get_serializer_context()
                serializer=finserializer.StudentGetDebtSerializer(debts,many=True,context=context)
                data+=serializer.data
            return Response(data)
        return Response(children)

    @action(detail=False, methods=['GET'],permission_classes=[permissions.ParentPermission])
    def children_pays(self, request):
        data=[]
        children=self.get_children()
        if children!="ItHasNotChildren":
            for instance in children:
                from finance import serializers as finserializer
                debts=get_model(conf.INCOME).objects.filter(student=instance)
                context=self.get_serializer_context()
                serializer=finserializer.InComeGetSerializer(debts,many=True,context=context)
                data+=serializer.data
        return Response(data)

    @action(detail=False, methods=['GET'],permission_classes=[permissions.ParentPermission])
    def get_children_attendances(self, request):
        from school.serializers import AttendanceSerializer
        data=[]
        children=self.get_children()
        if children!="ItHasNotChildren":
            for instance in children:
                attendances=get_model(conf.ATTENDANCE).objects.filter(user=instance.user)
                context=self.get_serializer_context()
                serializer=AttendanceSerializer(attendances,many=True,context=context)
                data.append(serializer.data)
        return Response(data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success":"true"},status=status.HTTP_200_OK)

class General_Statistics(APIView):
    permission_classes=[permissions.TasischiOrManagerOrAdminPermission]
    def get(self,request,*args,**kwargs):
        data={
            "admins":len(get_model(conf.ADMIN).objects.filter(user_is_active=True)),
            "teachers":len(get_model(conf.TEACHER).objects.filter(user_is_active=True)),
            "employers":len(get_model(conf.EMPLOYER).objects.filter(user_is_active=True)),
            "students":len(get_model(conf.STUDENT).objects.filter(user_is_active=True)),
        }
        return Response([data],status=200)
