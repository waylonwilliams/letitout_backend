# TO DO
# chat gpt analysis of journals
# home button react
# journals page react
#     chat gpt button on that page -> another page
#     journals link to themselves in text editor, I could supply the content that makes up specific journal id?


from flask import Blueprint, request, jsonify
import os
import base64
from prompts import prompts
import openai

main = Blueprint(__name__, "plan")

from pymongo.mongo_client import MongoClient
uri = "mongodb+srv://waylon:Vx9CR3sOBHQwN0uL@letitoutdb.8bxplet.mongodb.net/?retryWrites=true&w=majority"
db_client = MongoClient(uri)
db = db_client.main
user_info = db.user_info
journals = db.journals

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

chat_key = "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"
openai.api_key = chat_key

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
    if "burst" in emotions:
        emotions = emotions["burst"]["predictions"][0]["emotions"]
    elif "prosody" in emotions:
        emotions = emotions["prosody"]["predictions"][0]["emotions"]
    else:
        emotions = [{"name": "Calmness", "score": 1}]
    max_index = 0
    max_emotion = 0
    for i in range(len(emotions)):
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
    all_user_data = user_info.find()
    users = []
    for user in all_user_data:
        user["_id"] = str(user["_id"])
        users.append(user)
    return jsonify(users)


@main.route("/journal_get", methods=["POST"]) # may need to be post to get user
def journal_get():
    all_journal_data = journals.find({"user": "Waylon"}) # replace with current user
    journal_array = []
    for journal in all_journal_data:
        journal["_id"] = str(journal["_id"])
        journal_array.append(journal)
    print(journal_array)
    return journal_array


@main.route("/add_journal", methods=["POST"])
def add_journal():
    data = request.get_json()
    # make  a heading
    name = ""
    i = 0
    while i < len(data["content"]):
        if data["content"][i] == "<":
            while data["content"][i] != ">":
                i += 1
            i += 1
            continue
        name += data["content"][i]
        if len(name) >= 20:
            break
        i += 1

    doc = [
        {"user": data["user"], "prompt": data["prompt"], "content": data["content"], "name": name}
    ]
    journals.insert_many(doc)
    return {"success": "true"}
    # prompt content user name(first 20 of paragraph)


@main.route("/journal_analysis") # post in order to get user
def journal_analysis():
    all_journal_data = journals.find({"user": "Waylon"}) # replace with current user
    journal_array = []
    for journal in all_journal_data:
        name = ""
        i = 0
        while i < len(journal["content"]):
            if journal["content"][i] == "<":
                while journal["content"][i] != ">":
                    i += 1
                i += 1
                continue
            name += journal["content"][i]
            i += 1
        journal_array.append("Prompt:")
        journal_array.append(journal["prompt"])
        journal_array.append("Response:")
        journal_array.append(name)
    # send to chat
    journal_array = " ".join(journal_array)



    chat_summary = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[ {
        "role": "user",
        "content": "I am going to provide you with a string of journal prompts and responses. Analyze the string and provide insightful information about how the user processes their emotions. Make specific comments on improvements they can make and possible things they aren't considering. Praise the user for good things they have done which were morally just. Refer to things they have done like 'You are very animal friendly.'"
        },
        {
        "role": "assistant",
        "content": "Without the specific string of prompts and responses, it's impossible to provide any sort of analysis or feedback. Please supply the said string so I can provide proper assistance."
        },
        {
        "role": "user",
        "content": "Here is the string: {}".format(journal_array)
        }, ],
        temperature=1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    chat_specific = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[ {
        "role": "user",
        "content": "I am going to provide you with a string of journal prompts and responses. Pick out as many specific good things as you can that occurred throughout their journals. Write as if you are speaking to them, like \"You did this.\" Here is the string: {}".format(journal_array)
        }, ],
        temperature=1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
    chat_summary = chat_summary["choices"][0]["message"]["content"]
    chat_specific = chat_specific["choices"][0]["message"]["content"]
    return {"summary": str(chat_summary), "events": str(chat_specific)}