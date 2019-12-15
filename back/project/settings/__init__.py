from .settings import *
from .constance import *
from .logging import *

try:
    from .settings_local import *
except ImportError:
    try:
        from .settings_develop import *
    except ImportError:
        pass
    pass

import project.monkey_patch
