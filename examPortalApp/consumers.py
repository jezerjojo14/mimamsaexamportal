# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import ChatRoom, ChatLog, User, Team, Ordering


LOG_MAX=10

#
# class TheConsumer(WebsocketConsumer):
#     def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = 'consume_%s' % self.room_name
#
#         # Join room group
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name,
#             self.channel_name
#         )
#         print("joined room")
#         user = self.scope["user"]
#         if user.user_type=="proctor":
#             user.entered_video_call=True
#             user.save()
#             print(user.username+" joined video call logged")
#             team = Team.objects.get(sequence=self.room_name)
#             print(team)
#             proctor_user=User.objects.filter(proctored_teams=team).filter(entered_video_call=True)
#             peers = list((User.objects.filter(team=team).filter(entered_video_call=True)).union(proctor_user).values_list('username', flat=True))
#             print(peers)
#             for peer in peers:
#                 print(peer)
#                 if user.username == peer:
#                     print("lol thats just me tho")
#                     continue
#                 async_to_sync(self.channel_layer.group_send)(
#                 self.room_group_name,
#                     {
#                         'type': 'add_peer',
#                         'message': {
#                         'targetpeer': peer,
#                         'newcomer': user.username,
#                         }
#                     }
#                 )
#             print("adding peers")
#         self.accept()
#
#     def disconnect(self, close_code):
#         # Leave room group
#         user = self.scope["user"]
#         if user.entered_video_call:
#             user.entered_video_call=False
#             user.save()
#             async_to_sync(self.channel_layer.group_send)(
#                 self.room_group_name,
#                 {
#                     'type': 'remove_peer',
#                     'message': {
#                         'username': username,
#                     }
#                 }
#             )
#
#         user.entered_test=False
#         user.started_test=False
#         user.save()
#
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name,
#             self.channel_name
#         )
#
#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         consumer = text_data_json['consumer']
#         if consumer=="video":
#             message = text_data_json['message']
#             user = self.scope["user"]
#             id = text_data_json['id']
#             if message=='initSend':
#                 # Send message to room group
#                 async_to_sync(self.channel_layer.group_send)(
#                     self.room_group_name,
#                     {
#                         'type': 'init_send',
#                         'message': {
#                             'from': user.username,
#                             'to': id
#                         }
#                     }
#                 )
#             if message=='signal':
#                 # Send message to room group
#                 signal = text_data_json['signal']
#                 async_to_sync(self.channel_layer.group_send)(
#                     self.room_group_name,
#                     {
#                         'type': 'signal',
#                         'message': {
#                             'from': user.username,
#                             'to': id,
#                             'signal': signal
#                         }
#                     }
#                 )
#
#         elif consumer=="test":
#             action = text_data_json['message']
#             print("receive: "+str(text_data_json))
#             # Send message to room group
#             async_to_sync(self.channel_layer.group_send)(
#                 self.room_group_name,
#                 {
#                     'type': action+'_message'
#                 }
#             )
#
#         elif consumer=="log":
#             async_to_sync(self.channel_layer.group_send)(
#                 self.room_group_name,
#                 {
#                     'type': 'log_message'
#                 }
#             )
#
#         elif consumer=="question":
#             print(text_data_json)
#             qnumber = text_data_json['qnumber']
#             status = text_data_json['status']
#             username = text_data_json['username']
#
#             # Send message to room group
#             async_to_sync(self.channel_layer.group_send)(
#                 self.room_group_name,
#                 {
#                     'type': 'mark_question',
#                     'message': {
#                         'qnumber': qnumber,
#                         'username': username,
#                         'status': status
#                     }
#                 }
#             )
#
#         elif consumer=="chat":
#             message = text_data_json['message']
#             username = text_data_json['username']
#             code = text_data_json['code']
#             print(username+'\n'+message+'\n'+code)
#
#             # Send message to room group
#             async_to_sync(self.channel_layer.group_send)(
#                 self.room_group_name,
#                 {
#                     'type': 'chat_message',
#                     'message': {'content': message, 'username': username, 'code': code},
#                     # 'username': username,
#                     # 'code': code,
#                 }
#             )
#
#             print("Message sent to room")
#
#     # VideoConsumer
#
#     def init_send(self, event):
#         username = event['message']['from']
#         id = event['message']['to']
#         user = self.scope["user"]
#         team = Team.objects.get(sequence=self.room_name)
#         if Ordering.objects.filter(user_instance=user).count():
#             self_peer_id=Ordering.objects.get(user_instance=user).order_index
#         else:
#             self_peer_id=user.username
#         if id=='video-'+str(team.team_id)+'-'+str(self_peer_id):
#             if Ordering.objects.filter(user_instance__username=username).count():
#                 from_peer_id=Ordering.objects.get(user_instance__username=username).order_index
#                 from_id='video-'+str(team.team_id)+'-'+str(from_peer_id)
#             else:
#                 from_id=username
#             self.send(text_data=json.dumps({"message": "initSend", "id": from_id}))
#
#     def signal(self, event):
#         username = event['message']['from']
#         signal = event['message']['signal']
#         id = event['message']['to']
#         user = self.scope["user"]
#         team = Team.objects.get(sequence=self.room_name)
#         if Ordering.objects.filter(user_instance=user).count():
#             self_peer_id=Ordering.objects.get(user_instance=user).order_index
#             if id=='video-'+str(team.team_id)+'-'+str(self_peer_id):
#                 if Ordering.objects.filter(user_instance__username=username).count():
#                     from_peer_id=Ordering.objects.get(user_instance__username=username).order_index
#                     from_id='video-'+str(team.team_id)+'-'+str(from_peer_id)
#                 else:
#                     from_id=username
#                 self.send(text_data=json.dumps({"message": "signal", "id": from_id, "signal": signal}))
#         elif id==user.username:
#             if Ordering.objects.filter(user_instance__username=username).count():
#                 from_peer_id=Ordering.objects.get(user_instance__username=username).order_index
#                 from_id='video-'+str(team.team_id)+'-'+str(from_peer_id)
#             else:
#                 from_id=username
#             self.send(text_data=json.dumps({"message": "signal", "id": from_id, "signal": signal}))
#
#     def add_peer(self, event):
#         print("add_peer")
#         if (self.scope["user"]).username == event['message']['targetpeer']:
#             username = event['message']['newcomer']
#             team = Team.objects.get(sequence=self.room_name)
#             if Ordering.objects.filter(user_instance__username=username).count():
#                 self_peer_id=Ordering.objects.get(user_instance__username=username).order_index
#                 id='video-'+str(team.team_id)+'-'+str(self_peer_id)
#             else:
#                 id=username
#             self.send(text_data=json.dumps({"message": "initReceive", "id": id}))
#
#     def remove_peer(self, event):
#         print("remove peer")
#         username = event['message']['username']
#         team = Team.objects.get(sequence=self.room_name)
#         if Ordering.objects.filter(user_instance__username=username).count():
#             self_peer_id=Ordering.objects.get(user_instance__username=username).order_index
#             id='video-'+str(team.team_id)+'-'+str(self_peer_id)
#         else:
#             id=username
#         self.send(text_data=json.dumps({"message": "removePeer", "id": id}))
#
#     # TestConsumer
#
#     def start_message(self, event):
#         # Send message to WebSocket
#         print("start_message")
#         self.send(text_data=json.dumps({"message": "start"}))
#         user = self.scope["user"]
#         if user.user_type=="participant":
#             user.started_test=True
#             user.save()
#
#     def end_message(self, event):
#         # Send message to WebSocket
#         self.send(text_data=json.dumps({"message": "end"}))
#         user = self.scope["user"]
#         user.entered_test=False
#         user.started_test=False
#         user.ended_test=True
#         user.save()
#
#     # LogsConsumer
#
#     def log_message(self, event):
#         # Send message to WebSocket
#         self.send()
#
#     #QuestionConsumer
#
#     def mark_question(self, event):
#         print(event)
#         qnumber = event['message']['qnumber']
#         username = event['message']['username']
#         status = event['message']['status']
#         # Send message to WebSocket
#         self.send(text_data=json.dumps({
#             'qnumber': qnumber,
#             'username': username,
#             'status': status
#         }))
#
#     #ChatConsumer
#
#     def chat_message(self, event):
#         print(event)
#         message = event['message']['content']
#         username = event['message']['username']
#         code = event['message']['code']
#         # Send message to WebSocket
#         self.send(text_data=json.dumps({
#             'message': message,
#             'username': username,
#             'code': code,
#         }))
#
#         team=Team.objects.get(sequence=self.room_name)
#         room_model=ChatRoom.objects.get_or_create(team_instance=team, defaults={'chatlog_start': 0})[0]
#         log_count=ChatLog.objects.filter(chatroom_instance=room_model).count()
#
#         if log_count<LOG_MAX:
#             ChatLog.objects.create(chatroom_instance=room_model, user_instance=User.objects.get(username=username), message=message, log_number=log_count)
#         else:
#             log=ChatLog.objects.get(chatroom_instance=room_model, log_number=room_model.chatlog_start)
#             log.user_instance=User.objects.get(username=username)
#             log.message=message
#             log.save()
#             room_model.chatlog_start=(room_model.chatlog_start+1)%LOG_MAX
#             room_model.save()


class VideoConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'video_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        print("joined room")
        user = self.scope["user"]
        user.entered_video_call=True
        user.save()
        print(user.username+" joined video call logged")
        team = Team.objects.get(sequence=self.room_name)
        print(team)
        proctor_user=User.objects.filter(proctored_teams=team).filter(entered_video_call=True)
        print((User.objects.filter(team=team).filter(entered_video_call=True)))
        peers = list((User.objects.filter(team=team).filter(entered_video_call=True)).union(proctor_user).values_list('username', flat=True))
        print(peers)
        for peer in peers:
            print(peer)
            if user.username == peer:
                print("lol thats just me tho")
                continue
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'add_peer',
                    'message': {
                        'targetpeer': peer,
                        'newcomer': user.username,
                    }
                }
            )
        print("adding peers")
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        print("We're in")
        user = self.scope["user"]
        print("user defined")
        user.entered_test=False
        user.entered_video_call=False
        user.save()
        print("entered_video_call False")
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'remove_peer',
                'message': {
                    'username': user.username,
                }
            }
        )
        print("remove_peer")
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def remove_peer(self, event):
        print("remove peer")
        username = event['message']['username']
        if (self.scope["user"]).username != username:
            team = Team.objects.get(sequence=self.room_name)
            if Ordering.objects.filter(user_instance__username=username).count():
                self_peer_id=Ordering.objects.get(user_instance__username=username).order_index
                id='video-'+str(team.team_id)+'-'+str(self_peer_id)
            else:
                id=username
            print("id: "+id)
            self.send(text_data=json.dumps({"message": "removePeer", "id": id}))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope["user"]
        if message=='initSend':
            # Send message to room group
            id = text_data_json['id']
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'init_send',
                    'message': {
                        'from': user.username,
                        'to': id
                    }
                }
            )
        if message=='signal':
            # Send message to room group
            id = text_data_json['id']
            signal = text_data_json['signal']
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'signal',
                    'message': {
                        'from': user.username,
                        'to': id,
                        'signal': signal
                    }
                }
            )
        if message=='ping':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'ping',
                    'message': {
                        'from': user.username,
                    }
                }
            )

    def ping(self, event):
        if (self.scope["user"]).username==event["message"]["from"]:
            self.send(text_data=json.dumps({"message": "pong"}))
            if user.entered_video_call==False:
                user.entered_video_call=True
                user.save()


    def init_send(self, event):
        print("init_send")
        username = event['message']['from']
        id = event['message']['to']
        user = self.scope["user"]
        team = Team.objects.get(sequence=self.room_name)
        if Ordering.objects.filter(user_instance=user).count():
            self_peer_id=Ordering.objects.get(user_instance=user).order_index
            if id=='video-'+str(team.team_id)+'-'+str(self_peer_id):
                if Ordering.objects.filter(user_instance__username=username).count():
                    from_peer_id=Ordering.objects.get(user_instance__username=username).order_index
                    from_id='video-'+str(team.team_id)+'-'+str(from_peer_id)
                else:
                    from_id=username
                self.send(text_data=json.dumps({"message": "initSend", "id": from_id}))
        elif id==user.username:
            if Ordering.objects.filter(user_instance__username=username).count():
                from_peer_id=Ordering.objects.get(user_instance__username=username).order_index
                from_id='video-'+str(team.team_id)+'-'+str(from_peer_id)
            else:
                from_id=username
            self.send(text_data=json.dumps({"message": "initSend", "id": from_id}))

    def signal(self, event):
        username = event['message']['from']
        signal = event['message']['signal']
        id = event['message']['to']
        user = self.scope["user"]
        team = Team.objects.get(sequence=self.room_name)
        if Ordering.objects.filter(user_instance=user).count():
            self_peer_id=Ordering.objects.get(user_instance=user).order_index
            if id=='video-'+str(team.team_id)+'-'+str(self_peer_id):
                if Ordering.objects.filter(user_instance__username=username).count():
                    from_peer_id=Ordering.objects.get(user_instance__username=username).order_index
                    from_id='video-'+str(team.team_id)+'-'+str(from_peer_id)
                else:
                    from_id=username
                self.send(text_data=json.dumps({"message": "signal", "id": from_id, "signal": signal}))
        elif id==user.username:
            if Ordering.objects.filter(user_instance__username=username).count():
                from_peer_id=Ordering.objects.get(user_instance__username=username).order_index
                from_id='video-'+str(team.team_id)+'-'+str(from_peer_id)
            else:
                from_id=username
            self.send(text_data=json.dumps({"message": "signal", "id": from_id, "signal": signal}))

    def add_peer(self, event):
        print("add_peer")
        if (self.scope["user"]).username == event['message']['targetpeer']:
            print((self.scope["user"]).username)
            username = event['message']['newcomer']
            team = Team.objects.get(sequence=self.room_name)
            if Ordering.objects.filter(user_instance__username=username).count():
                self_peer_id=Ordering.objects.get(user_instance__username=username).order_index
                id='video-'+str(team.team_id)+'-'+str(self_peer_id)
            else:
                id=username
            self.send(text_data=json.dumps({"message": "initReceive", "id": id}))


class TestConsumer(WebsocketConsumer):
    def connect(self):
        print("Connected to TestConsumer")
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'test_%s' % self.room_name

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
        team = Team.objects.get(sequence=self.room_name)
        user = self.scope["user"]
        user.entered_video_call=False
        user.entered_test=False
        if not team.finished:
            user.ended_test=False
        user.save()

    def receive(self, text_data):
        print("received text data")
        text_data_json = json.loads(text_data)
        action = text_data_json['message']
        print("receive: "+str(text_data_json))
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
        print("start_message")
        self.send(text_data=json.dumps({"message": "start"}))
        user = self.scope["user"]
        if user.user_type=="participant":
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

    def change_device(self, event):
        print("change_device")
        print(event)
        username=event["message"]["username"]
        user = self.scope["user"]
        print(username)
        print(user.username)
        if user.username==username:
            print("sending")
            self.send(text_data=json.dumps({"message": "leave"}))


class LogsConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'logs_%s' % self.room_name

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
        log = text_data_json['log']
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'log_message',
                "message": {
                    "log": log
                }
            }
        )

    # Receive message from room group
    def log_message(self, event):
        # Send message to WebSocket
        user = self.scope["user"]
        if user.user_type == "proctor":
            log = event['message']['log']
            # Send message to WebSocket
            self.send(text_data=json.dumps({
                'log': log
            }))


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

        print("Message sent to room")



    # Receive message from room group
    def chat_message(self, event):
        print(event)
        message = event['message']['content']
        username = event['message']['username']
        if User.objects.get(username=username).user_type=="proctor":
            username="Proctor"
        code = event['message']['code']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'code': code,
        }))
