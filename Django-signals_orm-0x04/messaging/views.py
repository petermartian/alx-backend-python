from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.cache import cache_page
from django.db import models
from .models import Message


@login_required
def delete_user(request):
    user = request.user
    logout(request)
    user.delete()
    return redirect('/')  # or redirect to a goodbye page


def get_all_replies(message):
    replies = []
    def recurse(msg):
        children = msg.replies.all()
        for child in children:
            replies.append(child)
            recurse(child)
    recurse(message)
    return replies


@cache_page(60)  # cache for 60 seconds
@login_required
def conversation_view(request):
    messages = (
        Message.objects
        .filter(models.Q(sender=request.user) | models.Q(receiver=request.user))
        .select_related('sender', 'receiver', 'parent_message')
        .prefetch_related('replies')
        .order_by('-timestamp')
    )

    # Only root messages (not replies)
    root_messages = [msg for msg in messages if not msg.parent_message]

    return render(request, 'messaging/conversation.html', {
        'messages': root_messages,  # for rendering only top-level
    })


def get_all_replies(message):
    replies = []

    def recurse(msg):
        children = Message.objects.filter(parent_message=msg)
        for child in children:
            replies.append(child)
            recurse(child)

    recurse(message)
    return replies


@login_required
def unread_messages_view(request):
    unread_msgs = Message.unread.for_user(request.user)
    return render(request, 'messaging/unread.html', {'messages': unread_msgs})

@login_required
def unread_messages_view(request):
    unread_msgs = Message.unread.unread_for_user(request.user)
    return render(request, 'messaging/unread.html', {'messages': unread_msgs})




