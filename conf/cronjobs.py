# os,json import
import os,json
# django import
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings
# datetime import
from datetime import datetime
# rest_framework import
from rest_framework.decorators import authentication_classes, permission_classes,api_view
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# local functions import
from .utils.sms import create_debts_sms
from myconf.conf import get_model
from myconf import conf

# bu yerda chegirmalarni tekshirish
def check_discount(study_price,student,price):
    # Shunga o'xshash debt yo'qligini tekshiryapti
    debt=get_model(conf.STUDENT_DEBT).objects.filter(
        student=student,
        created_date__month=datetime.now().month,
        created_date__year=datetime.now().year
    )
    # TODO
    if student.discount:
        discount=student.discount.price#student.discount.price
        discount_price=(study_price/100)-discount#shu yerda discount_price=study_price-discount
        price=price-discount_price

    if len(debt)==0:
        debt=get_model(conf.STUDENT_DEBT).objects.create(
            student=student,
            price=price,
            balance=-price
        )
        if student.discount:
            student.discount_type=student.discount_type if student.discount_month else None
            student.discount=student.discount if student.discount_month else 0
            student.discount_month=student.discount_month-1 if student.discount_month else 0
            student.save()
        return {"message":"success"}
    return {"message":"nosuccess"}

# davomat cron
@api_view(['GET'])
def davomat_users(request):
    current_date = datetime.now().isoweekday()
    if current_date!=7:
        users=get_user_model().objects.filter(~Q(type_user="parent"),Q(is_active=True))
        for user in users:
            get_model(conf.ATTENDANCE).objects.create(user=user)
    return Response({"message": "succesfully"})

# qarzdorlik cron
@api_view(['GET'])
def student_debts(request):
    current_date = datetime.now().date()
    companies=get_model(conf.COMPANY).objects.filter(active=True)
    company=companies[0] if companies else None
    begin_date=company.begin_date
    end_date=company.end_date
    if current_date>=begin_date and current_date<=end_date:
        students=get_model(conf.STUDENT).objects.filter(user__is_active=True)
        study_price=company.study_price
        hostel_price=company.hostel_price
        for student in students:
            # condition?true:false
            # true if condition else false
            price=study_price+hostel_price if student.hostel else study_price
            check_discount(study_price=study_price,student=student,price=price)#TODO
            # Qarzdorlik bo'lsa shu bo'yicha sms xabarnomi jo'natish
            debts=get_model(conf.STUDENT_DEBT).objects.filter(
                student=student,
                paid=False,
            )
            parents=student.parents.all()
            if len(parents)>=1:
                parent=parents[0]
                create_debts_sms(parent=parent,child=student,type_message="OYLIK_TULOV",debts=debts)
    return Response({"message": "succesfully"})

# set assets
@api_view(['GET'])
@authentication_classes([SessionAuthentication])  # Use SessionAuthentication for authentication
@permission_classes([IsAuthenticated])  # Require users to be authenticated
def set_assets(request):
    json_path=os.path.join(settings.STATICFILES_DIRS[0],'data.json')
    with open(json_path, 'r') as file:
        # Load the JSON data from the file
        json_data = json.load(file)
    types_admin=json_data['types-admin']
    for type_admin in types_admin:
        get_model(conf.TYPE_OF_ADMIN).objects.get_or_create(title=type_admin['title'])
    
    permissions_admin_admin=json_data['permissions-admin']
    for permission_admin in permissions_admin_admin:
        get_model(conf.PERMISSION).objects.get_or_create(title=permission_admin['title'],path=permission_admin['path'])

    classes=json_data['classes']
    for class_of_school in classes:
        get_model(conf.CLASS).objects.get_or_create(title=class_of_school['title'])

    companies=json_data['companies']
    for company in companies:
        get_model(conf.COMPANY).objects.get_or_create(
            begin_date=company['begin_date'],
            end_date=company['end_date'],
            study_price=company['study_price'],
            hostel_price=company['hostel_price'],
            camera_entrance=company['camera_entrance'],
            camera_exit=company['camera_exit']
        )

    return Response({"message": "succesfully"})
