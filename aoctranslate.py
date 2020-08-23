import re
from core.position import Position
from core.hand import Hand
from core.call import Call, Pass, Dbl, Rdbl

pattern_rdbl = re.compile('.*xx$')
pattern_dbl = re.compile('^[^x]*x$')

class AOCTranslate():
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
