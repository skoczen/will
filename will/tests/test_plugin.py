import re
from datetime import datetime

import pytest
from freezegun import freeze_time

from const import WILLS_BIRTHDAY
from will import settings
from will.plugin import WillPlugin


@pytest.fixture
def plugin(mocker):
    mocker.patch.object(WillPlugin, "publish", return_value=None)
    return WillPlugin()


@pytest.fixture
def content():
    return "This is a test content"


@pytest.fixture
def backend_message(message, io_backend):
    return message({"backend": io_backend})


@pytest.fixture
@freeze_time(WILLS_BIRTHDAY)
def say_event(event, content, backend_message):
    return event({
        'type': "say",
        'content': content,
        'source_message': backend_message,
        'kwargs': {}
    })


@pytest.fixture
@freeze_time(WILLS_BIRTHDAY)
def reply_event(plugin, event, content, backend_message):
    backend = plugin.get_backend(backend_message, None)

    return backend, event({
        'type': "reply",
        'content': content,
        'topic': "message.outgoing.{}".format(backend),
        'source_message': backend_message,
        'kwargs': {}
    })


@pytest.fixture
@freeze_time(WILLS_BIRTHDAY)
def topic_event(plugin, event, content, backend_message):
    backend = plugin.get_backend(backend_message, None)

    return backend, event({
        'type': "topic_change",
        'content': content,
        'topic': "message.outgoing.{}".format(backend),
        'source_message': backend_message,
        'kwargs': {}
    })


def test__prepared_content(plugin, content):
    assert plugin._prepared_content(content, "",
                                    "") == re.sub(r'>\s+<', '><', content)


def test__trim_for_execution_has_analysis_attribute(plugin, message, analysis):
    m = message({"analysis": analysis})
    assert plugin._trim_for_execution(m) == m


def test__trim_for_execution_has_analysis_attribute_in_source_message(plugin, message, analysis):
    m = message({"source_message": {"analysis": analysis}})
    assert plugin._trim_for_execution(m) == m


def test_get_backend_has_backend_atrribute(plugin, backend_message):
    assert plugin.get_backend(backend_message) == backend_message.backend


def test_get_backend_message_has_backend_atrribute_in_data(plugin, message, backend_message):
    m = message({"data": backend_message})
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
def test_say_package_for_scheduling_is_true(plugin, content, say_event, backend_message):
    backend = plugin.get_backend(backend_message, None)
    topic, event = plugin.say(content,
                              message=backend_message,
                              package_for_scheduling=True)
    assert topic == "message.outgoing.%s" % backend
    assert event == say_event


@freeze_time(WILLS_BIRTHDAY)
def test_say_package_for_scheduling_is_false(plugin, content, backend_message, say_event):
    backend = plugin.get_backend(backend_message, None)
    plugin.say(content, message=backend_message, package_for_scheduling=False)
    plugin.publish.assert_called_once_with("message.outgoing.%s" % backend,
                                           say_event)


@freeze_time(WILLS_BIRTHDAY)
def test_reply_package_for_scheduling_is_true(plugin, content, event, reply_event, backend_message):
    incoming_event = event({"data": backend_message})
    plugin_reply = plugin.reply(incoming_event,
                                content,
                                package_for_scheduling=True)
    _, event = reply_event
    assert plugin_reply == event


@freeze_time(WILLS_BIRTHDAY)
def test_reply_package_for_scheduling_is_false(plugin, content, event, reply_event, backend_message):
    incoming_event = event({"data": backend_message})
    plugin.reply(incoming_event, content, package_for_scheduling=False)
    backend, event = reply_event
    plugin.publish.assert_called_once_with("message.outgoing.%s" % backend, event)


@freeze_time(WILLS_BIRTHDAY)
def test_set_topic(plugin, content, topic_event, backend_message):
    plugin.set_topic(content, message=backend_message)
    backend, event = topic_event
    plugin.publish.assert_called_once_with("message.outgoing.%s" % backend, event)


@freeze_time(WILLS_BIRTHDAY)
def test_schedule_say(mocker, plugin, content, backend_message):
    mocker.patch.object(plugin,
                        "add_outgoing_event_to_schedule",
                        return_value=None)
    when = datetime.now()
    topic, event = plugin.say(content,
                              message=backend_message,
                              package_for_scheduling=True)
    plugin.schedule_say(content, when, message=backend_message)
    plugin.add_outgoing_event_to_schedule.assert_called_once_with(
        when, {
            "type": "message",
            "topic": topic,
            "event": event
        })
