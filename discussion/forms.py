from django import forms
from .models import Topic, Post, Board

class NewTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = [ 'subject']

    def __init__(self, *args, **kwargs):
        super(NewTopicForm, self).__init__(*args, **kwargs)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['message', ]


class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['name', 'description']
