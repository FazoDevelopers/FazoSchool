from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .face_rec_gpu import FaceRecognition
# from .face_rec import FaceRecognition
from rest_framework.decorators import api_view


users=get_user_model().objects.filter(is_active=True)
users_list=[]
for user in users:
    if user.image:
        user_dict={
            "id":user.id,
            "username":user.get_username(),
            "path":user.image.path
        }
        users_list.append(user_dict)
cam1=FaceRecognition(users=users_list,similarity=0.5,limit=5)

@api_view(['GET'])
def cam(request,pk):
    result=cam1.start(position=pk)
    number=0
    print(result)
    if result:
        number=1
    return JsonResponse({"message":number},safe=True)


