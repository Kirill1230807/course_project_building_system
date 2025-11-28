from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("login-guest/", views.login_guest, name="login_guest"),
    path("logout/", views.logout_view, name="logout"),
    path("sql-console/", views.sql_console, name="sql_console"),
    path("save-sql-result/", views.save_sql_result, name="save_sql_result"),
    path("saved-queries/", views.saved_queries, name="saved_queries"),
    path("sql-saved/", views.sql_saved_success, name="sql_saved_success"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset-code/", views.reset_code, name="reset_code"),
    path("reset-password/", views.reset_password, name="reset_password"),
    path("send-request/", views.send_access_request, name="send_access"),
    path("manage-requests/", views.manage_requests, name="manage_requests"),
    path("approve/<int:req_id>/", views.approve_request, name="approve_request"),
    path("reject/<int:req_id>/", views.reject_request, name="reject_request"),
    path("users/", views.manage_users, name="manage_users"),
    path("users/<int:user_id>/change-role/", views.change_role, name="change_role"),

]