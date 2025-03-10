
from django.contrib import admin
from django.urls import path,include

from django.conf import settings
from django.conf.urls.static import static

from django.http import HttpResponseRedirect

def redirect_to_admin(request):
    return HttpResponseRedirect('/admin/')

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_admin),  # ✅ Redirect home to admin panel
    # path('get_hinglish_google/<str:hindi_word>/', views.get_hinglish_google, name='get_hinglish_google'),
    # path('get_hinglish_google', views.get_hinglish_google, name='get_hinglish_google'),

    path('ip_json', views.ip_json, name='ip_json'),
    path('ip_models', views.ip_models, name='ip_models'),
    path('pb_delete_all', views.pb_delete_all, name='pb_delete_all'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
