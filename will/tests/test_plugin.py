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


def test__prepared_content(plugin, content):
    assert plugin._prepared_content(
        content, "", "") == re.sub(r'>\s+<', '><', content)


def test__trim_for_execution_has_analysis_attribute(plugin, message, analysis):
    m = message({"analysis": analysis})
    assert plugin._trim_for_execution(m) == m


def test__trim_for_execution_has_analysis_attribute_in_source_message(plugin, message, analysis):
    m = message({"source_message": {"analysis": analysis}})
    assert plugin._trim_for_execution(m) == m


def test_get_backend_has_backend_atrribute(plugin, message, io_backend):
    m = message({"backend": io_backend})
    assert plugin.get_backend(m) == m.backend


def test_get_backend_message_has_backend_atrribute_in_data(plugin, message, io_backend):
    m = message({"data": message({"backend": io_backend})})
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
def test_say_package_for_scheduling_is_true(plugin, content, message, event, io_backend):
    original_message = message({"backend": io_backend})
    backend = plugin.get_backend(original_message, None)
    e = event({'type': "say",
               'content': content,
               'source_message': original_message,
               'kwargs': {}})
    # Package plugin.say in a tuple to be able to make an assertion
    plugin_say = (plugin.say(content, message=original_message, package_for_scheduling=True))
    assert plugin_say == ("message.outgoing.%s" % backend, e)


@freeze_time(WILLS_BIRTHDAY)
def test_reply_package_for_scheduling_is_true(plugin, content, message, event, io_backend):
    original_message = message({"backend": io_backend})
    incoming_event = event({"data": original_message})
    backend = plugin.get_backend(original_message, None)
    e = event({'type': "reply",
               'content': content,
               'topic': "message.outgoing.%s" % backend,
               'source_message': original_message,
               'kwargs': {}})
    plugin_reply = plugin.reply(incoming_event, content, package_for_scheduling=True)
    assert plugin_reply == e
