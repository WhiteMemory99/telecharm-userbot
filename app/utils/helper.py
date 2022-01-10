import html
import sys


def quote_html(text: str) -> str:
    """
    Escape unexpected HTML characters.

    :param text: Original text
    :return:
    """
    return html.escape(text, quote=False)


def extract_entity_text(text: str, offset: int, length: int) -> str:
    """
    Get entity value.

    :param text: Full message text
    :param offset: Entity offset
    :param length: Entity length
    :return: Returns required part of the text
    """
    if sys.maxunicode == 0xFFFF:
        return text[offset : offset + length]  # noqa

    entity_text = text.encode("utf-16-le")
    entity_text = entity_text[offset * 2 : (offset + length) * 2]  # noqa
    return entity_text.decode("utf-16-le")
