import magicattr

class Person:
    settings = {
        'autosave': True,
        'style': {
            'height': 30,
            'width': 200
        },
        'themes': ['light', 'dark']
    }
    def __init__(self, name, age, friends):
        self.name = name
        self.age = age
        self.friends = friends


bob = Person(name="Bob", age=31, friends=[])

magicattr.set(bob, '__class__.__init__.__globals__["__name__"]', "polluted")

print(__name__)