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
    return render(request, 'index.html', {'posts':posts.order_by('-id')})


@login_required
def follow_view(request):
    followers = request.user.following.all()
    posts = Post.objects.filter(user_name__in=followers)
    my_posts = Post.objects.filter(user_name=request.user)
    posts = posts.union(my_posts)
    return render(request, 'index.html', {'posts':posts.order_by('-id')})



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
            form = CreatePost(request.POST, request.FILES)
            if form.is_valid():
                data = form.cleaned_data
                Post.objects.create(
                    user_name=request.user,
                    title=data['title'],
                    body=data['body'],
                    image = data['image']
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



def direct_message_view(request):
    '''
    grabs all direct messages written by and targeting the current user
    loops through them and checks if the message is in the feed list already
    if feed is empty appends the most recent message and moves onto the next dm
    if feed is not empty it loops through feed and if any of feed items have a
    user equal to the current dm author or target(loop ran based on if author is user or not)
    if that is true it marks in_feed as true meaning the message will not be added to
    the feed
    '''
    DMS = DirectMessage.objects.filter(target=request.user)
    DMS = DMS.union(DirectMessage.objects.filter(author=request.user)).order_by('-id')
    feed=[]
    for dm in DMS:
        in_feed = False
        if dm.author == request.user:
            if len(feed) == 0:
                feed.append({'user':dm.target, 'message': dm.message})
                continue
            else:
                for item in feed:
                    if item['user'] == dm.target:
                        in_feed = True
            if not in_feed:
                feed.append({'user':dm.target, 'message': dm.message})
        else:
            if len(feed) == 0:
                feed.append({'user':dm.author, 'message': dm.message})
                continue
            else:
                for item in feed:
                    if item['user'] == dm.author:
                        in_feed = True
            if not in_feed:
                feed.append({'user':dm.author, 'message': dm.message})

    return render(request, 'dm_view.html', {'dms': feed})


def message_feed_view(request, author_id):
    if request.user.id == author_id:
        return HttpResponseRedirect('/')
    target = CustomUser.objects.get(id=author_id)
    DMS = DirectMessage.objects.filter(target=request.user).filter(author=author_id)
    for dm in DMS:
        dm.message.seen = True
        dm.message.save()
    DMS2 = DirectMessage.objects.filter(target=author_id).filter(author=request.user)
    DMS = DMS.union(DMS2)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            DM = Message.objects.create(text=data['text'])
            DirectMessage.objects.create(target=target, message=DM, author= request.user)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    form = MessageForm()
    return render(request, 'messagefeed.html', {'dms': DMS, 'form': form, 'target': target})


@login_required
def handle_like(request, post_id):
    like = Post.objects.get(id=post_id)
    user = request.user
    if like not in user.liked_posts.all():
        user.liked_posts.add(like)
        like.likes += 1
        like.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        user.liked_posts.remove(like)
        like.likes -= 1
        like.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
