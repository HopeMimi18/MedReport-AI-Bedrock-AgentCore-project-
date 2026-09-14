from strands import Agent
from strands.models import BedrockModel

model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    region_name="us-east-1"
)

agent = Agent(
    model=model,
    system_prompt="You are a helpful assistant. Keep answers clear and concise."
)

response = agent("Say hello and confirm that Amazon Nova Pro is working.")
print(response)