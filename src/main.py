from smolagents import HfApiModel, CodeAgent, ManagedAgent
from manager import ManimManagerAgent

model = HfApiModel("Qwen/Qwen2.5-72B-Instruct")
manager = ManimManagerAgent(model)

user_input=input("Enter query: ")
video_path = manager.create_animation(user_input)

print(f"Animation created at: {video_path}")