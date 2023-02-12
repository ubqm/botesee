import asyncio
from fastapi import FastAPI, BackgroundTasks, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from models.events import MatchReady, MatchFinished, MatchAborted, MatchCancelled
from loguru import logger
logger.add("errors.log", level="ERROR", rotation="1 week")

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logger.error(f"{request}: {exc_str}")
    logger.error(f"entity = {exc.body}")
    content = {'status_code': 422, 'message': exc_str, 'data': exc.body}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.get("")
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/match_status_ready")
async def respond_status_ready(match: MatchReady, background_tasks: BackgroundTasks):
    logger.info(f"{match.json()}")
    print(match.dict())
    # background_tasks.add_task()
    # loop.create_task(
    #     bot_client.post_faceit_message_ready(
    #         channel_id=828940900033626113, request_json=request.json
    #     )
    # )
    # print("respond match_status_ready function called")
    # return Response(status=200)


@app.post("/match_status_finished")
async def respond_status_finished(match: MatchFinished):
    logger.info(f"{match.json()}")
    # print(request.json)
    # loop.create_task(
    #     bot_client.post_faceit_message_finished(
    #         channel_id=828940900033626113, request_json=request.json
    #     )
    # )
    # print("respond match_status_finished function called")
    # return Response(status=200)


@app.post("/match_status_aborted")
async def respond_status_aborted(match: MatchAborted | MatchCancelled):
    logger.info(f"{match.json()}")
    # print(request.json)
    # loop.create_task(
    #     bot_client.post_faceit_message_aborted(
    #         channel_id=828940900033626113, request_json=request.json
    #     )
    # )
    # print("respond match_status_aborted function called")
    # return Response(status=200)


@logger.catch(message="")
async def main(a, b):
    print(a / b)


if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=8001)
    logger.add("errors.json", level="ERROR", serialize=False)
    asyncio.run(main(1, 0))
