import ctypes
import json
import html2text
import logging
import pprint
import random
import requests
import sys
import time
import traceback

from DDPClient import DDPClient
from multiprocessing import Manager
from multiprocessing.dummy import Process
from six.moves.urllib import parse

from will import settings
from will.utils import Bunch, UNSURE_REPLIES, clean_for_pickling
from will.abstractions import Event, Message, Person, Channel
from .base import IOBackend


class RocketChatBackend(IOBackend):
    friendly_name = "RocketChat (BETA)"
    internal_name = "will.backends.io_adapters.rocketchat"
    required_settings = [
        {
            "name": "ROCKETCHAT_USERNAME",
            "obtain_at": "Will username as configured in Rocket.Chat.",
        },
        {
            "name": "ROCKETCHAT_PASSWORD",
            "obtain_at": "Will password as configured in Rocket.Chat.",
        },
        {
            "name": "ROCKETCHAT__URL",
            "obtain_at": (
                "Including protocol and port if not 80 e.g. "
                "http://localhost:3000"
            ),
        },
        {
            "name": "ROCKETCHAT_HANDLE",
            "obtain_at": (
                "Will's mention name in Rocket.chat, e.g. @will is 'will'"
            ),
        },
    ]

    pp = pprint.PrettyPrinter(indent=4)

    def __init__(self):

        self.rcapi = settings.ROCKETCHAT_URL + '/api/v1/'
        self.subscribed_rooms = {}

        # Set up Values to be shared by Processes
        self.manager = Manager()
        self.token = self.manager.Value(ctypes.c_char_p, '')
        self.userid = self.manager.Value(ctypes.c_char_p, '')

    def normalize_incoming_event(self, event):
        logging.info('Normalizing incoming Rocket.Chat event')
        logging.debug('event: {}'.format(self.pp.pformat(event)))
        if event["type"] == "message":

            # Were we mentioned?
            will_is_mentioned = False
            for mention in event['mentions']:
                if mention['username'] == self.me.handle:
                    will_is_mentioned = True
                    break

            # Handle direct messages, which in Rocket.Chat are a rid
            # made up of both users' _ids.
            is_private_chat = False
            if self.me.id in event["rid"]:
                is_private_chat = True

                # Create a "Channel" to align with Rocket.Chat DM
                # paradigm. There might well be a better way of doing
                # this. See TODO in _rest_channels_list.
                sender_id = event['u']['_id']
                ids = [sender_id, self.me.id]
                ids.sort()
                channel_id = '{}{}'.format(*ids)
                sender = self.people[sender_id]
                channel_members = {}
                channel_members[sender_id] = sender
                channel_members[self.me.id] = self.me
                channel = Channel(
                    id=channel_id,
                    name=channel_id,
                    source=clean_for_pickling(channel_id),
                    members=channel_members
                )
            else:
                channel = clean_for_pickling(self.channels[event["rid"]])
            logging.debug('channel: {}'.format(channel))

            # Set various variables depending on whether @handle was
            # part of the message.
            interpolated_handle = "@%s " % self.handle
            logging.debug('interpolated_handle: {}'
                          .format(interpolated_handle))
            is_direct = False
            if is_private_chat or event['msg'].startswith(interpolated_handle):
                is_direct = True

            # Strip my handle from the start. NB Won't strip it from
            # elsewhere in the text, and won't strip other mentions.
            # This will stop regexes from working, not sure if it's a
            # feature or a bug.
            if event['msg'].startswith(interpolated_handle):
                event['msg'] = event['msg'][len(interpolated_handle):].strip()

            if interpolated_handle in event['msg']:
                will_is_mentioned = True

            # Determine if Will said it.
            logging.debug('self.people: {}'.format(self.pp.pformat(self.people)))
            sender = self.people[event['u']['_id']]
            logging.debug('sender: {}'.format(sender))
            if sender['handle'] == self.me.handle:
                logging.debug('Will said it')
                will_said_it = True
            else:
                logging.debug('Will didnt say it')
                will_said_it = False

            m = Message(
                content=event['msg'],
                type=event.type,
                is_direct=is_direct,
                is_private_chat=is_private_chat,
                is_group_chat=not is_private_chat,
                backend=self.internal_name,
                sender=sender,
                channel=channel,
                will_is_mentioned=will_is_mentioned,
                will_said_it=will_said_it,
                backend_supports_acl=True,
                source=clean_for_pickling(event)
            )
            return m
        else:
            logging.debug('Passing, I dont know how to normalize this event of type ', event["type"])
            pass

    # This and send_message heavily "inspired" by slack.py. Technical
    # debt may be present. :)
    def handle_outgoing_event(self, event):
        # Print any replies.
        logging.info('Handling outgoing Rocket.Chat event')
        logging.debug('event: {}'.format(self.pp.pformat(event)))

        if event.type in ["say", "reply"]:

            if "kwargs" in event and "html" in event.kwargs and event.kwargs["html"]:
                event.content = html2text.html2text(event.content)

            if hasattr(event, "source_message") and event.source_message:
                self.send_message(event)
            else:
                # TODO: Rocket.Chat backend needs to provide ways to handle and properly route:
                # 1. 1-1 messages
                # 2. Group (channel) messages
                # 3. Ad-hoc group messages (if they exist)
                # 4. Messages that have a channel/room explicitly specified that's different than
                #    where they came from.
                # 5. Messages without a channel (Fallback to ROCKETCHAT_DEFAULT_CHANNEL) (messages that don't have a room )
                kwargs = {}
                if "kwargs" in event:
                    kwargs.update(**event.kwargs)

        if event.type in ["topic_change", ]:
            self.set_room_topic(event.content)
        elif (
            event.type == "message.no_response" and
            event.data["source"].data.is_direct and
            event.data["source"].data.will_said_it is False
        ):
            event.content = random.choice(UNSURE_REPLIES)
            self.send_message(event)

    def set_topic(self, event):
        logging.warn("Rocket.Chat doesn't support topics yet: https://github.com/RocketChat/Rocket.Chat/issues/328")

    def send_message(self, event):
        logging.info('Sending message to Rocket.Chat')
        logging.debug('event: {}'.format(self.pp.pformat(event)))
        data = {}
        if hasattr(event, "kwargs"):
            logging.debug('event.kwargs: {}'.format(event.kwargs))
            data.update(event.kwargs)

            # TODO: Go through the possible attachment parameters at
            # https://rocket.chat/docs/developer-guides/rest-api/chat/postmessage
            # - this is a bare minimum inspired by slack.py
            if 'color' in event.kwargs:
                data.update({
                    "attachments": [
                        {
                            'color': event.kwargs["color"],
                            'text': event.content,
                        }
                    ],
                })
            else:
                data.update({
                    'text': event.content,
                })
        else:
            # I haven't seen this yet, not sure when it's relevant.
            # 'text' was wrongly set to 'msg' and nothing blew up. ;)
            logging.debug("event doesn't have kwargs")
            data.update({
                'text': event.content,
            })

        if "source_message" in event:
            if hasattr(event.source_message, "data"):
                data['roomId'] = event.source_message.data.channel.id
            else:
                data['roomId'] = event.source_message.channel.id
        else:
            data['roomId'] = event.data['source'].data.channel.id

        self._rest_post_message(data)

    def _get_rest_metadata(self):
        self._rest_users_list()
        self._rest_channels_list()

    def _get_realtime_metadata(self):
        self._realtime_get_rooms()

    # REST API functions, documented at
    # https://rocket.chat/docs/developer-guides/rest-api/

    def _rest_login(self):
        params = {'username': settings.ROCKETCHAT_USERNAME,
                  'password': settings.ROCKETCHAT_PASSWORD}
        r = requests.post('{}login'.format(self.rcapi),
                          data=params)
        rj = r.json()
        self.token.value = rj['data']['authToken']
        self.userid.value = rj['data']['userId']

    def _rest_users_list(self):
        logging.debug('Getting users list from Rocket.Chat')

        # Remember to paginate. ;)
        count = 50
        passes = 0
        headers = {'X-Auth-Token': self.token.value,
                   'X-User-Id': self.userid.value}
        fetched = 0
        total = 0

        self.handle = settings.ROCKETCHAT_HANDLE
        self.mention_handle = "@%s" % settings.ROCKETCHAT_HANDLE

        people = {}

        while fetched <= total:
            params = {'count': count,
                      'offset': fetched}
            r = requests.get('{}users.list'.format(self.rcapi),
                             headers=headers,
                             params=params)
            rj = r.json()
            if rj['success'] is False:
                logging.exception('rj: {}'.format(rj))
            total = rj['total']

            for user in rj['users']:
                # TODO: Unlike slack.py, no timezone support at present.
                # RC returns utcOffset, but this isn't enough to
                # determine timezone.
                # TODO: Pickle error if timezone set to UTC, and I didn't
                # have a chance to report it. Using GMT as a poor substitute.
                person = Person(
                    id=user['_id'],
                    handle=user['username'],
                    mention_handle="@%s" % user["username"],
                    source=clean_for_pickling(user)['username'],
                    name=user['name'],
                    timezone='GMT'
                )

                people[user['_id']] = person
                if user['username'] == self.handle:
                    self.me = person

            passes += 1
            fetched = count * passes

        self.people = people

    def _get_userid_from_username(self, username):
        if username is None:
            raise TypeError("No username given")

        for id, data in self.people.iteritems():
            if data['handle'] == username:
                return id

    def _rest_channels_list(self):
        logging.debug('Getting channel list from Rocket.Chat')

        # Remember to paginate. ;)
        count = 50
        passes = 0
        headers = {'X-Auth-Token': self.token.value,
                   'X-User-Id': self.userid.value}
        fetched = 0
        total = 0

        channels = {}

        while fetched <= total:
            r = requests.get('{}channels.list'.format(self.rcapi),
                             headers=headers)
            rj = r.json()

            total = rj['total']

            for channel in rj['channels']:
                members = {}
                for username in channel['usernames']:
                    userid = self._get_userid_from_username(username)
                    members[userid] = self.people[userid]

                channels[channel['_id']] = Channel(
                    id=channel['_id'],
                    name=channel['name'],
                    source=clean_for_pickling(channel),
                    members=members
                )

            passes += 1
            fetched = count * passes

        self.channels = channels

    def _rest_post_message(self, data):
        logging.info('Posting message to Rocket.Chat REST API')
        logging.debug('data: {}'.format(data))
        headers = {'X-Auth-Token': self.token.value,
                   'X-User-Id': self.userid.value}
        logging.debug('headers: {}'.format(headers))
        r = requests.post('{}chat.postMessage'.format(self.rcapi),
                          headers=headers,
                          json=data,
                          **settings.REQUESTS_OPTIONS)
        rj = r.json()
        # TODO: Necessary / useful to check return codes?
        if not 'success' in rj:
            logging.debug('rj: {}'.format(rj))
            assert rj['success']

    # Realtime API functions, documented at
    # https://rocket.chat/docs/developer-guides/realtime-api/

    def _realtime_connect(self):
        # TODO: Consider using auto_reconnect and debug options.
        up = parse.urlparse(settings.ROCKETCHAT_URL)
        if up.scheme == 'http':
            ws_proto = 'ws'
        else:
            ws_proto = 'wss'
        self.rc = DDPClient('{}://{}/websocket'.format(ws_proto, up.netloc))
        self.rc.connect()
        # TODO: Argh. This needs to be here because if we continue
        # before the connection is ready, stuff fails with no errors
        # to the console. This will take some debug effort.
        time.sleep(5)

    def _realtime_login(self):
        params = [{'user': {'username': settings.ROCKETCHAT_USERNAME}, 'password': settings.ROCKETCHAT_PASSWORD}]
        self.rc.call('login', params, self._login_callback)

    def _login_callback(self, error, result):
        logging.debug('_login_callback')
        if error:
            logging.exception('error: {}'.format(error))
            return

        logging.debug('result: {}'.format(result))

        self.token.value = result['token']
        self.userid.value = result['id']

        logging.debug('self.token.value: {}'.format(self.token.value))
        logging.debug('self.userid.value: {}'.format(self.userid.value))

        # Use dummy to make it a Thread, otherwise DDP events don't
        # get back to the right place. If there is a real need to make
        # it a real Process, it is probably just a matter of using
        # multiprocessing.Value(s) in the right place(s).
        # TODO: Could this be the reason for the 100% CPU usage?
        # Have asked in #development.
        self.update_thread = Process(target=self._get_updates)
        self.update_thread.start()

    def _changed_callback(self, collection, _id, fields, cleared):
        logging.debug('_changed_callback')
        logging.debug('collection: {}'.format(collection))
        logging.debug('id: {}'.format(_id))
        logging.debug('fields: {}'.format(self.pp.pformat(fields)))
        logging.debug('cleared: {}'.format(cleared))
        event = Event(type='message', version=1, **fields['args'][0])
        self.handle_incoming_event(event)

    def _stream_room_message_callback(self, error, event):
        logging.debug('_stream_room_message_callback')
        if error:
            logging.exception('error: {}'.format(error))
            return

    # Gets updates from REST and Realtime APIs.
    def _get_updates(self):
        try:
            polling_interval_seconds = 5
            self.rc.on('changed', self._changed_callback)
            self._get_rest_metadata()

            while True:
                # Update channels/people/me/etc.
                self._get_rest_metadata()
                self._get_realtime_metadata()

                time.sleep(polling_interval_seconds)
        except (KeyboardInterrupt, SystemExit):
            pass
        except:
            logging.critical("Error in watching RocketChat API: \n%s" % traceback.format_exc())

    # Use this to get a list of all rooms that we are in.
    # https://rocket.chat/docs/developer-guides/realtime-api/the-room-object
    def _realtime_get_rooms(self):
        params = [{'$date': 0}]
        self.rc.call('rooms/get', params, self._get_rooms_callback)

    def _get_rooms_callback(self, error, result):
        logging.debug('_get_rooms_callback')
        if error:
            logging.exception('_get_rooms_callback error: {}'.format(error))
            return

        # TODO: When we leave a room, we don't delete it from
        # self.subscribed_rooms. Not a problem in practice -
        # subscriptions to the room won't fire, but messy.
        for room in result:
            logging.debug('room: {}'.format(room))
            if room['_id'] not in self.subscribed_rooms:
                self.rc.subscribe('stream-room-messages', [room['_id']],
                                  self._stream_room_message_callback)
            self.subscribed_rooms[room['_id']] = True

    def bootstrap(self):
        # Bootstrap must provide a way to to have:
        # a) self.normalize_incoming_event fired, or incoming events put into self.incoming_queue
        # b) any necessary threads running for a)
        # c) self.me (Person) defined, with Will's info
        # d) self.people (dict of People) defined, with everyone in an organization/backend
        # e) self.channels (dict of Channels) defined, with all available channels/rooms.
        #    Note that Channel asks for users, a list of People.
        # f) A way for self.handle, self.me, self.people, and self.channels to be kept accurate,
        #    with a maximum lag of 60 seconds.

        self._realtime_connect()
        self._realtime_login()
