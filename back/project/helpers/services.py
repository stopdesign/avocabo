import unicodedata
from django.core.files.storage import FileSystemStorage
from django.utils.crypto import get_random_string


class ASCIIFileSystemStorage(FileSystemStorage):
    """
    Convert unicode characters in name to ASCII characters.
    """

    def get_valid_name(self, name):
        filename = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('utf8')
        try:
            name, ext = filename.split('.')
            name = name.strip()
            ext = ext.lower()

            if not name:
                name = get_random_string(5)
            filename = '%s.%s' % (name, ext)
        except ValueError:
            pass

        if not filename:
            filename = get_random_string(5)

        return super().get_valid_name(filename)
