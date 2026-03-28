from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Category, Topic, Comment
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count

# --- KHU VỰC HIỂN THỊ CHÍNH ---
def home(request):
    categories = Category.objects.all()
    query = request.GET.get('q') # Lấy từ khóa tìm kiếm
    
    if query:
        # Nếu có gõ tìm kiếm -> Lọc bài viết có chứa từ khóa
        topic_list = Topic.objects.filter(title__icontains=query).order_by('-created_at')
    else:
        # Nếu không tìm kiếm -> Hiển thị tất cả bài mới nhất
        topic_list = Topic.objects.all().order_by('-created_at')
        
    # Phân trang (5 bài/trang)
    paginator = Paginator(topic_list, 5) 
    page_number = request.GET.get('page')
    recent_topics = paginator.get_page(page_number)
        
    return render(request, 'index.html', {'categories': categories, 'recent_topics': recent_topics, 'query': query})

def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content')
        if content:
            Comment.objects.create(topic=topic, author=request.user, content=content)
            return redirect('topic_detail', topic_id=topic.id)
    return render(request, 'topic_detail.html', {'topic': topic})

# Lọc bài viết theo Chuyên mục
def category_topics(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    categories = Category.objects.all() # Vẫn lấy danh sách chuyên mục để hiện cột bên phải
    topic_list = Topic.objects.filter(category=category).order_by('-created_at')
    
    # Phân trang (5 bài/trang)
    paginator = Paginator(topic_list, 5) 
    page_number = request.GET.get('page')
    recent_topics = paginator.get_page(page_number)
    
    return render(request, 'category_topics.html', {
        'category': category, 
        'categories': categories, 
        'recent_topics': recent_topics
    })

# --- KHU VỰC THAO TÁC BÀI VIẾT (CRUD) ---
@login_required(login_url='/login/')
def create_topic(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category_id')
        image = request.FILES.get('image') # Lấy file ảnh từ form
        
        if title and content and category_id:
            category = Category.objects.get(id=category_id)
            new_topic = Topic.objects.create(
                title=title, 
                content=content, 
                category=category, 
                author=request.user,
                image=image # Lưu ảnh vào Database
            )
            return redirect('topic_detail', topic_id=new_topic.id)
    return render(request, 'create_topic.html', {'categories': categories})

@login_required(login_url='/login/')
def edit_topic(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    
    # Chặn đứng: Nếu không phải tác giả hoặc không phải Admin thì đuổi ra
    if request.user != topic.author and not request.user.is_staff:
        return redirect('topic_detail', topic_id=topic.id)
        
    categories = Category.objects.all()
    if request.method == 'POST':
        topic.title = request.POST.get('title')
        topic.content = request.POST.get('content')
        category_id = request.POST.get('category_id')
        topic.category = Category.objects.get(id=category_id)
        
        # Nếu người dùng có up ảnh mới thì thay thế ảnh cũ
        if 'image' in request.FILES:
            topic.image = request.FILES['image']
            
        topic.save()
        return redirect('topic_detail', topic_id=topic.id)
        
    return render(request, 'edit_topic.html', {'topic': topic, 'categories': categories})

@login_required(login_url='/login/')
def delete_topic(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    if request.user == topic.author or request.user.is_staff:
        topic.delete()
    return redirect('home')

@login_required(login_url='/login/')
def like_topic(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    if request.user in topic.likes.all():
        topic.likes.remove(request.user) # Nếu đã like rồi thì bỏ like
    else:
        topic.likes.add(request.user) # Chưa like thì thả tim
    return redirect('topic_detail', topic_id=topic.id)


# --- KHU VỰC XỬ LÝ TÀI KHOẢN VÀ THÀNH VIÊN ---
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
            return redirect('home')
        else:
            messages.error(request, 'Sai tài khoản hoặc mật khẩu!')
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('home')

def user_profile(request, username):
    user_prof = get_object_or_404(User, username=username)
    user_topics = Topic.objects.filter(author=user_prof).order_by('-created_at')
    return render(request, 'profile.html', {'user_prof': user_prof, 'user_topics': user_topics})

# Hiển thị danh sách Tất cả Thành viên (Đã tích hợp Bảng Xếp Hạng)
def members_list(request):
    # Dùng hàm Count để đếm số bài viết (topic), sau đó order_by giảm dần (-topic_count)
    users = User.objects.annotate(topic_count=Count('topic')).order_by('-topic_count', 'username')
    return render(request, 'members.html', {'users': users})