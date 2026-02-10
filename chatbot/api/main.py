"""
FastAPI application for AI Agent API (T095).

Provides REST endpoints for agent interaction with JWT authentication.
"""

"""
FastAPI application for AI Agent API (T095).
Provides REST endpoints for agent interaction with JWT authentication.
"""

# ✅ LOAD ENV FIRST (CRITICAL)
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from chatbot.agent.config import get_settings
from chatbot.api.routes import sessions, messages, confirm, plan, audit, chat, chatkit


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="AI Agent API",
        description="REST API for the AI Agent",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(sessions.router, prefix="/api/agent", tags=["sessions"])
    app.include_router(messages.router, prefix="/api/agent", tags=["messages"])
    app.include_router(confirm.router, prefix="/api/agent", tags=["confirm"])
    app.include_router(plan.router, prefix="/api/agent", tags=["plan"])
    app.include_router(audit.router, prefix="/api/agent", tags=["audit"])
    app.include_router(chat.router, prefix="/api", tags=["chat"])
    app.include_router(chatkit.router, tags=["chatkit"])

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        import logging
        logging.exception(exc)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Something went wrong. Please try again.",
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                },
            },
        )

    @app.get("/")
    def root():
        return {
            "status": "ok",
            "message": "Todo Chatbot API is running",
            "openai_key_loaded": bool(os.getenv("OPENAI_API_KEY")),
        }

    return app

print("OPENAI_API_KEY loaded:", bool(os.getenv("OPENAI_API_KEY")))


app = create_app()
