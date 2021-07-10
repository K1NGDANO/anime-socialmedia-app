from django import forms
from linkedin_app.models import Post

class SignUpForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField(max_length=50)
    bio = forms.CharField(max_length=150)
    image = forms.ImageField()

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)


class CreatePost(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'body'
        ]


class MessageForm(forms.Form):
    text= forms.CharField(max_length=140)