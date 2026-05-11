class Apple:
  def __init__(self):
    self._B = Banana()

  def eat(self, msg):
    self._B.eat(msg)

class Banana:
  def __init__(self):
    pass

  def eat(self, msg):
    sink(msg)

if __name__ == "__main__":
  a = Apple()
  a.eat("Hello, World!")