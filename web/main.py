from fastapi import FastAPI, Request

from models.events import MatchReady, MatchFinished, MatchAborted, MatchCancelled

app = FastAPI()


# @app.get("/")
# async def respond_default_get():
#     player_data, matches_data, elo_data = await db_fetch_data()
#     context = {"players": player_data, "matches": matches_data, "elo": elo_data}
#     return flask.render_template("index.html", **context)
@app.get("/")
async def health():
    return {"status": "ok"}


@app.post("/match_status_ready")
async def respond_status_ready(match: MatchReady):
    print(match.dict())
    # loop.create_task(
    #     bot_client.post_faceit_message_ready(
    #         channel_id=828940900033626113, request_json=request.json
    #     )
    # )
    # print("respond match_status_ready function called")
    # return Response(status=200)


@app.post("/match_status_finished")
async def respond_status_finished(match: MatchFinished):
    pass
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
    pass
    # print(request.json)
    # loop.create_task(
    #     bot_client.post_faceit_message_aborted(
    #         channel_id=828940900033626113, request_json=request.json
    #     )
    # )
    # print("respond match_status_aborted function called")
    # return Response(status=200)