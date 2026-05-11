from flask import Flask, request, jsonify
import builtins

app = Flask(__name__)

class AgentParam:
  name = "default_agent"
  temperature = 0.7

agent_param = AgentParam()

def _recursive_update_param(param, config, depth=0):
  """Reproduces ragflow's ComponentParamBase._recursive_update_param"""
  if depth > 5:
    raise ValueError("Too deep")
  for config_key, config_value in config.items():
    attr = getattr(param, config_key, None)
    if type(attr).__name__ in dir(builtins) or attr is None:
      setattr(param, config_key, config_value)
    else:
      _recursive_update_param(attr, config_value, depth + 1)

@app.route("/v1/agent/completion", methods=["POST"])
def agent_completion():
  data = request.get_json()
  # ragflow passes request body fields to component parameter update
  _recursive_update_param(agent_param, data)
  return jsonify({"status": "ok", "agent_name": agent_param.name})

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=9380)
