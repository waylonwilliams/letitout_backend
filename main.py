# TO DO
# audio from react to flask
# write prompts for each emotion
# create text editor page after flask has analyzed the sigh
# database to save user journals (mongo db)
# another option to have hume analyze your journals


from flask import Blueprint, request, redirect, session
import json
import os
import base64
from binary import lll

main = Blueprint(__name__, "plan")


from hume import HumeBatchClient
from hume.models.config import FaceConfig
from hume.models.config import ProsodyConfig

client = HumeBatchClient("pP0Q67fHYxCnZUTy9Ov71kCBXw6vzglYABCogBJkTooXAWfj")
configs = [ProsodyConfig(granularity="utterance")] # this uses prosody, was more interested in sounds, can explore more tomorrow


@main.route("/")
def base():
    return "test"



@main.route("/audio")
def audio():
    # ill need to process whatever data you send here
    #data = request.json()
    # with axios
    #file = request.form["file"]
    #filename = request.form["fileName"]
    audio_b64 = lll # request.get_json()
    audio_clean = base64.b64decode(audio_b64)
    with open("audio.webm", "wb") as fh:
        fh.write(audio_clean)
    session["urls"] = ["https://storage.googleapis.com/hume-test-data/video/armisen-clip.mp4"] # just change it to local file
    job = client.submit_job(session["urls"], configs)
    print(job)
    print("Running...")
    job.await_complete()
    job.download_predictions("predictions.json")
    with open("predictions.json", "r") as fh:
        emotions = json.load(fh)
    emotions = emotions[0]["results"]["predictions"][0]["models"]["prosody"]["grouped_predictions"][0]["predictions"][0]["emotions"]
    print(emotions)
    max_index = 0
    max_emotion = 0
    for i in range(len(emotions)):
        if emotions[i]["score"] > max_emotion:
            max_emotion = emotions[i]["score"]
            max_index = i
    print("Max = ", emotions[max_index])

    # resetting for next user, should be in flask session imo
    os.remove("predictions.json")

    return redirect("/")   

@main.route("/journal", methods=["POST"])
def journal():
    return