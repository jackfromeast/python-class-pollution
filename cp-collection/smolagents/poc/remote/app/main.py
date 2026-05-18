"""
Minimal smolagents Gradio app that exposes the local Python executor remotely.
The agent uses CodeAgent with local_python_executor, deployed via GradioUI.
"""
from smolagents import CodeAgent, GradioUI, HfApiModel

agent = CodeAgent(
    tools=[],
    model=HfApiModel(),
)

if __name__ == "__main__":
    GradioUI(agent).launch(server_name="0.0.0.0", server_port=7860)
