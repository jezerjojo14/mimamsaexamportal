# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import ChatRoom, ChatLog, User, Team


LOG_MAX=10

class TestConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'test_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': action+'_message'
            }
        )

    # Receive message from room group
    def start_message(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": "start"}))
        user = self.scope["user"]
        user.started_test=True
        user.save()

    def end_message(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": "end"}))
        user = self.scope["user"]
        user.entered_test=False
        user.started_test=False
        user.ended_test=True
        user.save()


class LogsConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'logs_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        user = self.scope["user"]
        user.entered_test=True
        user.save()

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

        user = self.scope["user"]
        user.entered_test=False
        user.started_test=False
        user.save()

    def receive(self, text_data):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'log_message'
            }
        )

    # Receive message from room group
    def log_message(self, event):
        # Send message to WebSocket
        self.send()


class QuestionConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'mark_q_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        qnumber = text_data_json['qnumber']
        status = text_data_json['status']
        username = text_data_json['username']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'mark_question',
                'message': {
                    'qnumber': qnumber,
                    'username': username,
                    'status': status
                }
            }
        )

    # Receive message from room group
    def mark_question(self, event):
        print(event)
        qnumber = event['message']['qnumber']
        username = event['message']['username']
        status = event['message']['status']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'qnumber': qnumber,
            'username': username,
            'status': status
        }))


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        message = text_data_json['message']
        username = text_data_json['username']
        code = text_data_json['code']
        print(username+'\n'+message+'\n'+code)

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {'content': message, 'username': username, 'code': code},
                # 'username': username,
                # 'code': code,
            }
        )

        print("Message sent to room")



    # Receive message from room group
    def chat_message(self, event):
        print(event)
        message = event['message']['content']
        username = event['message']['username']
        code = event['message']['code']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'code': code,
        }))

        team=Team.objects.get(sequence=self.room_name)
        room_model=ChatRoom.objects.get_or_create(team_instance=team, defaults={'chatlog_start': 0})[0]
        log_count=ChatLog.objects.filter(chatroom_instance=room_model).count()

        if log_count<LOG_MAX:
            ChatLog.objects.create(chatroom_instance=room_model, user_instance=User.objects.get(username=username), message=message, log_number=log_count)
        else:
            log=ChatLog.objects.get(chatroom_instance=room_model, log_number=room_model.chatlog_start)
            log.user_instance=User.objects.get(username=username)
            log.message=message
            log.save()
            room_model.chatlog_start=(room_model.chatlog_start+1)%LOG_MAX
            room_model.save()
