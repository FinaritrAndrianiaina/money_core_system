from django.urls import path
from manager import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.home, name="home" ),
    path('register',views.registration_view,name='register'),
    path('login',auth_views.LoginView.as_view(template_name='login.html'),name='login'),
    path('logout',views.logout_view,name='logout'),
    path('new_token',views.create_get_new_adress,name='new_token'),
    path('update',views.update_my_account,name='update'),
    path('new_transaction/<int:token_id>',views.new_transaction,name='new_transaction'),

    path('save_token/<int:token_id>',views.filedetail,name='save_token'),
    path('share_token/<int:token_id>',views.share_adress,name='share_token'),

    path('tokenlist',views.tokenlist),
    path('info',views.update_form)
]
