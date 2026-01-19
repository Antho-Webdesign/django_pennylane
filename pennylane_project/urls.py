from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('listing_app.urls', namespace='listing_app')),     # page de recherche à la racine
    path('create/', include('creation_app.urls', namespace='creation_app')),  # pages de création
]
