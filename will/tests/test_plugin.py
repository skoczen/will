import re

import pytest
from freezegun import freeze_time

from will import settings
from will.plugin import WillPlugin

from const import WILLS_BIRTHDAY


@pytest.fixture
def plugin():
    return WillPlugin()


@pytest.fixture
def content():
    return "This is a test content"


@pytest.fixture
def backend_message(message, io_backend):
    return message({"backend": io_backend})


def test__prepared_content(plugin, content):
    assert plugin._prepared_content(
        content, "", "") == re.sub(r'>\s+<', '><', content)


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
def test_say_package_for_scheduling_is_true(plugin, content, event, backend_message):
    backend = plugin.get_backend(backend_message, None)
    e = event({'type': "say",
               'content': content,
               'source_message': backend_message,
               'kwargs': {}})
    topic, event = plugin.say(content, message=backend_message, package_for_scheduling=True)
    assert topic == "message.outgoing.%s" % backend
    assert event == e


@freeze_time(WILLS_BIRTHDAY)
def test_say_package_for_scheduling_is_false(plugin, content, event, mocker, backend_message):
    backend = plugin.get_backend(backend_message, None)
    e = event({'type': "say",
               'content': content,
               'source_message': backend_message,
               'kwargs': {}})
    mocker.patch.object(WillPlugin, "publish", return_value=None)
    plugin.say(content, message=backend_message, package_for_scheduling=False)
    WillPlugin.publish.assert_called_once_with("message.outgoing.%s" % backend, e)

@freeze_time(WILLS_BIRTHDAY)
def test_reply_package_for_scheduling_is_true(plugin, content, event, backend_message):
    incoming_event = event({"data": backend_message})
    backend = plugin.get_backend(backend_message, None)
    e = event({'type': "reply",
               'content': content,
               'topic': "message.outgoing.{}".format(backend),
               'source_message': backend_message,
               'kwargs': {}})
    plugin_reply = plugin.reply(incoming_event, content, package_for_scheduling=True)
    assert plugin_reply == e
