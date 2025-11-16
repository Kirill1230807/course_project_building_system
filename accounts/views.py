from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import CustomUser, GuestRequest
from accounts.decorator import require_role
from accounts.db_queries import Queries
import random
from decimal import Decimal
from datetime import date, datetime

# REGISTER
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if CustomUser.objects.filter(username=username).exists():
            return render(request, "accounts/register.html", {"error": "Користувач вже існує"})

        user = CustomUser(username=username)
        user.set_password(password)
        user.save()

        return redirect("accounts:login")

    return render(request, "accounts/register.html")


def login_guest(request):
    request.session["user_id"] = None
    request.session["role"] = "guest"

    return redirect("home:home")


# LOGIN
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return render(request, "accounts/login.html", {"error": "Невірний логін або пароль"})

        if not user.check_password(password):
            return render(request, "accounts/login.html", {"error": "Невірний логін або пароль"})

        request.session["user_id"] = user.id
        request.session["role"] = user.role

        return redirect("home:home")

    return render(request, "accounts/login.html")


# LOGOUT
def logout_view(request):
    request.session.flush()
    return redirect("accounts:login")


# SEND ACCESS REQUEST (Guest)
def send_access_request(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("accounts:login")

    user = CustomUser.objects.get(id=user_id)

    if request.method == "POST":
        message = request.POST.get("message")
        GuestRequest.objects.create(user=user, message=message)
        return redirect("home:home")

    return render(request, "accounts/send_request.html")


# ADMIN PANEL
def manage_requests(request):
    role = request.session.get("role")

    if role != "admin":
        return redirect("no_access")

    reqs = GuestRequest.objects.filter(status="new")
    return render(request, "accounts/manage_requests.html", {"requests": reqs})


def approve_request(request, req_id):
    req = GuestRequest.objects.get(id=req_id)
    req.status = "approved"

    user = req.user
    user.role = "authorized"
    user.save()

    req.save()

    return redirect("accounts:manage_requests")


def reject_request(request, req_id):
    req = GuestRequest.objects.get(id=req_id)
    req.status = "rejected"
    req.save()
    return redirect("manage_requests")


@require_role(["admin"])
def manage_users(request):
    users = CustomUser.objects.all().order_by("id")
    return render(request, "accounts/manage_users.html", {"users": users})


@require_role(["admin"])
def change_role(request, user_id):
    user = CustomUser.objects.get(id=user_id)

    if request.method == "POST":
        new_role = request.POST.get("role")
        user.role = new_role
        user.save()
        return redirect("accounts:manage_users")

    return render(request, "accounts/change_role.html", {"user": user})


FORBIDDEN_KEYWORDS = ["drop", "truncate", "alter", "delete", "update", "insert"]

@require_role(["admin", "operator", "authorized"])
def sql_console(request):
    result = None
    query = ""
    result_text = ""

    if request.method == "POST":
        query = request.POST.get("query")

        result = Queries.execute_sql(query)

        if isinstance(result, dict) and "rows" in result:
            # Перетворюємо результат у текст для збереження
            lines = []
            for row in result["rows"]:
                line = " | ".join(str(x) for x in row)
                lines.append(line)
            result_text = "\n".join(lines)

    return render(request, "accounts/sql_console.html", {
        "query": query,
        "result": result,
        "result_text": result_text,
    })

@require_role(["authorized", "admin"])
def save_sql_result(request):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        query_text = request.POST.get("query")
        result_text = request.POST.get("result_text")

        if not result_text:
            return HttpResponse("Помилка: порожній результат.", status=400)

        Queries.save_query(user_id, query_text, result_text)

        return redirect("accounts:sql_saved_success")


@require_role(["authorized", "admin"])
def saved_queries(request):
    user_id = request.session.get("user_id")
    data = Queries.get_saved_queries(user_id)
    return render(request, "accounts/saved_queries.html", {"items": data})

@require_role(["authorized", "admin"])
def sql_saved_success(request):
    return render(request, "accounts/sql_saved_success.html")

def convert_value(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if value is None:
        return None
    return value

def forgot_password(request):
    message = None
    error = None

    if request.method == "POST":
        username = request.POST.get("username")

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            error = "Користувача з таким логіном не існує"
            return render(request, "accounts/forgot_password.html", {"error": error})

        code = str(random.randint(100000, 999999))
        user.reset_code = code
        user.save()

        request.session["reset_user_id"] = user.id

        message = f"Ваш код відновлення: {code}"

    return render(request, "accounts/forgot_password.html",
                  {"message": message, "error": error})


def reset_code(request):
    error = None

    if request.method == "POST":
        input_code = request.POST.get("code")
        user_id = request.session.get("reset_user_id")

        if not user_id:
            return redirect("forgot_password")

        user = CustomUser.objects.get(id=user_id)

        if user.reset_code != input_code:
            error = "Невірний код підтвердження"
        else:
            return redirect("accounts:reset_password")

    return render(request, "accounts/reset_code.html", {"error": error})


def reset_password(request):
    error = None

    if request.method == "POST":
        new_password = request.POST.get("password")
        user_id = request.session.get("reset_user_id")

        if not user_id:
            return redirect("forgot_password")

        user = CustomUser.objects.get(id=user_id)

        user.set_password(new_password)
        user.reset_code = None
        user.save()

        request.session.flush()

        return redirect("accounts:login")

    return render(request, "accounts/reset_password.html")