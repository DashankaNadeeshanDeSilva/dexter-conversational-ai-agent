from openai import OpenAI

client = OpenAI(
  api_key=OpenAI.api_key,
)

response = client.responses.create(
  model="gpt-4o-mini",
  input="what is the capital of France?",
  store=True,
)

print(response.output_text)