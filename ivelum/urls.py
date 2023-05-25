from django.urls import re_path

from ivelum.views import proxy_view

urlpatterns = [
    re_path(r'^.*$', proxy_view, name='proxy'),
]
