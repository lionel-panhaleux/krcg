from src import twda


def test_get_card():
    assert twda._get_card("deny") == ("deny", 1)
    assert twda._get_card("2 deny") == ("deny", 2)
    assert twda._get_card("deny 2") == ("deny", 2)
    assert twda._get_card("2x deny") == ("deny", 2)
    assert twda._get_card("2 x deny") == ("deny", 2)
    # 'x' is usually separated from card name, but '*' may not be
    assert twda._get_card("2*deny") == ("deny", 2)
    assert twda._get_card("deny *2") == ("deny", 2)
    assert twda._get_card("deny x2") == ("deny", 2)
    assert twda._get_card("deny x 2") == ("deny", 2)
    assert twda._get_card("deny (2)") == ("deny", 2)
    assert twda._get_card("deny [2]") == ("deny", 2)
    # many forms are used, with or without parenthesis, 'x', '=', etc.
    assert twda._get_card("deny (x2)") == ("deny", 2)
    assert twda._get_card("deny =2") == ("deny", 2)
    assert twda._get_card("deny /2") == ("deny", 2)
    # crypt needs special handling as we got a number in front and back
    assert twda._get_card("2x anvil			6   cel pot dom pre tha	 primogen  brujah:1") == (
        "anvil",
        2,
    )
    # names beginning with an 'x' and parenthesied '(adv)' must be correctly matched
    assert twda._get_card(
        "2x xaviar (adv)		10  abo ani for pro aus cel pot	 gangrel:3"
    ) == ("xaviar (adv)", 2)
    # names beginning with a number are hard
    assert twda._get_card("2nd tradition") == ("2nd tradition", 1)
    # name ending with a number even harder
    assert twda._get_card("ak-47") == ("ak-47", 1)
    # channel 10 is unique: other cards will match 10 as the count
    assert twda._get_card("channel 10") == ("channel 10", 1)
    # pier 13 is hard to match fully, note there is no ',' atter card counts
    assert twda._get_card("2 pier 13, port of baltimore") == (
        "pier 13, port of baltimore",
        2,
    )
    # local 1111 is hard, card counts have less than 3 digits
    assert twda._get_card("local 1111 2") == ("local 1111", 2)
    assert twda._get_card("1x alia, god=92s messenger") == (
        "alia, god=92s messenger",
        1,
    )
