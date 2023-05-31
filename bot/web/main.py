from fastapi import BackgroundTasks, Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel

from bot.clients.rabbit import RabbitClient
from bot.web.dependencies import get_rabbit
from bot.web.models.events import (
    MatchAborted,
    MatchCancelled,
    MatchFinished,
    MatchReady,
)

logger.add("errors.log", level="ERROR", rotation="1 week")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logger.error(f"{request}: {exc_str}")
    logger.error(f"entity = {exc.body}")
    content = {"status_code": status.HTTP_422_UNPROCESSABLE_ENTITY, "message": exc_str, "data": exc.body}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class OKResponse(BaseModel):
    status: str = "ok"


@app.get("/", tags=["health"])
@app.get("/health", tags=["health"])
async def health() -> OKResponse:
    return OKResponse()


@app.post("/match_status_ready", tags=["FaceIT Webhooks"])
async def respond_status_ready(
    match: MatchReady,
    background_tasks: BackgroundTasks,
    rabbit: RabbitClient = Depends(get_rabbit),
) -> OKResponse:
    logger.info(f"{match.json()}")
    background_tasks.add_task(rabbit.publish, message=match.json())
    return OKResponse()


@app.post("/match_status_finished", tags=["FaceIT Webhooks"])
async def respond_status_finished(
    match: MatchFinished,
    background_tasks: BackgroundTasks,
    rabbit: RabbitClient = Depends(get_rabbit),
) -> OKResponse:
    logger.info(f"{match.json()}")
    background_tasks.add_task(rabbit.publish, message=match.json())
    return OKResponse()


@app.post("/match_status_aborted", tags=["FaceIT Webhooks"])
async def respond_status_aborted(
    match: MatchAborted | MatchCancelled,
    background_tasks: BackgroundTasks,
    rabbit: RabbitClient = Depends(get_rabbit),
) -> OKResponse:
    logger.info(f"{match.json()}")
    background_tasks.add_task(rabbit.publish, message=match.json())
    return OKResponse()
