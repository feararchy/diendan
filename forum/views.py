from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Category, Topic, Comment
from django.contrib.auth.decorators import login_required

def home(request):
    categories = Category.objects.all()
    query = request.GET.get('q') # Lấy từ khóa tìm kiếm
    
    if query:
        # Nếu có gõ tìm kiếm -> Lọc bài viết có chứa từ khóa
        recent_topics = Topic.objects.filter(title__icontains=query).order_by('-created_at')
    else:
        # Nếu không tìm kiếm -> Hiển thị 10 bài mới nhất
        recent_topics = Topic.objects.all().order_by('-created_at')[:10]
        
    return render(request, 'index.html', {'categories': categories, 'recent_topics': recent_topics, 'query': query})

def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content')
        if content:
            Comment.objects.create(topic=topic, author=request.user, content=content)
            return redirect('topic_detail', topic_id=topic.id)
    return render(request, 'topic_detail.html', {'topic': topic})

@login_required(login_url='/login/')
def create_topic(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category_id')
        if title and content and category_id:
            category = Category.objects.get(id=category_id)
            new_topic = Topic.objects.create(title=title, content=content, category=category, author=request.user)
            return redirect('topic_detail', topic_id=new_topic.id)
    return render(request, 'create_topic.html', {'categories': categories})

# --- KHU VỰC XỬ LÝ TÀI KHOẢN ---
def register_user(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        if User.objects.filter(username=u).exists():
            messages.error(request, 'Tên đăng nhập đã có người sử dụng!')
        else:
            user = User.objects.create_user(username=u, password=p)
            login(request, user) # Đăng ký xong tự động đăng nhập luôn
            return redirect('home') # Chuyển về trang chủ
    return render(request, 'register.html')

def login_user(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('home') # Đăng nhập xong (Admin hay Khách) đều về Trang chủ
        else:
            messages.error(request, 'Sai tài khoản hoặc mật khẩu!')
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('home') # Đăng xuất xong về Trang chủ