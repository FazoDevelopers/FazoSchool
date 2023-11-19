# views.py
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from .face_rec_gpu import FaceRecognition

users = get_user_model().objects.filter(is_active=True)
users_list = [
    {
        "id": user.id,
        "username": user.get_username(),
        "path": user.image.path
    } for user in users if user.image
]

cam1 = FaceRecognition(users=users_list, similarity=0.5, limit=5)


@api_view(['GET'])
def cam(request, pk):
    result = cam1.start(position=pk, video_source="http://192.168.1.119:4747/video")
    number = 0
    print(result)
    if result:
        number = 1
    return JsonResponse({"message": number}, safe=True)
