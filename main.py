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
from binary import lll

main = Blueprint(__name__, "plan")


from hume import HumeBatchClient
from hume.models.config import ProsodyConfig
from hume.models.config import BurstConfig

client = HumeBatchClient("N8s5670QNccUlXE5S3uOydcR8Q2EWMP2dWGkXG0NIx4Sf86v")
configs = [ProsodyConfig(granularity="utterance"), BurstConfig()] # this uses prosody, was more interested in sounds, can explore more tomorrow
urls = ["audio.webm"]


@main.route("/")
def base():
    return "test"


@main.route("/audio", methods=["POST"])
def audio():
    # ill need to process whatever data you send here
    #data = request.json()
    # with axios
    #file = request.form["file"]
    #filename = request.form["fileName"]
    audio_b64 = request.get_json() # request.get_json()
    audio_b64 = audio_b64[35:] # data:audio/webm;codecs=opus;base64,Gk
    audio_clean = base64.b64decode(audio_b64)
    with open("audio.webm", "wb") as fh:
        fh.write(audio_clean)
    # previously used urls https://storage.googleapis.com/hume-test-data/video/armisen-clip.mp4


    # need to fix hume api to work with local files


    job = client.submit_job([], configs, files=urls)
    print(job)
    print("Running...")
    job.await_complete()
    job.download_predictions("predictions.json")
    with open("predictions.json", "r") as fh:
        emotions = json.load(fh)
    try:
        emotions = emotions[0]["results"]["predictions"][0]["models"]["burst"]["grouped_predictions"][0]["predictions"][0]["emotions"]
    except:
        pass # sometimes prosody works, sometimes burst, so I try both
    try:
        emotions = emotions[0]["results"]["predictions"][0]["models"]["prosody"]["grouped_predictions"][0]["predictions"][0]["emotions"]
    except:
        emotions = [{'name': 'Calmness', 'score': 1}] # default to calm i feel like that makes sense
    max_index = 0
    max_emotion = 0
    for i in range(len(emotions)):
        if emotions[i]["score"] > max_emotion:
            max_emotion = emotions[i]["score"]
            max_index = i
    print("Max = ", emotions[max_index])

    # resetting for next user, should be in flask session imo
    os.remove("predictions.json")
    os.remove("audio.webm")

    return redirect("/")   

@main.route("/journal", methods=["POST"])
def journal():
    return