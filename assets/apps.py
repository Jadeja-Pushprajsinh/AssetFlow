from django.apps import AppConfig


class AssetsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'assets'

    def ready(self):
        # Register post_save signal for asset_tag generation
        import assets.models  # noqa: F401
