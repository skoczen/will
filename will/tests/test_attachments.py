import pytest
from will.abstractions import Attachment
from will.backends.io_adapters.slack import SlackAttachmentConverter, SlackBackend


def test_no_fallback():
    with pytest.raises(Exception):
        Attachment(text="Test Text")


def test_no_text():
    with pytest.raises(Exception):
        Attachment(fallback="Test Text")


def test_no_footer():
    attachment = Attachment(fallback="Test Fallback",
                            text="Test Text")
    assert attachment.footer == "Will"


def test_custom_footer():
    attachment = Attachment(fallback="Test Fallback",
                            text="Test Text", footer="My Awesome Bot")
    assert attachment.footer == "My Awesome Bot"


def test_no_footer_icon():
    attachment = Attachment(fallback="Test Fallback",
                            text="Test Text")
    assert attachment.footer_icon == "http://heywill.io/img/favicon.png"


def test_custoom_footer_icon():
    attachment = Attachment(fallback="Test Fallback",
                            text="Test Text", footer_icon="https://picture.png")
    assert attachment.footer_icon == "https://picture.png"


def test_button_on_create():
    attachment = Attachment(fallback="Test Fallback",
                            text="Test Text",
                            button_text="Test Button",
                            button_url="google.com")
    assert attachment.button_url == "google.com"
    assert attachment.button_text == "Test Button"


def test_custom_color_button_on_create():
    attachment = Attachment(fallback="Test Fallback",
                            text="Test Text",
                            button_text="Test Button",
                            button_url="google.com",
                            button_color="#62f442")
    assert attachment.button_color == "#62f442"


def test_style_default():
    attachment = Attachment(fallback="Test Fallback",
                            text="Test Text")
    assert attachment.color == '#555555'
    assert attachment.button_color == '#555555'


def test_style_blue():
    attachment = Attachment(fallback="Test Fallback",
                            text="Test Text", style='blue')
    assert attachment.color == '#3B80C6'
    assert attachment.button_color == '#3B80C6'


def test_style_green():
    attachment = Attachment(fallback="Test Fallback",
                            text="Test Text", style='green')
    assert attachment.color == '#0e8a16'
    assert attachment.button_color == '#0e8a16'


def test_style_purple():
    attachment = Attachment(fallback="Test Fallback",
                            text="Test Text", style='purple')
    assert attachment.color == '#876096'
    assert attachment.button_color == '#876096'


def test_style_orange():
    attachment = Attachment(fallback="Test Fallback",
                            text="Test Text", style='orange')
    assert attachment.color == '#FB7642'
    assert attachment.button_color == '#FB7642'


def test_style_yellow():
    attachment = Attachment(fallback="Test Fallback",
                            text="Test Text", style='yellow')
    assert attachment.color == '#f4c551'
    assert attachment.button_color == '#f4c551'


def test_style_teal():
    attachment = Attachment(fallback="Test Fallback",
                            text="Test Text", style='teal')
    assert attachment.color == '#007AB8'
    assert attachment.button_color == '#007AB8'


def test_add_button():
    attachment = Attachment(fallback="Test Fallback",
                            text="Test Text")
    attachment.add_button(text="Button", url="https://google.com")
    assert attachment.actions == [{'color': '#555555', 'type': 'button', 'text': 'Button', 'url': 'https://google.com'}]


def test_add_two_buttons():
    attachment = Attachment(fallback="Test Fallback",
                            text="Test Text")
    attachment.add_button(text="Button", url="https://google.com")
    attachment.add_button(text="Open Maps", url="https://maps.google.com")
    assert attachment.actions == [{'color': '#555555', 'type': 'button', 'text': 'Button', 'url': 'https://google.com'},
                                  {'color': '#555555', 'type': 'button',
                                   'text': 'Open Maps', 'url': 'https://maps.google.com'}]


def test_txt():
    attachment = Attachment(fallback="Test Fallback",
                            text="Test Text",
                            style="yellow",
                            button_text="Open Database",
                            button_url="http://my.database.url")
    assert attachment.txt() == "Test Text http://my.database.url"


def test_slack_converter_single_attachment():
    attachment = Attachment(fallback="Test Fallback",
                            text="Test Text",
                            style="yellow",
                            button_text="Open Database",
                            button_url="http://my.database.url")

    assert SlackAttachmentConverter(attachment).render() == str([{'fallback': 'Test Fallback',
                                                                  'color': '#f4c551',
                                                                  'text': 'Test Text',
                                                                  'actions': [{'color': '#f4c551',
                                                                               'type': 'button',
                                                                               'text': 'Open Database',
                                                                               'url': 'http://my.database.url'}],
                                                                  'footer': 'Will',
                                                                  'footer_icon': 'http://heywill.io/img/favicon.png'}])


def test_slack_converter_list_attachments():
    x = ['Ron', 'Bill', 'Gina', 'Rachael']
    attachments = []
    payload = ""
    for i in x:
        attachments.append(Attachment(fallback='The name is %s' % i,
                                      style='yellow',
                                      text='The name is %s' % i,
                                      button_text='Open in database',
                                      button_url='https://my.database.url/people/v2/' + i))

    for a in attachments:
        payload += str(
            [
                {
                    "fallback": a.fallback,
                    "color": a.color,
                    "text": a.text,
                    "actions": a.actions,
                    "footer": a.footer,
                    "footer_icon": a.footer_icon,
                }
            ]
        )

    assert SlackAttachmentConverter(attachments).render() == payload
