from intentManipulation.intentTypes.baseIntent import BaseIntent
from intentManipulation.intentTypes.replies import Replies, Types


class InstantFallbackIntent(BaseIntent):
    def getIntentType(self):
        return Types.FALLBACK

    def getChangeIntent(self):
        return self.reply["fallbackIntent"]

    def _produceFirstSentence(self):
        return self.reply["main"]

    def parseIncomingMessage(self, message: str):
        # sourcery skip: assign-if-exp, swap-if-expression
        if not self.alreadyWelcomed:
            return self.sendFirstMessage()
        return {"changeIntent": Replies.MENU}


def __main():
    fbi = InstantFallbackIntent(Replies.MENU)
    return


if __name__ == "__main__":
    __main()
