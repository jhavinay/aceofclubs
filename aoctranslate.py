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
from pcekbidder.callWithStateInfo import CallWithStateInfo
from core.callhistory import CallHistory

pattern_pass = re.compile('^\s*ps\s*$', re.I)
pattern_rdbl = re.compile('^\s*XX\s*$', re.I)
pattern_dbl = re.compile('^\s*X$', re.I)


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
    def call(cls, callstring, who):
        bidder = cls.position(who)
        if pattern_pass.match(callstring):
            return CallWithStateInfo(Pass(), bidder)
        elif pattern_rdbl.match(callstring):
            return CallWithStateInfo(Rdbl(), bidder)
        elif pattern_dbl.match(callstring):
            return CallWithStateInfo(Dbl(), bidder)
        else:
            return CallWithStateInfo(Call(callstring.upper()), bidder)

    @classmethod
    def callstring(cls, call):
        if call == Pass():
            return "ps  "
        elif call == Dbl():
            return "   X"
        elif call == Rdbl():
            return "  XX"
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

    @classmethod
    def getCalls(cls, bidsMade, dealno):
        return cls._getCallsAndAuction(bidsMade, dealno)[0]

    @classmethod
    def getAuction(cls, bidsMade, dealno):
        return cls._getCallsAndAuction(bidsMade, dealno)[1]

    @classmethod
    def _getCallsAndAuction(cls, bidsMade, dealno):
        tmp_auction = CallHistory.empty_for_board_number(dealno)
        allCalls = []
        for actions in bidsMade:
            (call, caller) = actions.split(sep=";")
            call = cls.call(call.strip(), caller.strip())
            allCalls.append(call)
            tmp_auction.append_call(call)
        return (allCalls, tmp_auction)

if __name__ == "__main__":
    assert AOCTranslate.callstring(Pass()) == "ps  "
    assert pattern_dbl.match(AOCTranslate.callstring(Dbl()))
    assert pattern_rdbl.match(AOCTranslate.callstring(Rdbl()))

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

    auctionstr = ["ps ;N", "ps ;E", "1H ;S", "  X;W", "ps ;N", "1S ;E"]
    auction = AOCTranslate.getAuction(auctionstr, 3)
    auction_string = auction.calls_string()
    expected = "P P 1H X P 1S"
    assert auction_string == expected, "expected {} got {}".format(
        expected, auction_string)
    print("All tests for aoctranslate.py passed")
