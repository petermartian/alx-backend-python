from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory

class SignalTestCase(TestCase):
    def test_notification_created_on_message(self):
        sender = User.objects.create_user(username='alice', password='12345')
        receiver = User.objects.create_user(username='bob', password='12345')

        message = Message.objects.create(sender=sender, receiver=receiver, content="Hello!")

        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, receiver)
        self.assertEqual(notification.message, message)

def test_message_edit_creates_history(self):
    sender = User.objects.create_user(username='alice2', password='123')
    receiver = User.objects.create_user(username='bob2', password='123')
    message = Message.objects.create(sender=sender, receiver=receiver, content="Original")

    # Edit message
    message.content = "Edited content"
    message.save()

    self.assertTrue(message.edited)
    self.assertEqual(MessageHistory.objects.count(), 1)
    history = MessageHistory.objects.first()
    self.assertEqual(history.old_content, "Original")

def test_user_deletion_cleans_related_data(self):
    user = User.objects.create_user(username='to_delete', password='123')
    receiver = User.objects.create_user(username='other', password='123')
    message = Message.objects.create(sender=user, receiver=receiver, content="Bye")
    Notification.objects.create(user=receiver, message=message)

    self.assertEqual(Message.objects.count(), 1)
    user.delete()
    self.assertEqual(Message.objects.count(), 0)  # Sender's message gonedef test_threaded_messages(self):
    u1 = User.objects.create_user(username='u1', password='123')
    u2 = User.objects.create_user(username='u2', password='123')

    parent = Message.objects.create(sender=u1, receiver=u2, content="Root message")
    reply1 = Message.objects.create(sender=u2, receiver=u1, content="Reply 1", parent_message=parent)
    reply2 = Message.objects.create(sender=u1, receiver=u2, content="Reply 2", parent_message=reply1)

    self.assertEqual(parent.replies.count(), 1)
    self.assertEqual(reply1.replies.count(), 1)
    self.assertEqual(reply2.replies.count(), 0)


def test_unread_message_manager(self):
    u1 = User.objects.create_user(username='u1m', password='pass')
    u2 = User.objects.create_user(username='u2m', password='pass')
    Message.objects.create(sender=u1, receiver=u2, content='Hello!', read=False)
    Message.objects.create(sender=u1, receiver=u2, content='Read msg', read=True)

    unread = Message.unread.for_user(u2)
    self.assertEqual(unread.count(), 1)








