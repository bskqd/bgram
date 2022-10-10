from core.config import SettingsABC, Settings


def settings_provider() -> SettingsABC:
    _settings = getattr(settings_provider, '_settings', None)
    if not _settings:
        _settings = Settings()
        setattr(settings_provider, '_settings', _settings)
    return _settings
