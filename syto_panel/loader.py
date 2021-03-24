import fnmatch

from django.conf import settings
from manifest_loader.loaders import LoaderABC


class VuetifyLoader(LoaderABC):
    @staticmethod
    def get_single_match(manifest, key):
        return manifest.get(key, key).replace(settings.STATIC_URL, "/")

    @staticmethod
    def get_multi_match(manifest, pattern):
        matched_files = [
            file for file in manifest.keys() if fnmatch.fnmatch(file, pattern)
        ]
        return [
            manifest.get(file).replace(settings.STATIC_URL, "/")
            for file in matched_files
        ]
