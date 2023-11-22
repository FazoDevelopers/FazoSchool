from myconf.conf import get_model
from myconf import conf
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.status import HTTP_401_UNAUTHORIZED,HTTP_200_OK


def create_sms(parent,child,type_message):
    get_model(conf.MESSAGE).objects.create(parent=parent,child=child,type_message=type_message)

def create_debts_sms(parent,child,type_message,debts):
    message=get_model(conf.MESSAGE).objects.create(parent=parent,child=child,type_message=type_message)
    message.debts.set([debt.id for  debt in debts])
    
def get_kirish_content(self):
    parent=self.parent
    child=self.child
    created_date=self.created_date
    message=f"""
    {child.first_name}.{child.last_name}
    Maktabga {created_date} kirdi!
    """
    message+=f"Ushbu xabar jo'nash vaqti:{self.formatted_created_date}"
    return message

def get_chiqish_content(self):
    parent=self.parent
    child=self.child
    created_date=self.created_date
    message=f"""
    {child.first_name}.{child.last_name}
    Maktabdan {created_date} chiqdi!
    """
    message+=f"Ushbu xabar jo'nash vaqti:{self.formatted_created_date}"
    return message

def get_debts_content(self):
    parent=self.parent
    child=self.child
    debts=self.debts
    created_date=self.created_date
    message="{child.first_name}.{child.last_name}"
    for debt in debts:
        message+=f"""
            {debt.created_date} oy uchun {debt.balance} so'm qarzdor!
        """
    message+=f"Ushbu xabar jo'nash vaqti:{self.formatted_created_date}"
    return message

class MessageView(APIView):
    permission_classes=[AllowAny]
    def get(self,request):
        username=request.GET.get("username",None)
        password=request.GET.get("password",None)
        data={}
        status=HTTP_401_UNAUTHORIZED
        if username=="+998900500902" and password=="Ss20010806":
            status=HTTP_200_OK
            message=get_model(conf.MESSAGE).objects.last()
            if message:
                data={
                    "phone":message.parent.username,
                    "message":message.content
                }
                status=HTTP_200_OK
        return Response(data,status=status)

    def delete(self,request):
        username=request.GET.get("username",None)
        password=request.GET.get("password",None)
        data={}
        status=HTTP_401_UNAUTHORIZED
        if username=="+998900500902" and password=="Ss20010806":
            get_model(conf.MESSAGE).objects.last().delete() if get_model(conf.MESSAGE).objects.last() else None
            data={"message":"success"}
            status=HTTP_200_OK
        return Response(data,status)


#TODO sms