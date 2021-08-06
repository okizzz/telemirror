import re


def check_list(letter_list: list, text: str):
    for letter in letter_list:
        if re.search(letter, text) is not None:
            return True
    return False


def replace_text(letter_list: list, text: str):
    for letter in letter_list:
        if 'from' in letter and 'to' in letter:
            text = re.sub(rf'\b\w*{letter["from"]}\w*\b', letter['to'], text)
    return text
