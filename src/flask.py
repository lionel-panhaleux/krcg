import collections
import functools
import threading

import arrow
from flask import Flask, request, jsonify, make_response

from . import analyzer
from . import twda
from . import vtes


initialized = threading.Event()


def init_twda():
    if not twda.TWDA:
        twda.TWDA.load_from_vekn(save=False)
    initialized.set()


class KRCG(Flask):
    def __init__(self):
        if not vtes.VTES:
            vtes.VTES.load_from_vekn(save=False)
        vtes.VTES.configure()
        self.completion_trie = collections.defaultdict(set)
        for name, card in vtes.VTES.items():
            for part in name.split(" "):
                for i in range(3, len(part) + 1):
                    self.completion_trie[part[:i]].add(vtes.VTES.get_name(card))

        threading.Thread(target=init_twda).start()
        super().__init__("krcg")


app = KRCG()


def allow_cors_option():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


def allow_cors_response(data, *args, **kwargs):
    response = make_response(jsonify(data), *args, **kwargs)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


def twda_required(f):
    def check_init(*args, **kwargs):
        if not initialized.wait(5):
            return allow_cors_response("Initializing", 503)
        return f(*args, **kwargs)

    return check_init


@app.route("/deck", methods=["OPTIONS", "POST"])
@twda_required
def deck():
    if request.method == "OPTIONS":
        return allow_cors_option()
    data = request.get_json()
    if data.get("twda_id"):
        return allow_cors_response([vtes.VTES.deck_to_dict(twda.TWDA[data["twda_id"]])])
    twda.TWDA.configure(
        data.get("date_from") or arrow.get(2008, 1, 1),
        data.get("date_to") or arrow.get(),
        data.get("players") or 0,
    )
    if data.get("cards"):
        A = analyzer.Analyzer()
        try:
            A.refresh(*data["cards"], similarity=1)
        except analyzer.AnalysisError:
            return allow_cors_response([])
        return allow_cors_response(
            [[k, vtes.VTES.deck_to_dict(v)] for k, v in A.examples.items()]
        )


@app.route("/complete/<text>", methods=["GET"])
def complete(text):
    if request.method == "OPTIONS":
        return allow_cors_option()
    return allow_cors_response(
        sorted(
            functools.reduce(
                lambda x, y: x & y if x and y else x | y,
                [
                    app.completion_trie.get(part.lower(), set())
                    for part in text.split(" ")
                ],
                set(),
            )
        )
    )
