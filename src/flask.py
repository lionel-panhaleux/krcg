import threading

import arrow
from flask import Blueprint, Flask, request, jsonify, render_template

from . import analyzer
from . import twda
from . import vtes


class KRCG(Flask):
    def make_default_options_response(self,):
        response = super().make_default_options_response()
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response

    def process_response(self, response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response


base = Blueprint("base", "krcg")
initialized = threading.Event()


def init_twda():
    twda.TWDA.load_from_vekn(save=False)
    initialized.set()


def create_app(test=False):
    if test:
        initialized.set()
    else:
        vtes.VTES.load_from_vekn(save=False)
        vtes.VTES.configure()
        threading.Thread(target=init_twda).start()
    app = KRCG("krcg", template_folder=".")
    app.register_blueprint(base)
    return app


def twda_required(f):
    def check_init(*args, **kwargs):
        if not initialized.wait(5):
            return "Initializing", 503
        return f(*args, **kwargs)

    return check_init


@base.route("/", methods=["GET"])
def swagger():
    return render_template("src/index.html")


@base.route("/openapi.yaml", methods=["GET"])
def openapi():
    return render_template("src/openapi.yaml")


@base.route("/card/<text>", methods=["GET"])
def card(text):
    try:
        text = int(text)
    except ValueError:
        pass
    try:
        return jsonify(vtes.VTES.normalized(vtes.VTES[text]))
    except KeyError:
        return "Card not found", 404


@twda_required
@base.route("/deck", methods=["POST"])
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
@base.route("/deck/<twda_id>", methods=["GET"])
def deck_by_id(twda_id):
    if not twda_id:
        return "Bad Request", 400
    if twda_id not in twda.TWDA:
        return "Not Found", 404
    return jsonify(vtes.VTES.deck_to_dict(twda.TWDA[twda_id], twda_id))


@base.route("/complete/<text>", methods=["GET"])
def complete(text):
    return jsonify(vtes.VTES.complete(text))
