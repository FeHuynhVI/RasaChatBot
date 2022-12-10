from __future__ import annotations
import os
from underthesea import word_tokenize
from underthesea import pos_tag
from underthesea import word_tokenize
from underthesea import sent_tokenize
from underthesea import text_normalize
from rasa.nlu.constants import TOKENS_NAMES, MESSAGE_ATTRIBUTES

import re
from typing import Any, Dict, List, Text
from rasa.nlu.tokenizers.tokenizer import Token, Tokenizer
from rasa.shared.nlu.training_data.message import Message

from rasa.nlu.constants import TOKENS_NAMES, MESSAGE_ATTRIBUTES

from typing import Any, Dict, List, Optional, Text

import regex

import rasa.shared.utils.io
import rasa.utils.io
from rasa.engine.recipes.default_recipe import DefaultV1Recipe

from typing import Any, Dict, List, Optional, Text

PATH_STOP_WORD = "/home/ninepoints/Documents/RiN/rasa/RasaChatBot/customs/stopwords.txt"


@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER, is_trainable=False
)
class VietnameseTokenizer(Tokenizer):
    """Creates features for entity extraction."""

    @staticmethod
    def not_supported_languages() -> Optional[List[Text]]:
        """The languages that are not supported."""
        return ["zh", "ja", "th"]

    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        """Returns the component's default config."""
        return {
            # Flag to check whether to split intents
            "intent_tokenization_flag": False,
            # Symbol on which intent should be split
            "intent_split_symbol": "_",
            # Regular expression to detect tokens
            "token_pattern": None,
        }

    def __init__(self, config: Dict[Text, Any]) -> None:
        """Initialize the tokenizer."""
        super().__init__(config)
        self.emoji_pattern = rasa.utils.io.get_emoji_regex()

        if "case_sensitive" in self._config:
            rasa.shared.utils.io.raise_warning(
                "The option 'case_sensitive' was moved from the tokenizers to the "
                "featurizers.",
                docs=DOCS_URL_COMPONENTS,
            )

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> VietnameseTokenizer:
        """Creates a new component (see parent class for full docstring)."""
        # Path to the dictionaries on the local filesystem.
        return cls(config)

    def remove_emoji(self, text: Text) -> Text:
        """Remove emoji if the full text, aka token, matches the emoji regex."""
        match = self.emoji_pattern.fullmatch(text)

        if match is not None:
            return ""

        return text

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)

        text = text_normalize(text)

        # remove 'not a word character' if
        text = regex.sub(
            # there is a space or an end of a string after it
            r"[^\w#@&]+(?=\s|$)|"
            # there is a space or beginning of a string before it
            # not followed by a number
            r"(\s|^)[^\w#@&]+(?=[^0-9\s])|"
            # not in between numbers and not . or @ or & or - or #
            # e.g. 10'000.00 or blabla@gmail.com
            # and not url characters
            r"(?<=[^0-9\s])[^\w._~:/?#\[\]()@!$&*+,;=-]+(?=[^0-9\s])",
            " ",
            text,
        )

        words = word_tokenize(text)

        words = [w.strip() for w in words if w]

        wordsRemoveEmojiGlobal = []

        for word in words:
            wordsRemoveEmojiLocal = []
            for oneWord in word.split(" "):
                removes = self.remove_emoji(oneWord)
                if removes:
                    wordsRemoveEmojiLocal.append(removes)
            if len(wordsRemoveEmojiLocal) > 0:
                wordsRemoveEmojiGlobal.append(" ".join(wordsRemoveEmojiLocal).strip())

        stopwords = set(open(PATH_STOP_WORD, encoding="utf8").read().split(' ')[:-1])

        words = [w for w in wordsRemoveEmojiGlobal if w not in stopwords]

        tokens = self._convert_words_to_tokens(words, text)

        return self._apply_token_pattern(tokens)
