import re

import MeCab
import jaconv


def add_furigana(sentence):
    tagger = MeCab.Tagger()
    node = tagger.parseToNode(sentence)

    output = ''
    while node:
        if node.surface != '':
            surface = node.surface
            features = node.feature.split(',')
            # Get the reading (pronunciation) in katakana
            if len(features) >= 8 and features[7] != '*':
                reading = features[7]
                # Convert katakana to hiragana
                hiragana = jaconv.kata2hira(reading)
            else:
                hiragana = ''
            # Check if the surface contains kanji
            if any('\u4e00' <= char <= '\u9fff' for char in surface):
                # Add furigana
                output += f'{surface}({hiragana})'
            else:
                output += surface
        node = node.next
    return output


parentheses_to_ruby_pattern = re.compile(r'([\u4e00-\u9fff]+)\((.*?)\)')


def parentheses_to_ruby(text):
    # Regular expression pattern to match kanji followed by furigana in parentheses
    def repl(match):
        kanji = match.group(1)
        furigana = match.group(2)
        return f'<ruby>{kanji}<rt>{furigana}</rt></ruby>'

    # Substitute all occurrences in the text
    return parentheses_to_ruby_pattern.sub(repl, text)
