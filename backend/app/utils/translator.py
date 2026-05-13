from deep_translator import GoogleTranslator

LANGUAGE_MAP = {
    'en': 'en',
    'hi': 'hi',
    'mr': 'mr',
    'bn': 'bn',
    'ta': 'ta',
    'te': 'te',
    'fr': 'fr',
    'es': 'es',
    'de': 'de',
    'ar': 'ar',
    'zh': 'zh-CN',
    'zh-cn': 'zh-CN',
    'zh_cn': 'zh-CN',
    'ja': 'ja',
}

BASE_DUMMY_RESPONSE = '''Predicted Disease: Demo Disease
Description: This is a placeholder response until the ML model is connected.
Precautions:
- Drink water
- Take rest
- Consult doctor if symptoms worsen'''


class TranslationService:
    def __init__(self) -> None:
        self._fallback_responses = {
            'en': BASE_DUMMY_RESPONSE,
            'hi': (
                '??????? ??????: ???? ???\n'
                '?????: ?? ?? ??????? ????? ?? ?? ?? ???? ???? ????? ???? ?????\n'
                '??????????:\n'
                '- ???? ????\n'
                '- ???? ????\n'
                '- ????? ????? ?? ?????? ?? ?????? ????'
            ),
        }

    def normalize_language(self, language_code: str | None) -> str:
        if not language_code:
            return 'en'
        normalized = language_code.lower().strip()
        return LANGUAGE_MAP.get(normalized, 'en')

    def translate_text(self, text: str, target_language: str, source_language: str = 'auto') -> str:
        normalized_target = self.normalize_language(target_language)
        normalized_source = 'auto' if source_language == 'auto' else self.normalize_language(source_language)

        if not text.strip() or normalized_target == normalized_source:
            return text

        try:
            return GoogleTranslator(source=normalized_source, target=normalized_target).translate(text)
        except Exception as exc:
            print(f'Translation failed ({normalized_source} -> {normalized_target}): {exc}')
            return text

    def translate_to_english(self, text: str, source_language: str | None = None) -> str:
        normalized_source = self.normalize_language(source_language)
        if normalized_source == 'en':
            return text
        return self.translate_text(text, target_language='en', source_language='auto')

    def translate_from_english(self, text: str, target_language: str | None = None) -> str:
        normalized_target = self.normalize_language(target_language)
        if normalized_target == 'en':
            return text
        return self.translate_text(text, target_language=normalized_target, source_language='en')

    def generate_dummy_response(self, target_language: str) -> str:
        normalized_target = self.normalize_language(target_language)
        if normalized_target == 'en':
            return self._fallback_responses['en']
        try:
            return self.translate_text(self._fallback_responses['en'], normalized_target, 'en')
        except Exception:
            return self._fallback_responses.get(normalized_target, self._fallback_responses['en'])


translator_service = TranslationService()
