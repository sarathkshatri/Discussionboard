
from datetime import timezone, datetime

import xlwt
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from .forms import NewTopicForm, PostForm, BoardForm
from .models import Board, Topic, Post
from django.contrib import messages
from django. views.generic import UpdateView, DeleteView
import datetime

# Create your views here.
@login_required()
def discussion(request):
    board = Board.objects.all()
    return render(request, 'discussion.html',{'board' : board})

@login_required()
@user_passes_test(lambda u: u.is_superuser)
def edit_board(request,pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == "POST":
        form = BoardForm(request.POST, instance=board)
        if form.is_valid():
            boardform = form.save(commit=False)
            # topicform.subject = Topic.subject
            #boardform.author = request.user
            boardform.save()
            print(boardform.name)
            messages.success(request, f'Your Board has been updated')
            return redirect('discussion')
    else:
        # edit
        form = BoardForm(instance=board)
    return render(request, 'board_edit.html', {'form': form})

@login_required()
@user_passes_test(lambda u: u.is_superuser)
def delete_board(request,pk):
    board = get_object_or_404(Board, pk=pk)
    board.delete()
    return redirect('discussion')

@login_required()
@user_passes_test(lambda u: u.is_superuser)
def new_board(request):
    if request.method == 'GET':

        form = BoardForm()
        context = {
                'bform': form,
        }
        return render(request, 'new_board.html', context)
    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            boardform = form.save(commit=False)
            # topicform.subject = Topic.subject
            boardform.author = request.user
            boardform.save()
            print(boardform.name)
            messages.success(request, f'Your New Board has been updated')
            return redirect('discussion')


@login_required()
def discussion_topic(request, pk):
    post = get_object_or_404(Board,pk=pk)
    topics = post.topics.order_by('-last_updated').annotate(replies=Count('posts'))
    return render(request, 'discussion_topic.html', {'post': post, 'topics': topics})

@login_required()
@user_passes_test(lambda u: u.is_superuser)
def new_topic(request, pk):

    board = get_object_or_404(Board, pk=pk)


    if request.method == 'GET':

        form = NewTopicForm()
        context = {
                'tform': form,
                'board': board
        }
        return render(request, 'new_topic.html', context)

    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topicform = form.save(commit=False)
            topicform.board = board
            #topicform.subject = Topic.subject
            topicform.author = request.user
            topicform.save()
            print(topicform.board)
            messages.success(request, f'Your Topic has been updated')
            return redirect('discussion_topic', pk=board.pk)

@login_required()
@user_passes_test(lambda u: u.is_superuser)
def edit_topic(request,pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    board = get_object_or_404(Board, pk=pk)
    if request.method == "GET":
        form = NewTopicForm(instance= topic)
        context = {
            'form': form,
            'topic': topic
        }
        return render(request, 'edit_topic.html', context)
    if request.method == 'POST':
        form = NewTopicForm(request.POST, instance=topic)
        if form.is_valid():
            topicform = form.save(commit=False)
            topicform.author = request.user
            topicform.save()
            print(topicform.board)
            messages.success(request, f'Your Topic has been updated')
            return redirect('discussion_topic', pk=board.pk)

@login_required()
@user_passes_test(lambda u: u.is_superuser)
def delete_topic(request,pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    board = get_object_or_404(Board, pk=pk)
    topic.delete()
    return redirect('discussion_topic', pk=board.pk)


@login_required()
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


class PostUpdateView(LoginRequiredMixin,UserPassesTestMixin, UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def form_valid(self, form):
        post = self.get_object()
        if self.request.user == form.instance.created_by:
            post = form.save(commit=False)
            post.updated_by = self.request.user
            post.updated_at = timezone.now()
            post.save()
            return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)
        return False


   # def form_valid(self, form):
    #    form.instance.author = self.request.user
     #   return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.created_by:
            return True
        return False


class PostDeleteView(LoginRequiredMixin,UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'delete_post.html'
    pk_url_kwarg = 'post_pk'
    success_url = reverse_lazy('discussion')

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.created_by:
            return True
        return False

@login_required
def export_boards_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment;' \
                                      'filename=Boards.csv'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Boards')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['name', 'description']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style.font.bold = False

    boards = Board.objects.all().values_list('name', 'description')

    for wo in boards:
        row_num += 1
        for col_num in range(len(wo)):
            value = wo[col_num]
            #if isinstance(value, datetime.datetime):
             #   value = value.strftime('%d/%m/%Y')
            #if isinstance(value, ):
               # value = value.__str__()
            #if isinstance(value, Roomallotment):
             #   value = value.__str__()
            ws.write(row_num, col_num, value, font_style)

    wb.save(response)
    return response


@login_required()
def export_topics_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment;' \
                                      'filename=Topics.csv'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Topics')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['subject', 'last_updated','board', 'author']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style.font.bold = False

    topics = Topic.objects.all().values_list('subject', 'last_updated','board', 'author')

    for wo in topics:
        row_num += 1
        for col_num in range(len(wo)):
            value = wo[col_num]
            if isinstance(value, datetime.datetime):
               value = value.strftime('%d/%m/%Y')
            # if isinstance(value,author):
            # value = value.__str__()
            # if isinstance(value, Roomallotment):
            #   value = value.__str__()
            ws.write(row_num, col_num, value, font_style)

    wb.save(response)
    return response


@login_required()
def export_posts_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment;' \
                                      'filename=Posts.csv'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Posts')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['message', 'topic','created_at', 'updated_at','created_by','updated_by']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style.font.bold = False

    posts = Post.objects.all().values_list('message', 'topic','created_at', 'updated_at','created_by','updated_by')

    for wo in posts:
        row_num += 1
        for col_num in range(len(wo)):
            value = wo[col_num]
            if isinstance(value, datetime.datetime):
               value = value.strftime('%d/%m/%Y')
            # if isinstance(value,author):
            # value = value.__str__()
            # if isinstance(value, Roomallotment):
            #   value = value.__str__()
            ws.write(row_num, col_num, value, font_style)

    wb.save(response)
    return response