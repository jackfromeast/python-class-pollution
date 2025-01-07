import bot.config as conf

conf_editor = conf.ConfigEditor(conf.config)
conf_editor.set_value("openai.__init__.__globals__.__name__", "polluted")
print(conf.__name__)