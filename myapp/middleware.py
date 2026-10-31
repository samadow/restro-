from django.urls import resolve, Resolver404


SKIP_PATHS = ["/api/auth/login/", "/api/auth/refresh/", "/api/login/", "/api/token/refresh/"]

ACTIONS = {
    "POST": "create",
    "PUT": "update",
    "PATCH": "update",
    "DELETE": "delete",
}


class AuditLogMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (
            request.method in ACTIONS
            and request.path.startswith("/api/")
            and request.path not in SKIP_PATHS
            and response.status_code < 400
        ):
            self.save_log(request, response)

        return response

    def save_log(self, request, response):
        from .models import AuditLog, Staff, Restaurant

        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            user = None

        try:
            match = resolve(request.path)
            view_name = match.func.__name__
            object_id = match.kwargs.get("pk")
        except Resolver404:
            view_name = ""
            object_id = None

        action = ACTIONS[request.method]
        last_part = request.path.rstrip("/").split("/")[-1]
        if request.method == "POST" and object_id and not last_part.isdigit():
            action = last_part

        if object_id is None and isinstance(getattr(response, "data", None), dict):
            object_id = response.data.get("id")

        restaurant = None
        if user:
            restaurant = Restaurant.objects.filter(owner=user).first()
            if not restaurant:
                staff = Staff.objects.filter(user=user, is_active=True).first()
                restaurant = staff.restaurant if staff else None

        AuditLog.objects.create(
            user=user,
            restaurant=restaurant,
            action=action,
            model_name=view_name,
            object_id=object_id if isinstance(object_id, int) else None,
            description=f"{request.method} {request.path} -> {response.status_code}"
        )
