from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/v1/create/", views.create_new_event),
    path("api/v1/update/<int:event_id>/", views.update_event),
    path("api/v1/get/<int:event_id>/", views.get_event),
]