import ollama 

client = ollama.Client()

# model = "llama2:13b"
model = "gemma3"
prompt = "Describe the plot of Infinity War to me."

response = client.generate(model=model, prompt=prompt)

print("Response from Ollama: ")
print(response.response)