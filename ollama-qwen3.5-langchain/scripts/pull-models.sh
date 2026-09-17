#!/usr/bin/env bash
set -e
docker compose exec ollama ollama pull qwen3.5:9b
docker compose exec ollama ollama pull nomic-embed-text
