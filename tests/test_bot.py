# import datetime

# from krcg import discord_bot
# from krcg import vtes


# def test_bot():
#     # use the bot configuration for VTES cards database
#     vtes.VTES.configure(fuzzy_threshold=12, safe_variants=False)
#     # match REMAP values (it may contain easter eggs)
#     response = discord_bot.handle_message("krcg")
#     assert not response.get("content")
#     assert response["embed"]
#     assert response["embed"].to_dict() == {
#         "color": 3498574,
#         "fields": [
#             {"inline": True, "name": "Type", "value": "Master"},
#             {"inline": True, "name": "Cost", "value": "2 Pool"},
#             {
#                 "inline": False,
#                 "name": "Card Text",
#                 "value": "Unique location.\n"
#                 "Lock to give a minion you control +1 intercept. Lock "
#                 "and burn 1 pool to give a minion controlled by another "
#                 "Methuselah +1 intercept.",
#             },
#         ],
#         "footer": {
#             "text": "Click the title to submit new rulings or rulings corrections"
#         },
#         "image": {
#             "url": (
#                 "https://images.krcg.org/krcgnewsradio.jpg"
#                 f"#{datetime.datetime.now():%Y%m%d%H}"
#             )
#         },
#         "title": "KRCG News Radio",
#         "type": "rich",
#         "url": (
#             "https://codex-of-the-damned.org/en/card-search.html"
#             "?card=KRCG+News+Radio"
#         ),
#     }
#     # matching isn't easy
#     response = discord_bot.handle_message("monastery")
#     assert not response.get("content")
#     assert response["embed"]
#     assert response["embed"].to_dict() == {
#         "color": 3498574,
#         "fields": [
#             {"inline": True, "name": "Type", "value": "Master"},
#             {"inline": True, "name": "Cost", "value": "3 Pool"},
#             {
#                 "inline": False,
#                 "name": "Card Text",
#                 "value": "Unique location.\n"
#                 "+1 hand size. Lock to give a vampire with capacity 8 or "
#                 "more +1 stealth.",
#             },
#         ],
#         "footer": {
#             "text": "Click the title to submit new rulings or rulings corrections"
#         },
#         "image": {
#             "url": (
#                 "https://images.krcg.org/monasteryofshadows.jpg"
#                 f"#{datetime.datetime.now():%Y%m%d%H}"
#             )
#         },
#         "title": "Monastery of Shadows",
#         "type": "rich",
#         "url": (
#             "https://codex-of-the-damned.org/en/card-search.html"
#             "?card=Monastery+of+Shadows"
#         ),
#     }
#     # multiple possibilities gives you a choice
#     response = discord_bot.handle_message("isabel")
#     assert not response.get("content")
#     assert response["embed"]
#     assert response["embed"].to_dict() == {
#         "color": 16777215,
#         "description": "1: Isabel Giovanni\n" "2: Isabel de Leon",
#         "footer": {"text": "Click a number as reaction."},
#         "title": "What card did you mean ?",
#         "type": "rich",
#     }
#     # too many possibilities (> 10) gives you an error
#     response = discord_bot.handle_message("the")
#     assert response["content"] == "Too many candidates, try a more complete card name."
#     assert not response.get("embed")
#     # vampire with advanced version
#     response = discord_bot.handle_message("kemintiri")
#     assert response["embed"]
#     assert response["embed"].to_dict() == {
#         "color": 16777215,
#         "description": "1: Kemintiri\n" "2: Kemintiri (ADV)",
#         "footer": {"text": "Click a number as reaction."},
#         "title": "What card did you mean ?",
#         "type": "rich",
#     }
#     # vampire with comma in the name
#     response = discord_bot.handle_message("tariq")
#     assert response["embed"]
#     assert response["embed"].to_dict() == {
#         "color": 16777215,
#         "description": "1: Tariq, The Silent\n" "2: Tariq, The Silent (ADV)",
#         "footer": {"text": "Click a number as reaction."},
#         "title": "What card did you mean ?",
#         "type": "rich",
#     }
#     # card with column in the name
#     response = discord_bot.handle_message("condemnation")
#     assert response["embed"]
#     assert response["embed"].to_dict() == {
#         "color": 16777215,
#         "description": "1: Condemnation: Betrayed\n"
#         "2: Condemnation: Doomed\n"
#         "3: Condemnation: Languid\n"
#         "4: Condemnation: Mute\n"
#         "5: Consanguineous Condemnation",
#         "footer": {"text": "Click a number as reaction."},
#         "title": "What card did you mean ?",
#         "type": "rich",
#     }
#     # fuzzy match
#     response = discord_bot.handle_message("enchant kidnred")
#     assert response["embed"]
#     assert response["embed"].title == "Enchant Kindred"
#     # no match
#     response = discord_bot.handle_message("foobar")
#     assert not response.get("embed")
#     assert response["content"] == "No card match"
#     # reset default VTES configuration to avoid failing other tests
#     vtes.VTES.configure(fuzzy_threshold=6, safe_variants=True)
