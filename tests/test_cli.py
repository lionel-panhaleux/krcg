from krcg import cli


def test_help(capsys, twda):
    cli.execute([])
    assert (
        capsys.readouterr().out
        == """usage: krcg [-h] [-v N]  ...

VTES tool

optional arguments:
  -h, --help           show this help message and exit
  -v N, --verbosity N  0: errors, 1: warnings , 2: info, 3: debug

subcommands:
  
    init               initialize the local TWDA database
    affinity           display cards with the most affinity to given cards
    top                display top cards (played in most TW decks)
    build              build a deck
    deck               show TWDA decks
    card               show VTES cards
    complete           card name completion
    search             card search
    json               Format a decklist to JSON
"""  # noqa
    )


def test_card(capsys, twda):
    cli.execute(["card", "krcg"])
    assert (
        capsys.readouterr().out
        == """KRCG News Radio
[Master][2P] -- (Jyhad:U, VTES:U, CE:U, LoB:PA, LotN:PG, KoT:U/PB, SP:PwN1 - #101067)
Unique location.
Lock to give a minion you control +1 intercept. Lock and burn 1 pool to give a minion controlled by another Methuselah +1 intercept.

"""  # noqa
    )


def test_card_rulings(capsys, twda):
    cli.execute(["card", ".44 magnum"])
    assert (
        capsys.readouterr().out
        == """.44 Magnum
[Equipment][2P] -- (Jyhad:C, VTES:C, Sabbat:C, SW:PB, CE:PTo3, LoB:PO3, FB:PTr2, V5:PTr1 - #100001)
Weapon: gun.
Strike: 2R damage, with 1 optional maneuver each combat.

-- Rulings
Provides only ony maneuver each combat, even if the bearer changes. [LSJ 19980302-2]
The optional maneuver cannot be used if the strike cannot be used (eg. {Hidden Lurker}). [LSJ 20021028]

"""  # noqa
    )


def test_card_rulings_links(capsys, twda):
    cli.execute(["card", "-l", ".44 magnum"])
    assert (
        capsys.readouterr().out
        == """.44 Magnum
[Equipment][2P] -- (Jyhad:C, VTES:C, Sabbat:C, SW:PB, CE:PTo3, LoB:PO3, FB:PTr2, V5:PTr1 - #100001)
Weapon: gun.
Strike: 2R damage, with 1 optional maneuver each combat.

-- Rulings
Provides only ony maneuver each combat, even if the bearer changes. [LSJ 19980302-2]
The optional maneuver cannot be used if the strike cannot be used (eg. {Hidden Lurker}). [LSJ 20021028]
[LSJ 19980302-2]: https://groups.google.com/d/msg/rec.games.trading-cards.jyhad/9YVFkeiL3Js/4UZXMyicluwJ
[LSJ 20021028]: https://groups.google.com/g/rec.games.trading-cards.jyhad/c/g0GGiVIxyis/m/35WA-O9XrroJ

"""  # noqa
    )


def test_deck(capsys, twda):
    cli.execute(["deck", "Fame"])
    assert (
        capsys.readouterr().out
        == """-- 4 decks --
[2020bbpsp] Tariq Wall Rush 2.0
[2020oddffb] Weenie Animalismo
[2020rftgp] Enkidu Anarch
[2020adbfb] Tzismice - Augusto
"""
    )


def test_deck_display(capsys, twda):
    cli.execute(["deck", "2020bf3hf"])
    assert (
        capsys.readouterr().out
        == """[2020bf3hf      ]===================================================
Black Forest Base 3
Hyvinkää, Finland
September 5th 2020
2R+F
14 players
Niko Vanhatalo
http://www.vekn.net/event-calendar/event/9667

-- 1gw5 + 3vp in the final

Deck Name: My stick is better than bacon

Here is a quick report by the Winner of the event Niko Vanhatalo.

Just your average Ventrue grinder/stickmen with my own personal preferences

Finals were pretty brutal because every deck was a bleeder in some way or the
other and there was no clear winner even when it was down to 2 players.
Players from 1 to 5 were Petri with Anarch stealth bleeder, Jyrkkä with
Lasombra/Kiasyd stealth bleeder, Pauli with Ventrue grinder, me with my own
Ventrue grinder and Lasse with Legion and Legionnaire bleeder.  My biggest
concern was my predator who played pretty much the same deck with like 90% of
the crypt being the same cards, but we were able to avoid unnecesary contesting
thanks to table talk. He still contested my Lodin later in the game but was
ousted pretty fast after that before any real damage to me was done.

Crypt (12 cards, min=18, max=31, avg=6.17)
------------------------------------------
3x Lodin (Olaf Holte)   8 DOM FOR PRE aus pro  prince    Ventrue:5
2x Graham Gottesman     7 DOM FOR obf pre tha  prince    Ventrue:5
2x Victor Donaldson     6 DOM for pre          prince    Ventrue:5
1x Mustafa, The Heir    6 FOR PRE cel dom      prince    Ventrue:4
1x Claus Wegener        5 DOM aus for tha                Tremere:5
1x Emily Carson         5 DOM for pre          primogen  Ventrue:5
1x Jephta Hester        5 DOM FOR aus                    Ventrue antitribu:4
1x Ulrike Rothbart      3 dom for                        Ventrue antitribu:4

Library (88 cards)
Master (16; 5 trifle)
1x Anarch Troublemaker
1x Direct Intervention
1x Dreams of the Sphinx
1x Giant's Blood
1x Golconda: Inner Peace   -- Neat card, but never played. Should propably switch for another Dreams or Wash
1x Misdirection
1x Papillon
2x Pentex(TM) Subversion
2x Perfectionist
2x Vessel
2x Villein
1x Wash

Action (14)
1x Dominate Kine
2x Entrancement
11x Govern the Unaligned

Equipment (2)
2x Heart of Nizchetus

Political Action (4)
4x Parity Shift

Action Modifier (19)
2x Bonding
3x Conditioning
3x Daring the Dawn
4x Freak Drive
5x Seduction
2x Threats

Reaction (16)
8x Deflection
3x On the Qui Vive
4x Second Tradition: Domain
1x Wake with Evening's Freshness -- This should be another On the Qui Vive but I was too lazy to find 1 from my collection

Combat (17)
5x Hidden Strength
6x Indomitability
2x Rolling with the Punches
4x Weighted Walking Stick
"""  # noqa
    )


def test_deck_filters(capsys, twda):
    cli.execute(["deck", "--players", "20", "--from", "2020", "--to", "2021"])
    assert (
        capsys.readouterr().out
        == """-- 2 decks --
[2020smpdms] Lasombra Nocturns
[2020sbyckp] Better Call Saulot
"""
    )


def test_affinity(capsys, twda):
    cli.execute(["affinity", "Fame"])
    assert (
        capsys.readouterr().out
        == """Fame                           (in 100% of decks, typically 1-2 copies)
Powerbase: Montreal            (in 75% of decks, typically 1 copy)
On the Qui Vive                (in 75% of decks, typically 3-4 copies)
Anarch Convert                 (in 75% of decks, typically 4 copies)
The Parthenon                  (in 75% of decks, typically 2-3 copies)
Tension in the Ranks           (in 50% of decks, typically 1 copy)
Vessel                         (in 50% of decks, typically 4 copies)
Army of Rats                   (in 50% of decks, typically 1-2 copies)
Bowl of Convergence            (in 50% of decks, typically 1-2 copies)
Raven Spy                      (in 50% of decks, typically 4-8 copies)
Cats' Guidance                 (in 50% of decks, typically 3 copies)
Enhanced Senses                (in 50% of decks, typically 3 copies)
Eyes of Argus                  (in 50% of decks, typically 4-7 copies)
Sense the Savage Way           (in 50% of decks, typically 6-7 copies)
Telepathic Misdirection        (in 50% of decks, typically 5-8 copies)
Canine Horde                   (in 50% of decks, typically 1-2 copies)
Carrion Crows                  (in 50% of decks, typically 6-12 copies)
Drawing Out the Beast          (in 50% of decks, typically 4 copies)
Terror Frenzy                  (in 50% of decks, typically 5-6 copies)
Ashur Tablets                  (in 50% of decks, typically 9-12 copies)
Direct Intervention            (in 50% of decks, typically 1 copy)
Pentex™ Subversion             (in 50% of decks, typically 1 copy)
Wash                           (in 50% of decks, typically 1-2 copies)
Mr. Winthrop                   (in 50% of decks, typically 1 copy)
Forced Awakening               (in 50% of decks, typically 2-4 copies)
Diversion                      (in 50% of decks, typically 10-11 copies)
Taste of Vitae                 (in 50% of decks, typically 5 copies)
"""
    )


def test_top(capsys, twda):
    cli.execute(["top", "-d", "animalism"])
    assert (
        capsys.readouterr().out
        == """Cats' Guidance                 (played in 4 decks, typically 2-4 copies)
Sense the Savage Way           (played in 3 decks, typically 3-7 copies)
Carrion Crows                  (played in 3 decks, typically 5-11 copies)
Nana Buruku                    (played in 2 decks, typically 2-4 copies)
Army of Rats                   (played in 2 decks, typically 1-2 copies)
Raven Spy                      (played in 2 decks, typically 4-8 copies)
Canine Horde                   (played in 2 decks, typically 1-2 copies)
Drawing Out the Beast          (played in 2 decks, typically 4 copies)
Terror Frenzy                  (played in 2 decks, typically 5-6 copies)
Stanislava                     (played in 2 decks, typically 4-5 copies)
"""
    )


def test_search(capsys, twda):
    cli.execute(
        [
            "search",
            "--trait",
            "black hand",
        ]
    )
    assert (
        capsys.readouterr().out
        == """The Admonitions
The Art of Memory
Black Hand Emissary
Black Hand Ritual
Blooding
Bloodwork
Cadet
Census Taker
Chronicle of the Lost Tribe
Circumspect Revelation
... (103 results available, use the -n option)
"""
    )
    cli.execute(
        [
            "search",
            "--trait",
            "prince",
            "--clan",
            "Ventrue",
            "--group",
            "1",
            "--type",
            "vampire",
        ]
    )
    assert (
        capsys.readouterr().out
        == """Emerson Bridges
Sir Walter Nash
Timothy Crowley
"""
    )


def test_complete(capsys, twda):
    cli.execute(["complete", "Pentex"])
    assert (
        capsys.readouterr().out
        == """Pentex™ Loves You!
Pentex™ Subversion
Enzo Giovanni, Pentex Board of Directors
Enzo Giovanni, Pentex Board of Directors (ADV)
Harold Zettler, Pentex Director
"""
    )
