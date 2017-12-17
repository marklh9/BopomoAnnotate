import pickle


def get_syllable(ch):
    # 5bit
    InitialConsonants = "ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙ"
    # 2bit
    Medials = "ㄧㄨㄩ"
    # 4bit
    FinalConsonants = "ㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦ"
    # 3bit
    Tones = "ˊˇˋ˙"
    ic = ch & 0b11111
    m = (ch >> 5) & 0b11
    fc = (ch >> 7) & 0b1111
    t = (ch >> 11) & 0b111
    s = ''
    # print("%d %d %d %d" % (ic,m,fc,t))
    if t == 4:
        s += Tones[3];
    if ic != 0 and ic <= len(InitialConsonants):
        s += InitialConsonants[ic - 1]
    if m != 0 and m <= len(Medials):
        s += Medials[m - 1]
    if fc != 0 and fc <= len(FinalConsonants):
        s += FinalConsonants[fc - 1]
    if t != 0 and t <= len(Tones) - 1:
        s += Tones[t - 1]
    return s


class BopomoLookup:
    dictionary = None

    def __init__(self, location):
        file = open(location, 'rb')
        if BopomoLookup.dictionary is None:
            BopomoLookup.dictionary = pickle.load(file)
        file.close()

    def one(self, ideograph):
        return BopomoLookup.dictionary[ideograph][0]

    def all(self, ideograph):
        return BopomoLookup.dictionary[ideograph]

