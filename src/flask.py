import collections
import functools
import threading

import arrow
from flask import Flask, request, jsonify, render_template

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
        super().__init__("krcg", template_folder=".")

    def make_default_options_response(self,):
        response = super().make_default_options_response()
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response

    def process_response(self, response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response


app = KRCG()


def twda_required(f):
    def check_init(*args, **kwargs):
        if not initialized.wait(5):
            return "Initializing", 503
        return f(*args, **kwargs)

    return check_init


@app.route("/", methods=["GET"])
def swagger():
    return render_template("src/index.html")


@app.route("/openapi.yaml", methods=["GET"])
def openapi():
    return render_template("src/openapi.yaml")


@twda_required
@app.route("/deck", methods=["POST"])
def deck_by_cards():
    data = request.get_json() or {}
    twda.TWDA.configure(
        arrow.get(data.get("date_from") or "2008-01-01"),
        arrow.get(data.get("date_to") or None),
        data.get("players") or 0,
        spoilers=False,
    )
    decks = twda.TWDA
    if data and data.get("cards"):
        A = analyzer.Analyzer()
        try:
            A.refresh(
                *[vtes.VTES.get_name(vtes.VTES[card]) for card in data["cards"]],
                similarity=1
            )
            decks = A.examples
        except analyzer.AnalysisError:
            return "No result in TWDA", 404
        except KeyError:
            return "Invalid card name", 400
    return jsonify([vtes.VTES.deck_to_dict(v, k) for k, v in decks.items()])


@twda_required
@app.route("/deck/<twda_id>", methods=["GET"])
def deck_by_id(twda_id):
    if not twda_id:
        return "Bad Request", 400
    if twda_id not in twda.TWDA:
        return "Not Found", 404
    return jsonify(vtes.VTES.deck_to_dict(twda.TWDA[twda_id], twda_id))


@app.route("/complete/<text>", methods=["GET"])
def complete(text):
    return jsonify(
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
