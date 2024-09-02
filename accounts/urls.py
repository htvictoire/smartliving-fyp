
from django.urls import path, re_path
from . import views

 
from django.urls import path
from . import views
#pour reinitialisation du mot de passe
from django.contrib.auth import views as auth_views # as auth_views pour eviter les conflits


urlpatterns = [

    path('depannaeeeeeeeyyyy/' , views.depannage , name='depannage'), 

    path('register/' , views.register , name='register'), 

    path('' , views.sign_in , name='login'),

    path("dashboard/", views.dashboard, name="dashboard") ,



    path('staff-signup/', views.create_user_staff, name='staff_signup'),
    path('deconnexion/' , views.logout_etudiants , name='deconnexion'),
    path('logout/' , views.logout_staff , name='logout'),


    path('activation/<uidb64>/<token>/' ,views.activate_account, name='activate'),
    path('resend_activation_email/<int:user_id>/', views.resend_activation_email, name='resend_activation_email'),



    #pour reinitialisation du mot de passe

    path('reset-password/' ,views.CustomPasswordResetView.as_view(), name='password_reset'),

    #path('reinitialisation-du-motdepasse-envoyee/' ,auth_views.PasswordResetDoneView.as_view(template_name="accounts/passwordresetdone.html"), name='password_reset_sent'), #no need, we have pop up

    path('reinitialisation-du-motdepasse/<uidb64>/<token>/' ,views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    #path('reinitialisation-du-motdepasse-fait/' ,auth_views.PasswordResetCompleteView.as_view(template_name = "accounts/passwordresetcomplete.html"), name='password_reset_complete'), #no need, we have pop up

    ]
