# my config import
from accounts import serializers as acserializers
from myconf.conf import get_model
from myconf import conf
from school.filters import AttendanceFilter
from school.table_with_xlsx import AddLessonWithExcel
from . import serializers
# rest framework import
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
# datetime import
import datetime
# django import
from django.db.models import Count
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.conf import settings
# permissions
from conf import permissions

class ScienceView(ModelViewSet):
    queryset=get_model(conf.SCIENCE).objects.all()
    serializer_class=serializers.ScienceSerializer
    permission_classes=[permissions.TasischiOrManagerOrAdminPermission]
    lookup_field = 'pk'

    @action(detail=True, methods=['GET'])
    def get_teachers_of_sciences(self, request, pk=None):
        from accounts.serializers import TeacherSerializer
        instance = self.get_object()
        teachers=get_model(conf.TEACHER).objects.filter(sciences=instance)
        serializer=TeacherSerializer(teachers,many=True)
        return Response(serializer.data)

class ClassView(ModelViewSet):#get information class
    queryset=get_model(conf.CLASS).objects.all()
    serializer_class=serializers.ClassSerializer
    permission_classes=[permissions.TasischiOrManagerOrAdminPermission|permissions.TeacherPermission]
    lookup_field = 'pk'
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

    def get_student(self):
        from django.contrib.auth.models import AnonymousUser
        if type(self.request.user)!=AnonymousUser:
            if hasattr(self.request.user,'student'):
                return self.request.user.student
            return "ItIsNotTeacher"
        return "AnonymousUser"

    @action(detail=False, methods=['GET'],permission_classes=[permissions.TasischiOrManagerOrAdminPermission|permissions.TeacherPermission])
    def get_students_of_classes(self, request):
        from accounts.serializers import StudentSerializer
        queryset = self.filter_queryset(self.get_queryset())
        data=[]
        for instance in queryset:
            students=get_model(conf.STUDENT).objects.filter(class_of_school=instance)
            stdserializer=StudentSerializer(students,many=True)
            serializer=self.get_serializer(instance,many=False)
            class_data=serializer.data
            class_data["students"]=stdserializer.data
            data.append(class_data)
        return Response(data)

    @action(detail=False, methods=['GET'],permission_classes=[permissions.TeacherPermission])
    def get_students_of_class(self, request):
        from accounts.serializers import StudentSerializer
        instance = self.get_teacher().sinf
        students=get_model(conf.STUDENT).objects.filter(class_of_school=instance)
        serializer=StudentSerializer(students,many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'],permission_classes=[permissions.TasischiOrManagerOrAdminPermission|permissions.TeacherPermission])
    def get_informations_of_class_pk(self, request, pk=None):
        from accounts.serializers import StudentSerializer
        instance = self.get_object()
        students=get_model(conf.STUDENT).objects.filter(class_of_school=instance)
        std_serializer=StudentSerializer(students,many=True)
        teacher=instance.teacher

        teacher_image_url = None
        if teacher:
            if teacher.user.image:
                teacher_image_url = request.build_absolute_uri(settings.MEDIA_URL + str(teacher.user.image))
            teacher={
                "username":teacher.user.username,
                "first_name":teacher.user.first_name,
                "last_name":teacher.user.last_name,
                "image":teacher_image_url
            }

        data={
            "title":instance.title,
            "teacher":teacher,
            "room":instance.room.title if instance.room else instance.room,
            "students":std_serializer.data
        }

        return Response(data)

    @action(detail=True, methods=['GET'],permission_classes=[permissions.TasischiOrManagerOrAdminPermission|permissions.TeacherPermission])
    def get_students_of_class_pk(self, request, pk=None):
        from accounts.serializers import StudentSerializer
        instance = self.get_object()
        students=get_model(conf.STUDENT).objects.filter(class_of_school=instance)
        serializer=StudentSerializer(students,many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'],permission_classes=[permissions.TeacherPermission])
    def get_lessons_of_class(self, request, pk=None):
        from .serializers import Lesson_Serializer
        instance = self.get_teacher().sinf
        lessons=get_model(conf.LESSON).objects.filter(student_class=instance)
        serializer=Lesson_Serializer(lessons,many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'],permission_classes=[permissions.TasischiOrManagerOrAdminPermission|permissions.TeacherPermission])
    def get_lessons_of_class_pk(self, request, pk=None):
        from .serializers import Lesson_Serializer
        instance = self.get_object()
        lessons=get_model(conf.LESSON).objects.filter(student_class=instance)
        serializer=Lesson_Serializer(lessons,many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'],permission_classes=[permissions.TasischiOrManagerOrAdminPermission|permissions.TeacherPermission])
    def get_attendances_of_class(self, request, pk=None):
        from .serializers import AttendanceSerializer
        instance = self.get_teacher().sinf
        students=get_model(conf.STUDENT).objects.filter(class_of_school=instance)
        attendances_arr=[]
        for student in students:
            attendances=get_model(conf.ATTENDANCE).objects.filter(user=student.user)
            attendances_serializer=AttendanceSerializer(attendances,many=True)
            student_dict={
                "id":student.id,
                "username":student.user.username,
                "first_name":student.user.first_name,
                "last_name":student.user.last_name,
                "attendances":[]
            }
            student_dict['attendances']=attendances_serializer.data
            attendances_arr.append(student_dict)
        return Response(attendances_arr)#TODO

    @action(detail=True, methods=['GET'],permission_classes=[permissions.TasischiOrManagerOrAdminPermission|permissions.TeacherPermission])
    def get_attendances_of_class_pk(self, request, pk=None):
        from .serializers import AttendanceSerializer
        instance = self.get_object()
        students=get_model(conf.STUDENT).objects.filter(class_of_school=instance)
        attendances_arr=[]
        for student in students:
            attendances=get_model(conf.ATTENDANCE).objects.filter(user=student.user)
            attendances_serializer=AttendanceSerializer(attendances,many=True)
            attendances_arr+=attendances_serializer.data
        return Response(attendances_arr)

from django.utils import timezone
from dateutil.relativedelta import relativedelta

class AttendanceView(ModelViewSet):
    queryset=get_model(conf.ATTENDANCE).objects.all()
    serializer_class=serializers.AttendanceSerializer
    permission_classes=[permissions.TasischiOrManagerOrAdminPermission]
    filterset_class = AttendanceFilter

    def get_queryset(self):
        date_type = self.request.query_params.get('date_type')
        today = timezone.now().date()

        if date_type == 'daily':
            return get_model(conf.ATTENDANCE).objects.filter(date=today)
        elif date_type == 'weekly':
            # Assuming you want to filter by the current week (Monday to Sunday)
            start_of_week = today - datetime.timedelta(days=today.weekday())
            end_of_week = start_of_week + datetime.timedelta(days=6)
            return get_model(conf.ATTENDANCE).objects.filter(date__range=(start_of_week, end_of_week))
        elif date_type == 'monthly':
            start_of_month = today.replace(day=1)
            end_of_month = (start_of_month + relativedelta(months=1)) - datetime.timedelta(days=1)
            return get_model(conf.ATTENDANCE).objects.filter(date__range=(start_of_month, end_of_month))
        else:
            return get_model(conf.ATTENDANCE).objects.all()


class RoomView(ModelViewSet):
    queryset=get_model(conf.ROOM).objects.all()
    serializer_class=serializers.RoomSerializer
    permission_classes=[permissions.TasischiOrManagerOrAdminPermission]

    @action(detail=False, methods=['GET'])
    def rooms_for_class(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        rooms_with_classes = queryset.annotate(num_classes=Count('sinflar'))
        rooms=[]
        for room in rooms_with_classes:
            if room.num_classes == 0:
                serializer = self.get_serializer(room, many=False)
                rooms.append(serializer.data)
        return Response(rooms)

class Lesson_TimeView(ModelViewSet):
    queryset=get_model(conf.LESSON_TIME).objects.all()
    serializer_class=serializers.Lesson_Time_Serializer

class LessonView(ModelViewSet):
    queryset=get_model(conf.LESSON).objects.all()
    serializer_class=serializers.Lesson_Serializer
    permission_classes=[permissions.TasischiOrManagerOrAdminPermission]

    @action(detail=False, methods=['POST'])
    def add_lesson_with_excel(self, request):
        uploaded_file = request.data.get('lessons_table')
        if not uploaded_file:
            return Response({"error": "No file was uploaded."}, status=status.HTTP_400_BAD_REQUEST)
        allowed_extensions = ['xls', 'xlsx']
        file_name = uploaded_file.name
        file_extension = file_name.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            return Response({"error": "Invalid file extension."}, status=status.HTTP_400_BAD_REQUEST)
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(filename)
        try:
            with transaction.atomic():
                get_model(conf.LESSON).objects.all().delete()
                obj = AddLessonWithExcel(file_path)
                obj.start()
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if fs.exists(filename):
                fs.delete(filename)
        return Response({"message": "success"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def get_lessons_of_class(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        data=[]
        from .serializers import Lesson_Serializer
        classes = get_model(conf.CLASS).objects.all()
        for instance in classes:
            lessons=queryset.filter(student_class=instance)
            serializer=Lesson_Serializer(lessons,many=True)
            obj={
                "class_id":instance.id,
                "class_title":instance.title,
                "lessons":serializer.data
            }
            data.append(obj)
        return Response(data)

class GradeView(ModelViewSet):
    queryset=get_model(conf.GRADE).objects.all()
    serializer_class=serializers.Grade_Serializer

class TaskView(ModelViewSet):
    queryset=get_model(conf.TASK).objects.all()
    serializer_class=serializers.TaskSerializer
    permission_classes=[permissions.TasischiOrManagerOrAdminPermission]
    filterset_fields="__all__"

class TaskForClassView(ModelViewSet):
    queryset=get_model(conf.TASK_FOR_CLASS).objects.all()
    serializer_class=serializers.TaskForClassSerializer
    permission_classes=[permissions.TeacherPermission]
    filterset_fields="__all__"

class Parent_CommentView(ModelViewSet):
    queryset=get_model(conf.PARENT_COMMENT).objects.all()
    serializer_class=serializers.Parent_CommentSerializer
    permission_classes=[permissions.TasischiOrManagerOrAdminPermission|permissions.ParentPermission]
    filterset_fields="__all__"

    @action(detail=False,methods=['GET'],permission_classes=[permissions.TasischiOrManagerOrAdminPermission|permissions.ParentPermission])
    def list_comments(self,request):
        user=self.request.user
        if user.is_authenticated:
            if user.type_user=="parent":
                queryset = self.filter_queryset(self.get_queryset()).filter(parent=user.id)
                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)
        return Response({"error":"auth"})

    @action(detail=False,methods=['POST'],permission_classes=[permissions.TasischiOrManagerOrAdminPermission|permissions.ParentPermission])
    def add_comment(self,request):
        user=self.request.user
        data=dict(request.data)
        if user.is_authenticated:
            if user.type_user=="admin":
                data['admin']=user.id
                serializer=self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                headers = self.get_success_headers(serializer.data)
                queryset = self.filter_queryset(self.get_queryset()).filter(parent=data['parent'])
                serializer = self.get_serializer(queryset, many=True)
            elif user.type_user=="parent":
                data['parent']=user.id
                serializer=self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                headers = self.get_success_headers(serializer.data)
                queryset = self.filter_queryset(self.get_queryset()).filter(parent=user.id)
                serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({"error":"auth"})

    @action(detail=False, methods=['GET'],permission_classes=[permissions.TasischiOrManagerOrAdminPermission|permissions.ParentPermission])
    def get_with_parent(self, request):
        parents=get_model(conf.PARENT).objects.all()
        data=[]
        context=self.get_serializer_context()
        for parent in parents:
            if parent.parent_comments.exists():
                pser=acserializers.ParentSerializer(parent,many=False,context=context)
                msgser=serializers.Parent_CommentSerializer(parent.parent_comments,many=True,context=context)
                data.append({
                    "parent":pser.data,
                    "messages":msgser.data,
                    "chat":True
                })
            else:
                pser=acserializers.ParentSerializer(parent,many=False,context=context)
                data.append({
                    "parent":pser.data,
                    "messages":[],
                    "chat":False
                })
        return Response(data)

class Teacher_LessonView(ModelViewSet):
    queryset=get_model(conf.TEACHER_LESSON).objects.all()
    serializer_class=serializers.Teacher_LessonSerializer
    permission_classes=[permissions.TasischiOrManagerOrAdminPermission|permissions.TeacherPermission]

class QuestionsView(ModelViewSet):
    queryset=get_model(conf.QUESTION).objects.all()
    serializer_class=serializers.QuestionSerializer
    permission_classes=[permissions.TasischiOrManagerOrAdminPermission|permissions.TeacherPermission|permissions.StudentPermission]

    @action(methods=["POST"],detail=True)
    def check_answer(self,request,pk=None):
        answer=request.data.get("answer")
        instance=self.get_object().answer
        return Response({"answer":"correct" if answer==instance else "nocorrect"})



class CompanyView(ModelViewSet):
    queryset=get_model(conf.COMPANY).objects.all()
    serializer_class=serializers.CompanySerializer
    permission_classes=[permissions.TasischiOrManagerOrAdminPermission]