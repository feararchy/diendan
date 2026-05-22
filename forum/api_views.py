import json
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Category, Topic, Comment


def api_health(request):
    return JsonResponse({
        "status": "ok",
        "message": "Kingmate Tech Forum API is running"
    })


def category_to_dict(category):
    try:
        topics_count = Topic.objects.filter(category=category).count()
    except Exception:
        topics_count = 0

    return {
        "id": category.id,
        "name": getattr(category, "name", ""),
        "description": getattr(category, "description", ""),
        "topics_count": topics_count
    }


def topic_to_dict(topic, request=None):
    image_url = ""

    if hasattr(topic, "image") and topic.image:
        try:
            image_url = topic.image.url
            if request:
                image_url = request.build_absolute_uri(image_url)
        except Exception:
            image_url = ""

    try:
        comments_count = Comment.objects.filter(topic=topic).count()
    except Exception:
        comments_count = 0

    likes_count = 0
    if hasattr(topic, "likes"):
        try:
            likes_count = topic.likes.count()
        except Exception:
            likes_count = 0

    return {
        "id": topic.id,
        "title": getattr(topic, "title", ""),
        "content": getattr(topic, "content", ""),
        "author": topic.author.username if getattr(topic, "author", None) else "",
        "category": topic.category.name if getattr(topic, "category", None) else "",
        "image": image_url,
        "comments_count": comments_count,
        "likes_count": likes_count,
        "created_at": topic.created_at.strftime("%Y-%m-%d %H:%M:%S") if getattr(topic, "created_at", None) else ""
    }


def comment_to_dict(comment):
    return {
        "id": comment.id,
        "topic_id": comment.topic.id if getattr(comment, "topic", None) else None,
        "author": comment.author.username if getattr(comment, "author", None) else "",
        "content": getattr(comment, "content", ""),
        "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M:%S") if getattr(comment, "created_at", None) else ""
    }


def api_docs(request):
    return JsonResponse({
        "project": "Kingmate Tech Forum",
        "description": "JSON API for testing Django forum data",
        "endpoints": [
            {"method": "GET", "url": "/api/health/", "description": "Kiểm tra API hoạt động"},
            {"method": "GET", "url": "/api/categories/", "description": "Lấy danh sách chuyên mục"},
            {"method": "GET", "url": "/api/topics/", "description": "Lấy danh sách bài viết"},
            {"method": "GET", "url": "/api/topics/?q=django", "description": "Tìm kiếm bài viết theo tiêu đề"},
            {"method": "GET", "url": "/api/topics/<id>/", "description": "Xem chi tiết bài viết và bình luận"},
            {"method": "POST", "url": "/api/auth/login/", "description": "Đăng nhập bằng JSON"},
            {"method": "GET", "url": "/api/auth/me/", "description": "Lấy thông tin người dùng đang đăng nhập"},
            {"method": "POST", "url": "/api/topics/<id>/like/", "description": "Thả tim hoặc bỏ thả tim bài viết"}
        ]
    }, json_dumps_params={"ensure_ascii": False, "indent": 2})


def api_categories(request):
    categories = Category.objects.all()
    return JsonResponse({
        "count": categories.count(),
        "results": [category_to_dict(c) for c in categories]
    }, json_dumps_params={"ensure_ascii": False})


def api_topics(request):
    q = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()

    topics = Topic.objects.select_related("author", "category").all()

    if hasattr(Topic, "created_at"):
        topics = topics.order_by("-created_at")
    else:
        topics = topics.order_by("-id")

    if q:
        topics = topics.filter(title__icontains=q)

    if category_id:
        topics = topics.filter(category_id=category_id)

    return JsonResponse({
        "count": topics.count(),
        "results": [topic_to_dict(t, request) for t in topics]
    }, json_dumps_params={"ensure_ascii": False})


def api_topic_detail(request, topic_id):
    try:
        topic = Topic.objects.select_related("author", "category").get(id=topic_id)
    except Topic.DoesNotExist:
        return JsonResponse({"error": "Topic not found"}, status=404)

    comments = Comment.objects.select_related("author").filter(topic=topic)

    if hasattr(Comment, "created_at"):
        comments = comments.order_by("created_at")

    return JsonResponse({
        "topic": topic_to_dict(topic, request),
        "comments": [comment_to_dict(c) for c in comments]
    }, json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    user = authenticate(request, username=username, password=password)

    if user is None:
        return JsonResponse({"error": "Invalid username or password"}, status=401)

    login(request, user)

    return JsonResponse({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser
        }
    })


def api_me(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            "authenticated": False,
            "user": None
        }, status=401)

    return JsonResponse({
        "authenticated": True,
        "user": {
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "is_staff": request.user.is_staff,
            "is_superuser": request.user.is_superuser
        }
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_like_topic(request, topic_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Login required"}, status=401)

    try:
        topic = Topic.objects.get(id=topic_id)
    except Topic.DoesNotExist:
        return JsonResponse({"error": "Topic not found"}, status=404)

    if not hasattr(topic, "likes"):
        return JsonResponse({
            "error": "Topic model does not have likes field"
        }, status=400)

    if request.user in topic.likes.all():
        topic.likes.remove(request.user)
        liked = False
    else:
        topic.likes.add(request.user)
        liked = True

    return JsonResponse({
        "topic_id": topic.id,
        "liked": liked,
        "likes_count": topic.likes.count()
    })