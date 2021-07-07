from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from linkedin_app.forms import SignUpForm, LoginForm, CreatePost
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from linkedin_app.models import CustomUser, Post

# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')



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
                    # image=data['image'],
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
        my_user = CustomUser.objects.filter(id=user_id)
        posts = Post.objects.filter(user_name=request.user)
        return render(request, 'profile_page.html', {'my_user': my_user, 'posts': posts})