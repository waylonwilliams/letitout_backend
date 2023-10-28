# TO DO
# database to save user journals (mongo db)
# another option to have hume analyze your journals


from flask import Blueprint, request, jsonify
import os
import base64
from prompts import prompts

main = Blueprint(__name__, "plan")

from pymongo.mongo_client import MongoClient
uri = "mongodb+srv://waylon:Vx9CR3sOBHQwN0uL@letitoutdb.8bxplet.mongodb.net/?retryWrites=true&w=majority"
db_client = MongoClient(uri)
db = db_client.main
user_info = db.user_info
try:
    db_client.admin.command('ping')
    print("\n\n\nPinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


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


@main.route("/audio", methods=["POST"])
def audio():
    # gets audio from react and decodes
    audio_b64 = request.get_json() 
    audio_b64 = audio_b64[35:] 
    audio_clean = base64.b64decode(audio_b64)
    with open("audio.webm", "wb") as fh:
        fh.write(audio_clean)

    # gets emotion scores from live api
    emotions = asyncio.run(get_emotion())
    print("\n\n\n Base emotions ", emotions)
    if "burst" in emotions:
        emotions = emotions["burst"]["predictions"][0]["emotions"]
    elif "prosody" in emotions:
        emotions = emotions["prosody"]["predictions"][0]["emotions"]
    else:
        emotions = [{"name": "Calmness", "score": 1}]
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

    return {"prompt": prompts[emotions[max_index]["name"]]}


@main.route("/provide_logins")
def provide_logins():
    x = user_info.find()
    users = []
    for user in x:
        users.append(user)
    print(users)
    return jsonify(users)
    # get data
    # return







@main.route("/journal_analysis") # should be just a get?
def journal_analysis():
    global journals
    journals = journals.find({"user": "Waylon"})
    print(type(journals))
    journal_array = []
    for i in journals:
        journal_array.append(i)
    print(journal_array[0], "TYPE: ", type(journal_array[0]))
    return jsonify(journal_array[0])
