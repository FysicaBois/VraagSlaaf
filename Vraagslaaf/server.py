import asyncio
import json
import logging

from dotenv import load_dotenv
from aiogoogle import Aiogoogle
from quart import Quart, render_template, Response, websocket, redirect, request

load_dotenv(dotenv_path="Vraagslaaf/env/.env")

with open("Vraagslaaf/env/client_creds.json") as creds_file:
    client_creds = json.load(creds_file)

app = Quart(__name__)

Log = app.logger
app.logger.setLevel(logging.DEBUG)

aiogoogle = Aiogoogle(client_creds=client_creds)

# slot stuf
queued_messages = []
smh = None
vdl = None
ready = False

queue: asyncio.Queue = None

text = "typ slaaf rol <getal> in Discord om te spelen"


@app.before_serving
async def startup():
    global queue
    queue = asyncio.Queue()  # make sure we create the queue on the application loop


@app.route('/')
async def home():
    return "I'm alive"


@app.route('/send/<text>')
async def send(text):
    global queue
    await queue.put("messsage💩" + text)
    return "sent " + text


@app.route('/theo')
async def theo():
    return await render_template("theo.html")


@app.route('/slots')
async def login():
    return await render_template("index.html", text=text)


@app.route('/verify/<has>')
async def verify(has):
    print(has)
    decoded = bytes.fromhex(has).decode('utf-8')
    print(decoded)
    id, email = decoded.split("%")
    await queue.put("verify" + "💩" + json.dumps({"id": int(id), "email": email}))
    return "Done"


@app.route('/stream')
async def stream():
    def eventStream():
        while True:
            global smh
            if smh.server_message is not None:
                yield 'data: {}\n\n'.format(smh.server_message)

    # this should be easier with websockets and quart
    return Response(eventStream(), mimetype="text/event-stream")


async def _send_message(websocket):
    while True:
        data = await queue.get()
        Log.debug(f"putting data in the queue: {data}")
        await websocket.send(data)


async def _receive_message(websocket):
    try:
        while True:
            data = await websocket.receive()
            Log.debug(data)
            # when we receive a message, pong it back to all listeners
    except asyncio.CancelledError:
        Log.info("Websocket disconnected")


@app.websocket('/ws')
async def socket():
    Log.info("Websocket connected")

    producer = asyncio.create_task(_send_message(websocket))
    consumer = asyncio.create_task(_receive_message(websocket))
    await asyncio.gather(producer, consumer)


# Google o-auth stuff.
# From here on out this is boilerplate oauth2 code to create credentials for the Vraagslaaf google account.

@app.route('/authorize')
def authorize():
    uri = aiogoogle.oauth2.authorization_url(
        client_creds=client_creds,
        include_granted_scopes=True,
        access_type="offline" # this has tot be included for aiogoogle to include refresh tokens, horribly documented

    )
    return redirect(uri)


@app.route('/callback/aiogoogle')
async def callback():
    # First, check if there's an error
    if request.args.get('error'):
        error = {
            'error': request.args.get('error'),
            'error_description': request.args.get('error_description')
        }
        return json.dumps(error)

    # Here we request the access and refresh token
    elif request.args.get('code'):
        full_user_creds = await aiogoogle.oauth2.build_user_creds(
            grant=request.args.get('code'),
            client_creds=client_creds
        )
        # Here, you should store full_user_creds in a db. Especially the refresh token and access token.

        with open("Vraagslaaf/env/user_creds.json", "w+") as user_creds_file:
            json.dump(full_user_creds, user_creds_file)
            return "Authorization succesful, you can now close this page"

    else:
        # Should either receive a code or an error
        return "Something's probably wrong with your callback"


def runner():
    app.run(debug=True)


if __name__ == "__main__":
    runner()
