class Ledger:
    _RATES = {
        "chatgpt-4o-latest":                  (0.005,   0.015),
        "gpt-4o-mini":                        (0.00015, 0.0006),
        "o3-mini":                            (0.0011,  0.0044),
        "gpt-4o":                             (0.0025,  0.01),
        "claude-3-7-sonnet-20250219":         (0.003,   0.015),
        "claude-sonnet-4-20250514":           (0.003,   0.015),
        "gpt-4o-search-preview":              (0.0025,  0.01),
        "deepseek-reasoner":                  (0.00055, 0.00219),
        "gemini-1.5-pro":                     (0.00125, 0.005),
        "gemini-2.0-flash-thinking-exp-01-21":(0.0001,  0.0004),
        "mistral-large-latest":               (0.002,   0.006),
    }

    def __init__(self):
        self.__purse = 0

    def tally(self, influx, outflux, breed):
        rate = self._RATES.get(breed)
        if rate is None:
            raise ValueError("Model name not recognized. Token cost not calculated.")
        ic, oc = rate
        self.__purse += (influx / 1000) * ic + (outflux / 1000) * oc

    def balance(self):
        return self.__purse

    def wipe(self):
        self.__purse = 0
