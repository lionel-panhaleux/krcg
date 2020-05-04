import logging
import pkg_resources  # part of setuptools

import arrow
from flask import Blueprint, Flask, request, jsonify, render_template


from . import analyzer
from . import config
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


logger = logging.getLogger()
base = Blueprint("base", "krcg")


def create_app(test=False):
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.WARNING)
    if not test:
        vtes.VTES.load_from_vekn(save=False)
        vtes.VTES.configure()
        logger.info("loading TWDA")
        twda.TWDA.load_from_vekn(save=False)
        twda.TWDA.configure()
    logger.info("launching app")
    app = KRCG("krcg", template_folder="templates")
    app.register_blueprint(base)
    return app


@base.route("/", methods=["GET"])
def swagger():
    return render_template("index.html")


@base.route("/openapi.yaml", methods=["GET"])
def openapi():
    return render_template(
        "openapi.yaml", version=pkg_resources.require("krcg")[0].version,
    )


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


@base.route("/card", methods=["POST"])
def card_search():
    data = request.get_json() or {}
    result = set(card["Id"] for card in vtes.VTES.original_cards.values())
    for type_ in data.get("type") or []:
        result &= vtes.VTES.search["type"].get(type_.lower(), set())
    for clan in data.get("clan") or []:
        clan = config.CLANS_AKA.get(clan.lower()) or clan
        result &= vtes.VTES.search["clan"].get(clan.lower(), set())
    for group in data.get("group") or []:
        result &= vtes.VTES.search["group"].get(group.lower(), set())
    for sect in data.get("sect") or []:
        result &= vtes.VTES.search["sect"].get(sect.lower(), set())
    for trait in data.get("trait") or []:
        result &= vtes.VTES.search["trait"].get(trait.lower(), set())
    for discipline in data.get("discipline") or []:
        discipline = config.DIS_MAP.get(discipline) or discipline
        result &= vtes.VTES.search["discipline"].get(discipline, set())
    for bonus in data.get("bonus") or []:
        result &= vtes.VTES.search.get(bonus.lower(), set())
    if data.get("text"):
        result &= set(vtes.VTES.search["text"].search(data["text"].lower()))
    return jsonify(sorted(vtes.VTES.get_name(vtes.VTES[int(i)]) for i in result))
