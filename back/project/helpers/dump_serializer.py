from django.conf import settings
from django.core.serializers.json import Serializer as JsonSerializer
from django.utils.encoding import is_protected_type


class Serializer(JsonSerializer):
    def _value_from_field(self, obj, field):
        """
        Тут подменяем данные полей используюя settings.EXPORT_DATA_MAP
        """
        value = field.value_from_object(obj)
        field_filter = settings.EXPORT_DATA_MAP.get(str(field))
        if field_filter:
            return field_filter(value)

        # Protected types (i.e., primitives like None, numbers, dates,
        # and Decimals) are passed through as is. All other values are
        # converted to string first.
        return value if is_protected_type(value) else field.value_to_string(obj)
