import datetime
import re

import pytest
from freezegun import freeze_time

from will import settings
from will.plugin import WillPlugin


@pytest.fixture
def plugin():
    return WillPlugin()


@pytest.fixture
def content():
    return "This is a test content"


def test__prepared_content(plugin, content):
    assert plugin._prepared_content(
        content, "", "") == re.sub(r'>\s+<', '><', content)


def test__trim_for_execution_has_analysis_attribute(plugin, message):
    m = message({"analysis": "some_analysis"})
    assert plugin._trim_for_execution(m) == m


def test__trim_for_execution_has_analysis_attribute_in_source_message(plugin, message):
    m = message({"source_message": {"analysis": "some_analysis"}})
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


@freeze_time("2012-01-14")
def test_say_package_for_scheduling_is_true(plugin, content, message, event, io_backend):
    original_message = message({"backend": io_backend})
    backend = plugin.get_backend(original_message, None)
    e = event(
        {'type': "say", 'content': content, 'source_message': original_message,
         'kwargs': {}})
    outgoing_message = "message.outgoing.%s" % backend
    # Package
    assert (plugin.say(
        content, message=original_message, package_for_scheduling=True)) == ("message.outgoing.%s" % backend, e)
