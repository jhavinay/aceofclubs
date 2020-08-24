if __name__ == "__main__":
    import find_src
    import re

import re
from core.position import Position
from core.partialhand import PartialHand
from core.hand import Hand
from core.suit import SPADES, HEARTS, DIAMONDS, CLUBS
from core.card import Card
from core.call import Call, Pass, Dbl, Rdbl

pattern_rdbl = re.compile('.*xx$')
pattern_dbl = re.compile('^[^x]*x$')


class AOCTranslate():
    suitmap = {0: CLUBS, 1: DIAMONDS, 2: HEARTS, 3: SPADES}
    ranks = range(13)
    rankstr = \
        ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    rankmap = dict(zip(ranks, rankstr))

    @classmethod
    def position(cls, pos):
        return Position.from_char(pos)

    @classmethod
    def hand(cls, handstring):
        return Hand.random()

    @classmethod
    def call(cls, callstring):
        if callstring == "ps":
            return Pass()
        elif pattern_rdbl.match(callstring):
            return Rdbl()
        elif pattern_dbl.match(callstring):
            return Dbl()
        else:
            return Call(callstring.upper())

    @classmethod
    def callstring(cls, call):
        if call == Pass():
            return "ps"
        elif call == Dbl():
            return "  x"
        elif call == Rdbl():
            return "  xx"
        else:
            return call.name.lower() + "  "

    # Given a card numbering from 0 (C2) to 52 (SA), get a card object
    @classmethod
    def card(cls, cardno):
        suit = AOCTranslate.suitmap[int(cardno/13)]
        rank = AOCTranslate.rankmap[cardno % 13]
        return Card(suit, rank)

    @classmethod
    def cardstr(cls, card):
        return 13 * card.suit.index + card.index()

    @classmethod
    def getHand(cls, cardnos):
        hand = PartialHand.empty()
        for c in cardnos:
            hand.addCard(cls.card(c))
        print(hand)
        assert hand.num_cards() == 13, "got {} cards in hand".format(
            hand.num_cards)
        return Hand.from_partial_hand(hand)

if __name__ == "__main__":
    assert AOCTranslate.callstring(Pass()) == "ps"
    assert re.match(AOCTranslate.callstring(Dbl()), '  x[^x]*')
    assert re.match(AOCTranslate.callstring(Rdbl()), '  xx$')

    assert AOCTranslate.card(0).name == "2C"
    assert AOCTranslate.card(12).name == "AC"
    assert AOCTranslate.card(15).name == "4D"
    assert AOCTranslate.card(25).name == "AD"
    assert AOCTranslate.card(26).name == "2H"
    assert AOCTranslate.card(38).name == "AH"
    assert AOCTranslate.card(51).name == "AS"

    assert AOCTranslate.cardstr(Card.card_from_char("AS")) == 51
    assert AOCTranslate.cardstr(Card.card_from_char("2C")) == 0

    print("Test for getHand")
    expected = "KJ8.AQ8754.Q4.QT"
    myhand = AOCTranslate.getHand(
        [50, 48, 45, 38, 36, 32, 31, 29, 28, 10, 8, 23, 15])
    handstr = myhand.shdc_dot_string()
    assert handstr == expected, "expected {}, got {}".format(
        expected, handstr)
    # Convert all card indices to card and get back the cards and make sure
    # that we get back the original
    for _ in range(52):
        c = AOCTranslate.card(_)
        ind = AOCTranslate.cardstr(c)
        assert _ == ind

    print("All tests for aoctranslate.py passed")
