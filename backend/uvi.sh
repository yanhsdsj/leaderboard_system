#!/bin/bash
# 启动 FastAPI 服务的脚本
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000