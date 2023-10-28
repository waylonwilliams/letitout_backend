from flask import Blueprint, request 

main = Blueprint(__name__, "plan")

from hume import HumeBatchClient
from hume.models.config import FaceConfig
from hume.models.config import ProsodyConfig


client = HumeBatchClient("MCuO1K3e33jT4rYJT1iqQc7CBxWoCzJ8KxGFkRLVIHbA0XJ0")
urls = []
configs = [ProsodyConfig(granularity="utterance")] # this uses prosody, was more interested in sounds, can explore more tomorrow


@main.route("/")
def base():
    return "test"

@main.route("/audio", methods=["POST"])
def audio():
    # ill need to process whatever data you send here
    urls.append("https://storage.googleapis.com/hume-test-data/video/armisen-clip.mp4") # assumes you will be passing a url, can also be adjusted
    job = client.submit_job(urls, configs)
    print(job)
    print("Running...")
    job.await_complete()
    job.download_predictions("predictions.json")
    print("Predictions downloaded to predictions.json")
    return

@main.route("/journal", methods=["POST"])
def journal():
    return