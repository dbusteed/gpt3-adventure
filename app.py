import os
import re
from matplotlib import textpath
import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

prompt_prefix = "You are an adventurer searching for treasure in a dungeon.\n\n"
prompt = [
    ["STORY: ", "You enter a dungeon."]
]

def format_prompt(prompt):
    fprompt = prompt_prefix
    for p in prompt:
        fprompt += (p[0] + p[1] + "\n")
    return fprompt[:-1]


@app.route("/", methods=["GET"])
def index_get():
    return render_template("index.html", prompt=prompt)


@app.route("/", methods=["POST"])
def index_post():
    response = request.form["response"]
    prompt.append(["YOU: ", response])
    prompt.append(["STORY: ", ""])
    while True:
        api_resp = openai.Completion.create(
            engine="text-davinci-001",
            prompt=format_prompt(prompt),
            temperature=1,
        )
        
        raw_text = api_resp.choices[0].text
        text = raw_text.replace('\n', ' ')
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'YOU:.*', '', text)
        prompt[-1][1] += text

        if 'YOU:' in raw_text:
            break
        if api_resp.choices[0].finish_reason == 'stop':
            break

    return redirect(url_for("index_get"))


if __name__ == "__main__":
    app.run()