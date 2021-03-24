import re
from datetime import datetime

import pytest
from freezegun import freeze_time

from const import WILLS_BIRTHDAY
from will import settings
from will.plugin import WillPlugin


@pytest.fixture
def plugin(mocker):
    """Initialize plugin module and mock methods"""
    mocker.patch.object(WillPlugin, "publish", return_value=None)
    mocker.patch.object(WillPlugin, "add_outgoing_event_to_schedule",
                        return_value=None)
    return WillPlugin()


@pytest.fixture
def content():
    """Response to be shown on the io_backend"""
    return "This is a test content"


@pytest.fixture
def source_message(message, io_backend):
    """Message comming from an io_backend"""
    return message({"backend": io_backend})


@pytest.fixture
def outgoing_topic(plugin, source_message):
    """Topic with which an event is published"""
    backend = plugin.get_backend(source_message, None)
    return "message.outgoing.{}".format(backend)


@pytest.fixture
@freeze_time(WILLS_BIRTHDAY)
def say_event(event, content, source_message):
    """Mimics an event abstraction for say method"""
    return event({
        'type': "say",
        'content': content,
        'source_message': source_message,
        'kwargs': {}
    })


@pytest.fixture
@freeze_time(WILLS_BIRTHDAY)
def reply_event(plugin, event, content, source_message, outgoing_topic):
    """Mimics an event abstraction for reply method"""

    return event({
        'type': "reply",
        'content': content,
        'topic': outgoing_topic,
        'source_message': source_message,
        'kwargs': {}
    })


@pytest.fixture
@freeze_time(WILLS_BIRTHDAY)
def topic_event(plugin, event, content, outgoing_topic, source_message):
    """Mimics an event abstraction for set_topic method"""

    return event({
        'type': "topic_change",
        'content': content,
        'topic': outgoing_topic,
        'source_message': source_message,
        'kwargs': {}
    })


def test__init__():
    kwargs = {"bot": "test"}
    plugin = WillPlugin(**kwargs)
    assert plugin.bot == "test"


def test__prepared_content(plugin, content):
    assert plugin._prepared_content(content, "",
                                    "") == re.sub(r'>\s+<', '><', content)


def test__trim_for_execution_has_analysis_attribute(plugin, message, analysis):
    m = message({"analysis": analysis})
    assert plugin._trim_for_execution(m) == m


def test__trim_for_execution_has_analysis_attribute_in_source_message(plugin, message, analysis):
    m = message({"source_message": message({"analysis": analysis})})
    assert plugin._trim_for_execution(m) == m


def test_get_backend_has_backend_atrribute(plugin, source_message):
    assert plugin.get_backend(source_message) == source_message.backend


def test_get_backend_message_has_backend_atrribute_in_data(plugin, message, source_message):
    m = message({"data": source_message})
    del m.backend
    assert plugin.get_backend(m) == m.data.backend


def test_get_backend_message_no_backend_or_data_attruibute(plugin, message, io_backend):
    settings.DEFAULT_BACKEND = io_backend
    m = message({})
    del m.backend
    assert plugin.get_backend(m) == settings.DEFAULT_BACKEND


def test_get_message_no_message_passed():
    message = {"message": "This is a test"}
    plugin = WillPlugin(**message)
    assert plugin.get_message(None) == plugin.message


def test_get_message_message_passed_as_parameter(plugin, message):
    m = message({})
    assert plugin.get_message(m) == m


def test_get_backend_service_as_parameter(message, plugin, io_backend, all_io_backends):
    m = message({})
    service = io_backend
    settings.IO_BACKENDS = all_io_backends
    assert plugin.get_backend(m, service) == service

# freeze_time to mock datetime.datetime.now() method which is invoked
# when creating an event or message.
# https://github.com/spulec/freezegun


@freeze_time(WILLS_BIRTHDAY)
def test_say_with_room_arg(plugin, content, say_event, source_message, outgoing_topic):
    room = "test"
    plugin.say(content, message=source_message, room=room)
    say_event.kwargs["channel"] = room
    plugin.publish.assert_called_once_with(outgoing_topic, say_event)


@freeze_time(WILLS_BIRTHDAY)
def test_say_with_channel_arg(plugin, content, say_event, source_message, outgoing_topic):
    channel = "test"
    plugin.say(content, message=source_message, channel=channel)
    say_event.kwargs["channel"] = channel
    plugin.publish.assert_called_once_with(outgoing_topic,
                                           say_event)


@freeze_time(WILLS_BIRTHDAY)
def test_say_package_for_scheduling_is_true(plugin, content, say_event,
                                            outgoing_topic, source_message):
    topic, event = plugin.say(content,
                              message=source_message,
                              package_for_scheduling=True)
    assert topic == outgoing_topic
    assert event == say_event


@freeze_time(WILLS_BIRTHDAY)
def test_say_package_for_scheduling_is_false(plugin, content, source_message,
                                             outgoing_topic, say_event):
    plugin.say(content, message=source_message, package_for_scheduling=False)
    plugin.publish.assert_called_once_with(outgoing_topic, say_event)


@freeze_time(WILLS_BIRTHDAY)
def test_reply_package_for_scheduling_is_true(plugin, content, event,
                                              reply_event, source_message):
    incoming_event = event({"data": source_message})
    plugin_reply = plugin.reply(incoming_event,
                                content,
                                package_for_scheduling=True)
    assert plugin_reply == reply_event


@freeze_time(WILLS_BIRTHDAY)
def test_reply_package_for_scheduling_is_false(plugin, content, event,
                                               reply_event, outgoing_topic,
                                               source_message):
    incoming_event = event({"data": source_message})
    plugin.reply(incoming_event, content, package_for_scheduling=False)
    plugin.publish.assert_called_once_with(outgoing_topic, reply_event)


@freeze_time(WILLS_BIRTHDAY)
def test_reply_event_has_words_and_no_content(plugin, content, event, reply_event,
                                              source_message, outgoing_topic):
    incoming_event = event({"data": source_message})
    plugin.message = incoming_event
    plugin.reply(event=content)
    plugin.publish.assert_called_once_with(outgoing_topic, reply_event)


@freeze_time(WILLS_BIRTHDAY)
def test_reply_event_and_content_passed_backwards(plugin, reply_event, content,
                                                  event, source_message,
                                                  outgoing_topic):
    incoming_event = event({"data": source_message})
    plugin.reply(event=content, content=incoming_event)
    plugin.publish.assert_called_once_with(outgoing_topic, reply_event)


@freeze_time(WILLS_BIRTHDAY)
def test_reply_message_has_data(plugin, content, event, reply_event,
                                source_message, outgoing_topic):
    incoming_event = event({"data": source_message})
    plugin.message = incoming_event
    plugin.reply(event=content, content=content)
    plugin.publish.assert_called_once_with(outgoing_topic, reply_event)


def test_reply_channel_in_kwargs(plugin, event, content, source_message):
    incoming_event = event({"data": source_message})
    reply = plugin.reply(incoming_event, content, channel="test")
    assert reply is None


def test_reply_service_in_kwargs(plugin, event, content, source_message):
    incoming_event = event({"data": source_message})
    reply = plugin.reply(incoming_event, content, service="test")
    assert reply is None


def test_reply_room_in_kwargs(plugin, event, content, source_message):
    incoming_event = event({"data": source_message})
    reply = plugin.reply(incoming_event, content, room="test")
    assert reply is None


@freeze_time(WILLS_BIRTHDAY)
def test_set_topic(plugin, content, topic_event, source_message, outgoing_topic):
    plugin.set_topic(content, message=source_message)
    plugin.publish.assert_called_once_with(outgoing_topic,
                                           topic_event)


@freeze_time(WILLS_BIRTHDAY)
def test_set_topic_with_room_arg(plugin, content, topic_event, source_message,
                                 outgoing_topic):
    room = "test"
    plugin.set_topic(content, message=source_message, room=room)
    plugin.publish.assert_called_once_with(outgoing_topic,
                                           topic_event)


@freeze_time(WILLS_BIRTHDAY)
def test_set_topic_with_channel_arg(plugin, content, topic_event, source_message,
                                    outgoing_topic):
    channel = "test"
    plugin.set_topic(content, message=source_message, channel=channel)
    plugin.publish.assert_called_once_with(outgoing_topic, topic_event)


@freeze_time(WILLS_BIRTHDAY)
def test_schedule_say(plugin, content, source_message):
    when = datetime.now()
    topic, event = plugin.say(content,
                              message=source_message,
                              package_for_scheduling=True)
    plugin.schedule_say(content, when, message=source_message)
    plugin.add_outgoing_event_to_schedule.assert_called_once_with(
        when, {
            "type": "message",
            "topic": topic,
            "event": event
        })


@freeze_time(WILLS_BIRTHDAY)
def test_schedule_say_with_room_arg(plugin, content, source_message):
    room = "test"
    when = datetime.now()
    topic, event = plugin.say(content, message=source_message, package_for_scheduling=True)
    event.kwargs["channel"] = room
    plugin.schedule_say(content, when, message=source_message, room=room)
    plugin.add_outgoing_event_to_schedule.assert_called_once_with(
        when, {"type": "message", "topic": topic, "event": event}
    )


@freeze_time(WILLS_BIRTHDAY)
def test_schedule_say_with_channel_arg(plugin, content, source_message):
    channel = "test"
    when = datetime.now()
    topic, event = plugin.say(content,
                              message=source_message,
                              package_for_scheduling=True)
    event.kwargs["channel"] = channel
    plugin.schedule_say(content, when, message=source_message, channel=channel)
    plugin.add_outgoing_event_to_schedule.assert_called_once_with(
        when, {
            "type": "message",
            "topic": topic,
            "event": event
        })
