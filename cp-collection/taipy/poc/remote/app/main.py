from taipy.gui import Gui

message = "Hello"

page = """
# Taipy Demo
<|{message}|input|>
"""

if __name__ == "__main__":
  gui = Gui(page=page)
  gui.run(host="0.0.0.0", port=5000, use_reloader=False)
