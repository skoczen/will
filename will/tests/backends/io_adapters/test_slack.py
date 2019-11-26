from will.backends.io_adapters import slack


class TestSlackMarkdownConverter:
    converter = slack.SlackMarkdownConverter()

    def test_convert_strong_with_text(self):
        slack_strong = self.converter.convert_strong("<b>", "hello")
        assert slack_strong == "*hello*"

    def test_convert_strong_with_empty_text(self):
        slack_strong = self.converter.convert_strong("<b>", "")
        assert slack_strong == ""

    def test_convert_a_with_text(self):
        slack_a = self.converter.convert_a({"href": "https://www.google.com"},
                                           "Google")
        assert slack_a == "<https://www.google.com|Google>"

    def test_convert_a_with_text_same_as_href(self):
        slack_a = self.converter.convert_a({"href": "https://www.google.com"},
                                           "https://www.google.com")
        assert slack_a == "<https://www.google.com>"
