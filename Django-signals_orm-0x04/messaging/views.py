from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message
from django.shortcuts import render
from django.views.decorators.cache import cache_page


@login_required
def delete_user(request):
    user = request.user
    logout(request)
    user.delete()
    return redirect('/')  # or a "goodbye" page

@login_required
def conversation_view(request):
    messages = (
        Message.objects
        .filter(receiver=request.user)
        .select_related('sender', 'receiver', 'parent_message')
        .prefetch_related('replies')
        .order_by('-timestamp')
    )
    return render(request, 'messaging/conversation.html', {'messages': messages})

@login_required
def unread_messages_view(request):
    unread_msgs = Message.unread.for_user(request.user)
    return render(request, 'messaging/unread.html', {'messages': unread_msgs})


@cache_page(60)  # cache for 60 seconds
@login_required
def conversation_view(request):
    messages = (
        Message.objects
        .filter(receiver=request.user)
        .select_related('sender', 'receiver', 'parent_message')
        .prefetch_related('replies')
        .order_by('-timestamp')
    )
    return render(request, 'messaging/conversation.html', {'messages': messages})

