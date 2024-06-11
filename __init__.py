import os

from support import SupportSC

try:
    if os.path.exists(os.path.join(os.path.dirname(__file__), '1gdrive.py')):
        from .gdrive import SSGDrive
    else:
        SSGDrive = SupportSC.load_module_f(__file__, 'gdrive').SSGDrive
except:
    pass