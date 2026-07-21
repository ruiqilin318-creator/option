from etf_option_analyzer.models.market import OptionChain, OptionType


def normalize_chain(chain: OptionChain) -> OptionChain:
    calls = sorted([o for o in chain.calls if o.option_type is OptionType.CALL], key=lambda x: x.strike)
    puts = sorted([o for o in chain.puts if o.option_type is OptionType.PUT], key=lambda x: x.strike)
    return OptionChain(chain.symbol, chain.expiry, calls, puts, chain.meta)
