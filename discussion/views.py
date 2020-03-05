
from datetime import timezone
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from .forms import NewTopicForm, PostForm
from .models import Board, Topic, Post
from django.contrib import messages
from django. views.generic import UpdateView, DeleteView

# Create your views here.
def discussion(request):
    board = Board.objects.all()
    return render(request, 'discussion.html',{'board' : board})

def discussion_topic(request, pk):
    post = get_object_or_404(Board,pk=pk)
    topics = post.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
    return render(request, 'discussion_topic.html', {'post': post, 'topics': topics})

def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        tform = NewTopicForm(request.POST)
        if tform.is_valid():
            topicform = tform.save(commit=False)
            topicform.board = board
            topicform.subject = Topic.subject
            topicform.author = request.user
            topicform.save()
            print(topicform.board)
            messages.success(request, f'Your Topic has been updated')
            return redirect('discussion_topic', pk=board.pk)
    else:
        tform = NewTopicForm()
    context = {
            'topicform': tform
    }
    return render(request, 'new_topic.html', {'board': board}, context)


def topic_posts(request, pk, topic_pk):
    top = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    top.views += 1
    top.save()
    return render(request, 'topic_posts.html', {'top': top})

@login_required
def reply_topic(request, pk, topic_pk):
    top = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            replyform = form.save(commit=False)
            replyform.topic = top
            replyform.created_by = request.user
            replyform.save()
            return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'top': top, 'replyform': form})

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)



class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'delete_post.html'
    pk_url_kwarg = 'post_pk'
    success_url = reverse_lazy('discussion')