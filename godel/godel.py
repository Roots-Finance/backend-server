import json
from datetime import datetime
from typing import Dict, List

import requests

from godel.article import Article

# Define a custom type for a response containing news articles categorized by tickers.
#
# `NewsResponse` is a dictionary where:
# - The keys are ticker symbols (e.g., "AAPL", "GOOGL", "MSFT"), represented as strings.
# - The values are lists of `Article` objects, each representing a news article related to the ticker.
#
# This type is useful for organizing news data where each ticker symbol has a collection
# of articles associated with it. For example, news articles related to Apple (AAPL)
# can be stored in the list under the "AAPL" key.
#
# Example:
# news_response = {
#     "AAPL": [Article(title="New iPhone Launch"...)],
#     "GOOGL": [Article(title="Google AI Innovation"...)]
# }
type NewsResponse = Dict[str, Dict[str, List[Article]]]


class Godel:
    def __init__(self):
        pass

    @staticmethod
    def queryNews(tickers: List[str], startDate: str, endDate: str) -> NewsResponse:
        """Queries Godel Terminal for news articles about a given list
        of tickers, starting from a specific date, and ending at a specific date.
        start/endDate format: 09-20-2003 -> September 20, 2003

        Args:
            tickers (List[str]): The list of tickers to request news for.
            startDate (str): The start date to begin looking for news.
            endDate (str): The cutoff date to stop looking for news.

        Returns:
            NewsResponse: An object containing tickers mapping to a list of Articles.

        """
        start = (
            datetime.strptime(startDate, "%m-%d-%Y").strftime("%Y-%m-%dT%H:%m:%S.")
            + "000Z"
        )
        end = (
            datetime.strptime(endDate, "%m-%d-%Y").strftime("%Y-%m-%dT%H:%m:%S.")
            + "000Z"
        )
        postBody = {
            "size": 10000000,
            "start": start,
            "end": end,
            "beforeCursor": None,
            "sources": [
                "Business Wire",
                "PR Newswire",
                "Forbes Inc.",
                "The Washington Post",
                "Moodys",
                "24-7 Press Release",
                "3BL Media",
                "AB Digital",
                "Access Intelligence",
                "Accesswire",
                "ACI Information Group",
                "Acquisdata",
                "Action Economics",
                "Actusnews",
                "Advance Publications, Inc.",
                "Adweek",
                "African Press Organization",
                "Agence France Presse",
                "AHC Media LLC",
                "All Africa Global Media",
                "Alliance News",
                "APN New Zealand Ltd",
                "ARKA News Agency",
                "ARR News Story",
                "Asia Business News",
                "Associated Press, The",
                "Atlantic Media",
                "Australian Associated Press",
                "Austria Press Agentur",
                "Autovia",
                "Baystreet.ca",
                "Benzinga",
                "Black Press Group",
                "Blockchain Wire",
                "bne IntelliNews",
                "BNK Invest",
                "Boston Globe, The",
                "Breaking Media",
                "BridgeTower Media",
                "British Broadcasting Corporation - BBC Monitoring",
                "Canada Newswire",
                "Canadian Press, The",
                "Canjex Publishing Ltd",
                "Cision",
                "City AM",
                "ContentEngine",
                "CryptoQuant",
                "Dennis Publishing",
                "Dig Media",
                "dpa-AFX",
                "dpa Deutsche Presse-Agentur GmbH",
                "DVV Media Group",
                "Economist Intelligence Unit",
                "Edison Investment Research Limited",
                "EFE News Service",
                "Elsevier CBNB",
                "Endeavor",
                "Federal Information & News Dispatch, Inc.",
                "Forkast",
                "Foundry",
                "Gale Group",
                "Gannett Media Corp",
                "GlobeNewswire",
                "GO Media",
                "Government Executive Media Group",
                "Hearst",
                "Hong Kong Free Press",
                "HT Media",
                "iCrowdNewswire",
                "Independent Digital News and Media",
                "Independent News and Media",
                "Independent Newspapers Limited",
                "Informatics India Limited",
                "Information Solutions",
                "InPublic - GlobeNewswire",
                "Inside Washington Publishers",
                "Interfax America Inc.",
                "Interfax-Ukraine",
                "Inter Press Service",
                "InvestorBrandNetwork",
                "Itar-Tass",
                "Japan Corporate News",
                "Johnston Press",
                "Kabar",
                "Kyiv Independent",
                "Kyodo News International, Inc.",
                "M2 Communications",
                "Market Exclusive",
                "MarketLine",
                "M-Brain Oy",
                "Media-OutReach",
                "Medqor",
                "Metropolis Business Media",
                "MJH Life Sciences",
                "Modular Finance",
                "Mondaq",
                "Multimedia Investments Ltd",
                "National Journal Group",
                "Networld Alliance",
                "NewMediaWire",
                "NewsBank",
                "News Data Service",
                "News Direct",
                "Newsfile Corp",
                "NewsRx.com",
                "New Straits Times",
                "NewsUSA",
                "NewsVoir",
                "Nordot",
                "NTB Norway",
                "Omniearth",
                "OMX",
                "Orbit Financial Technology Limited",
                "Oslo Bors ASA",
                "OTC PR Wire",
                "Pakistan Press International",
                "Pedia Content Solutions",
                "Penton Business Media",
                "People Support Transcription & Captioning",
                "Plus Media Solutions Pakistan",
                "Polish Press Agency",
                "PR.com",
                "Pressat",
                "PRISM Mediawire",
                "ProQuest Information & Learning",
                "PR Web",
                "Public Technologies",
                "Publishers Weekly",
                "Questex",
                "ReleaseWire",
                "Reportable",
                "Ritzau Denmark",
                "Roy Morgan International Limited",
                "Russell Publishing",
                "San Francisco Chronicle",
                "Schaeffers Investment Research",
                "SeeNews",
                "Sightline Media Group",
                "Solo Syndication Ltd.",
                "South American Business Information",
                "SPH Media",
                "Sports Business Journal",
                "STT Info Finland",
                "SyndiGate Media Inc.",
                "Targeted News Service",
                "Tenders",
                "Thai News Service",
                "The Content Exchange",
                "The Logic",
                "The New Republic",
                "TheNewswire.ca",
                "The Press Association UK",
                "TipRanks",
                "Trend News Agency",
                "Tribune Content Agency",
                "TT News Agency Sweden",
                "UKRINFORM",
                "Uloop",
                "United Press International",
                "Vietnam News Agency",
                "William Reed Business Media",
                "Winnipeg Free Press Co. Ltd.",
                "WPS USA Inc.",
                "Xinhua News Agency",
                "Yonhap News Agency",
                "Zack Investment Research",
                "Zinio",
            ],
            "languages": ["en"],
            "afterCursor": None,
            "symbols": tickers,
        }

        news_object = {ticker: {} for ticker in tickers}

        # response = requests.post(
        #     "https://api.godelterminal.com/api/paged/news",
        #     json.dumps(postBody),
        #     headers={"Content-Type": "application/json"},
        # )

        newBody = {
            "pageable": {"size": 10000000, "afterCursor": None, "beforeCursor": None},
            "languages": ["en"],
            "symbols": tickers,
            "dateTimeRange": {"startTime": start, "endTime": end},
        }

        newBody = {
            "pageable": {"size": 200, "afterCursor": None, "beforeCursor": None},
            "languages": ["en"],
            "symbols": [
                "PLTR",
                "BRK.B",
                "IBM",
                "BIBL",
                "CATX",
                "AMD",
                "JPM",
                "AMGN",
                "TSLA",
                "NVDA",
                "MSFT",
                "AAPL",
                "GOOGL",
                "JNJ",
                "GOOG",
                "UNH",
                "META",
                "WMT",
                "MA",
                "V",
                "ET",
                "TLT",
                "BAC",
                "PFE",
                "MRK",
                "CMG",
                "MCD",
                "SPY",
                "TPST",
                "AMZN",
                "F",
                "MU",
                "WBD",
                "ABEO",
                "MIST",
                "VRNA",
            ],
            "dateTimeRange": {"startTime": 0, "endTime": 1743324923563},
        }

        response = requests.post(
            "http://api.godelterminal.com/api/news/items",
            json.dumps(newBody),
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Referer": "https://app.godelterminal.com/",
                "Content-Type": "application/json",
                "Origin": "https://app.godelterminal.com",
                "DNT": "1",
                "Sec-GPC": "1",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Priority": "u=0",
                "TE": "trailers",
                "X-Forwarded-For": "89.42.215.203",
                "X-Real-IP": "89.42.215.203",
            },
            # proxies={
            #     "http": "http://127.0.0.1:8082",
            #     "https": "https://127.0.0.1:8082",
            # },
            verify=False,
        )

        print(response.text)

        print(response.json())
        response_obj = response.json()["content"]

        for article in response_obj:

            for security_ticker in article["securityIds"]:
                if security_ticker in news_object:
                    parsed = Article(
                        security_ticker,
                        article["providerName"],
                        article["key"],
                        article["publicationTime"],
                        article["title"],
                        article["description"],
                    )
                    article_dt = datetime.strptime(
                        parsed.publicationTime, "%Y-%m-%dT%H:%M:%SZ"
                    ).strftime("%Y-%m-%d")
                    if article_dt not in news_object[security_ticker]:
                        news_object[security_ticker][article_dt] = []
                    news_object[security_ticker][article_dt].append(parsed)

        return news_object
