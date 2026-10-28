import logging
from pathlib import Path

from fluent.runtime import FluentBundle, FluentResource

logger = logging.getLogger(__name__)

# translator.py -> i18n -> bot -> app -> корень проекта
LOCALES_DIR = Path(__file__).resolve().parents[3] / "locales"
DEFAULT_LOCALE = "ru"


class Translator:
    """Переводчик для одного языка. Создаётся на каждый апдейт, но это дёшево."""

    def __init__(self, hub: "TranslatorHub", locale: str):
        self.hub = hub
        self.locale = locale

    def get(self, key: str, **kwargs) -> str:
        # сначала язык пользователя, потом запасной
        for loc in (self.locale, self.hub.default_locale):
            bundle = self.hub.bundles[loc]
            message = bundle.get_message(key)
            if message is not None and message.value is not None:
                text, errors = bundle.format_pattern(message.value, kwargs)
                if errors:
                    logger.warning("i18n %s/%s: %s", loc, key, errors)
                return str(text)
        logger.warning("i18n: нет ключа %r", key)
        return key

    def switch(self, locale: str) -> "Translator":
        """Переводчик на другом языке (нужен после смены языка в хендлере)."""
        return self.hub.get_translator(locale)


class TranslatorHub:
    def __init__(self, default_locale: str = DEFAULT_LOCALE):
        self.default_locale = default_locale
        self.bundles: dict[str, FluentBundle] = {}

        for locale_dir in LOCALES_DIR.iterdir():
            if not locale_dir.is_dir():
                continue
            # use_isolating=False: иначе вокруг { $name } появляются невидимые символы
            bundle = FluentBundle([locale_dir.name], use_isolating=False)
            for ftl in sorted(locale_dir.glob("*.ftl")):
                bundle.add_resource(FluentResource(ftl.read_text(encoding="utf-8")))
            self.bundles[locale_dir.name] = bundle

        if default_locale not in self.bundles:
            raise RuntimeError(f"Нет переводов для языка по умолчанию: {default_locale}")

    @property
    def locales(self) -> frozenset[str]:
        return frozenset(self.bundles)

    def normalize(self, code: str | None) -> str:
        """'en-US' -> 'en'; неизвестный язык -> дефолтный."""
        base = (code or "").split("-")[0].lower()
        return base if base in self.bundles else self.default_locale

    def get_translator(self, locale: str | None) -> Translator:
        return Translator(self, self.normalize(locale))