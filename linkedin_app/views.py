from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from linkedin_app.forms import SignUpForm, LoginForm, CreatePost, MessageForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from linkedin_app.models import CustomUser, Post, DirectMessage, Message

# Create your views here.
@login_required
def index(request):
    posts = Post.objects.all()
    return render(request, 'index.html', {'posts':posts})


@login_required
def follow_view(request):
    followers = request.user.following.all()
    posts = Post.objects.filter(user_name__in=followers)
    my_posts = Post.objects.filter(user_name=request.user)
    posts = posts.union(my_posts)
    return render(request, 'index.html', {'posts':posts})



class SignUpView(View):
    def get(self, request):
        form_title = 'Sign Up'
        form = SignUpForm()
        return render(request, 'genform.html', {'form': form, 'form_title': form_title})

    def post(self, request):
        if request.method == 'POST':
            form = SignUpForm(request.POST, request.FILES)
            print('Form was posted')
            if form.is_valid():
                print('Form is valid')
                data = form.cleaned_data
                my_user = CustomUser.objects.create_user(
                    username=data['username'],
                    password=data['password'],
                    name=data['name'],
                    bio=data['bio'],
                    image=data['image'],
                )
                if my_user:
                    login(request, my_user)
                    return HttpResponseRedirect('/')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            my_user = authenticate(username=data['username'], password=data['password'])

            if my_user:
                login(request, my_user)
                return HttpResponseRedirect('/')

    form_title = 'Log In'
    form = LoginForm()
    return render(request, 'genform.html', {'form': form, 'form_title': form_title})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/login/')


class CreatePostView(LoginRequiredMixin, View):
    def get(self, request):
        form_title = 'Create New post'
        form = CreatePost()
        return render(request, 'genform.html', {'form': form, 'form_title': form_title})
        
    def post(self, request):
        if request.method == 'POST':
            form = CreatePost(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                Post.objects.create(
                    user_name=request.user,
                    title=data['title'],
                    body=data['body']
                )
                return HttpResponseRedirect('/')



class ProfilePageView(View):
    def get(self, request, user_id):
        my_user = CustomUser.objects.get(id=user_id)
        posts = Post.objects.filter(user_name=my_user.id)
        return render(request, 'profile_page.html', {'my_user': my_user, 'posts': posts})


@login_required
def add_follow(request, user_id):
    follow = CustomUser.objects.get(id=user_id)
    user = request.user
    if follow != user:
        user.following.add(follow)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def un_follow(request, user_id):
    follow = CustomUser.objects.get(id=user_id)
    user = request.user
    if follow != user:
        user.following.remove(follow)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class DirectMessagePost(LoginRequiredMixin, View):
    
    def get(self, request, user_id):
        form = MessageForm()
        return render(request, 'genform.html', {'form':form})
    
    def post(self, request, user_id):
        target = CustomUser.objects.get(id=user_id)
        form = MessageForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            DM = Message.objects.create(text=data['text'])
            DirectMessage.objects.create(target=target, message=DM, author= request.user)
            return HttpResponseRedirect('/')


def direct_message_view(request):
    DMS = DirectMessage.objects.filter(target=request.user)
    authors=[]
    for dm in DMS:
        if dm.author not in authors:
            authors.append(dm.author)

    return render(request, 'dm_view.html', {'dms': authors})


def message_feed_view(request, author_id):
    DMS = DirectMessage.objects.filter(target=request.user).filter(author=author_id)
    DMS2 = DirectMessage.objects.filter(target=author_id).filter(author=request.user)
    DMS = DMS.union(DMS2)
    if request.method == 'POST':
        target = CustomUser.objects.get(id=author_id)
        form = MessageForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            DM = Message.objects.create(text=data['text'])
            DirectMessage.objects.create(target=target, message=DM, author= request.user)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    form = MessageForm()
    return render(request, 'messagefeed.html', {'dms': DMS, 'form': form})