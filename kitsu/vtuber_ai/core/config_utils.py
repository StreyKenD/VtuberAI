# Função para interpretar ações (ex: *giggle*, *wink*)
def interpret_action(acao):
    common_actions = {
        "wink": "teehee",
        "giggle": "hehe",
        "laugh": "haha",
        "sigh": "sigh",
        "blushes": "hmm",
        "shrugs": "ehh"
    }
    return common_actions.get(acao.lower(), "")

ARPABET_MAP = {
    "ah": "AA", "aw": "AO", "ay": "AY", "a": "AE", "ar": "AA R",
    "ee": "IY", "eh": "EH", "e": "EH", "er": "ER",
    "ih": "IH", "i": "IH", "ie": "IY",
    "oh": "OW", "ow": "AW", "oi": "OY", "o": "AA",
    "oo": "UW", "u": "UH", "uh": "AH",
    "b": "B", "ch": "CH", "d": "D", "f": "F", "g": "G", "h": "HH",
    "j": "JH", "k": "K", "l": "L", "m": "M", "n": "N", "ng": "NG",
    "p": "P", "r": "R", "s": "S", "sh": "SH", "t": "T", "th": "TH",
    "v": "V", "w": "W", "y": "Y", "z": "Z", "zh": "ZH"
}