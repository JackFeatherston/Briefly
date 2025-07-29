# Briefly
# First time setup
docker-compose up --build

# Download AI models (one time only)
docker exec briefly-ollama ollama pull nomic-embed-text
docker exec briefly-ollama ollama pull llama2:7b

# Daily usage
docker-compose up        # Start
docker-compose down      # Stop
docker-compose build     # Rebuild if needed