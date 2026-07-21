from etf_option_analyzer.providers.mock import MockProvider
from etf_option_analyzer.reporting.markdown import render_report

if __name__ == "__main__":
    print(render_report(MockProvider().fetch_snapshot("510050"), "long"))
