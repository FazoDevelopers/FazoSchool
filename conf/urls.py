from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

# from .faceid import camera

from . import cronjobs
from .utils.sms import MessageView

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
)

urlpatterns = [
   path('admin/', admin.site.urls),
   path('api/v1/', include('accounts.urls')),

   # SMS CRON JOBS
   path("api/v1/sms/",MessageView.as_view()),

   # CRON JOBS   
   path('api/v1/cron/davomat_user/',cronjobs.davomat_users),
   path('api/v1/cron/student_debts/',cronjobs.student_debts),
   path('api/v1/cron/set_assets/',cronjobs.set_assets),

   #   path('api/v1/cam/<int:pk>/',camera.cam),

   # DOCS
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
