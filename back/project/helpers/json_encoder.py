from django.core.serializers.json import DjangoJSONEncoder
from hexbytes import HexBytes
from web3.datastructures import AttributeDict


class HexJsonEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, HexBytes):
            return obj.hex()
        if isinstance(obj, AttributeDict):
            return dict(obj)
        return super().default(obj)
