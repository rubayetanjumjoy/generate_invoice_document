from django.urls import path
from .views import form, generate_pdf, invoice, login_view, logout_user
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", login_view, name="login"),
    path("form/", form, name="form"),
    path("generate_pdf/", generate_pdf, name="generate_pdf"),
    path("invoice/", invoice, name="invoice"),
    path("logout/", logout_user, name="logout"),
]
