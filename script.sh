#!/bin/sh

if command -v uv >/dev/null 2>&1; then
    exec uv run ./main.py
else
    exec python3 ./main.py
fi