# TO DO
# audio from react to flask
# write prompts for each emotion
# create text editor page after flask has analyzed the sigh
# database to save user journals (mongo db)
# another option to have hume analyze your journals


from flask import Blueprint, request, redirect
import requests
import json
import os
import base64
from prompts import prompts

main = Blueprint(__name__, "plan")


from hume import HumeBatchClient
from hume.models.config import ProsodyConfig
from hume.models.config import BurstConfig
from hume import HumeStreamClient, StreamSocket
import asyncio

client = HumeBatchClient("N8s5670QNccUlXE5S3uOydcR8Q2EWMP2dWGkXG0NIx4Sf86v")
configs = [ProsodyConfig(granularity="utterance"), BurstConfig()] # this uses prosody, was more interested in sounds, can explore more tomorrow
urls = ["audio.webm"]

async def get_emotion():
    client = HumeStreamClient("N8s5670QNccUlXE5S3uOydcR8Q2EWMP2dWGkXG0NIx4Sf86v")
    config = BurstConfig()
    async with client.connect([config]) as socket:
        result = await socket.send_file("audio.webm")
        return result


@main.route("/")
def base():
    return "test"


@main.route("/audio", methods=["POST"])
def audio():
    # gets audio from react and decodes
    audio_b64 = request.get_json() 
    audio_b64 = audio_b64[35:] 
    audio_clean = base64.b64decode(audio_b64)
    with open("audio.webm", "wb") as fh:
        fh.write(audio_clean)

    emotions = asyncio.run(get_emotion())
    print("\n\n\n Base emotions ", emotions)
    emotions = emotions["burst"]["predictions"][0]["emotions"]
    print("\n\n\n", emotions)
    max_index = 0
    max_emotion = 0
    for i in range(len(emotions)):
        print(emotions[i]["name"])
        if emotions[i]["score"] > max_emotion:
            max_emotion = emotions[i]["score"]
            max_index = i
    print("Max = ", emotions[max_index])

    if emotions[max_index]["name"] in prompts.keys():
        print("Emotion: ", emotions[max_index]["name"], "Prompt: ", prompts[emotions[max_index]["name"]])
    else:
        print("No prompt for", emotions[max_index]["name"])

    # resetting for next user, should be in flask session imo
    os.remove("audio.webm")

    return redirect("/")   

@main.route("/journal", methods=["POST"])
def journal():
    return

