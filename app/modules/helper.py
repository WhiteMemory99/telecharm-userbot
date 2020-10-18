import sys


def extract_entity_text(text: str, offset: int, length: int):
    """
    Get value of entity
    :param text: Full message text
    :param offset: Entity offset
    :param length: Entity length
    :return: Returns required part of the text
    """
    if sys.maxunicode == 0xffff:
        return text[offset:offset + length]

    entity_text = text.encode('utf-16-le')
    entity_text = entity_text[offset * 2:(offset + length) * 2]
    return entity_text.decode('utf-16-le')
