# 컨테이너가 기동된 뒤 필요한 모델을 내려받는다.
docker compose exec ollama ollama pull qwen3.5:9b
docker compose exec ollama ollama pull nomic-embed-text
