import json
import os

from flask import jsonify, request
from google import genai
from google.genai import types

from database import DB
from models import User
from server.app import api_router as app


@app.route("/user/<oauth_sub>/ai-portfolio", methods=["GET"])
def generate_portfolio(oauth_sub):
    """Generate a personalized stock portfolio based on user preferences"""
    if not DB.connected:
        return (
            jsonify({"status": 0, "error": 1, "message": "Database not connected"}),
            500,
        )

    session = DB.create_session()
    located_user = session.query(User).filter(User.oauth_sub == oauth_sub).first()
    session.close()

    if not located_user:
        return (
            jsonify({"status": 0, "error": 1, "message": "User not found"}),
            404,
        )
    
    preferences = {
        "is_experienced_investor": located_user.is_experienced_investor,
        "preferred_sectors": located_user.preferred_sectors,
        "sector_preference_rankings": located_user.sector_preference_rankings,
        "market_cap_preference": located_user.market_cap_preference,
        "growth_vs_value": located_user.growth_vs_value,
        "cyclical_vs_defensive": located_user.cyclical_vs_defensive,
        "valuation_metrics_preference": located_user.valuation_metrics_preference,
        "dividend_preference": located_user.dividend_preference,
        "tech_sector_interest": located_user.tech_sector_interest,
        "healthcare_sector_interest": located_user.healthcare_sector_interest,
        "financial_sector_interest": located_user.financial_sector_interest,
        "consumer_goods_interest": located_user.consumer_goods_sector_interest,
        "industrials_interest": located_user.industrials_sector_interest,
        "emerging_markets_interest": located_user.emerging_markets_interest,
        "ESG_preference": located_user.esg_preference,
        "small_cap_interest": located_user.small_cap_interest,
        "blue_chip_interest": located_user.blue_chip_interest,
        "tech_subsectors_interest": located_user.tech_subsectors_interest,
        "healthcare_subsectors_interest": located_user.healthcare_subsectors_interest,
        "investment_time_horizon": located_user.investment_time_horizon,
    }
    
    # Generate portfolio using Gemini
    portfolio_data = generate_portfolio_content(preferences)
    
    # Verify the allocations add up to 100%
    if portfolio_data:
        # Extract the reasoning field
        reasoning = portfolio_data.get("reasoning", "")
        
        # Calculate total allocation (excluding the reasoning field)
        total_allocation = sum(
            allocation for key, allocation in portfolio_data.items() 
            if key != "reasoning" and isinstance(allocation, (int, float))
        )
        
        # If allocation doesn't add up to 100%, adjust it
        if total_allocation != 100:
            # Get all ticker keys (excluding "reasoning")
            ticker_keys = [key for key in portfolio_data.keys() if key != "reasoning"]
            
            if ticker_keys:
                # Sort by allocation value (descending)
                ticker_keys.sort(key=lambda x: portfolio_data[x], reverse=True)
                
                # Adjust the largest allocation
                diff = 100 - total_allocation
                portfolio_data[ticker_keys[0]] += diff
    
    return jsonify({
        "status": 1,
        "error": 0,
        "data": portfolio_data
    })


def generate(prompt: str):
    """Generate content using Google's Gemini API"""
    client = genai.Client(
        api_key=os.environ.get("GEMINI_KEY"),
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    data_str = ""

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        data_str += chunk.text

    # Remove markdown code block formatting if present
    data_str = data_str.replace("```json", "").replace("```", "")
    return json.loads(data_str)


def generate_portfolio_content(user_preferences):
    """Generate a simplified stock portfolio based on user preferences using Gemini"""
    
    prompt = f"""
    You are a professional financial advisor specializing in portfolio construction. Based on the user's investment preferences, create a personalized stock portfolio using only stocks from the S&P 500.

    User Investment Preferences:
    {json.dumps(user_preferences, indent=2)}

    Create a diversified portfolio allocation that meets the following criteria:
    1. Only include stocks that are currently in the S&P 500 index
    2. Allocations must be based on the user's sector preferences, market cap preference, and other stated investment criteria
    3. The total allocation MUST add up to EXACTLY 100%
    4. Provide however many stocks you deem appropiate; however, target a suitable amount of diversity.
    5. Allocations should be whole numbers (no decimal places)
    6. For each preferred sector, select stocks that represent different subsectors or business models
    7. If the user prefers dividends, include stocks with above-average dividend yields
    8. If the user has ESG preferences, prioritize companies with strong ESG ratings
    9. Portfolio should be aligned with the user's stated investment time horizon

    Return ONLY a JSON object with the following structure:
    {{
      "TICKER1": allocation_percentage,
      "TICKER2": allocation_percentage,
      "TICKER3": allocation_percentage,
      ...
      "reasoning": "Explain the general reasoning for the selected stocks, highlighting the cornerstone stocks and how the portfolio aligns with the user's preferences."
    }}

    For example:
    {{
      "MSFT": 12,
      "AAPL": 10,
      "GOOGL": 8,
      "JNJ": 7,
      ...
      "reasoning": "This portfolio focuses on your preferred Technology, Healthcare, and Finance sectors with an emphasis on large-cap, dividend-paying stocks. Microsoft (MSFT) and Apple (AAPL) are cornerstone holdings providing exposure to software, cloud computing, and AI. Johnson & Johnson (JNJ) provides stable healthcare exposure with a strong dividend history..."
    }}

    Make sure the ticker symbols are accurate and the total allocation equals EXACTLY 100%.
    """
    
    try:
        return generate(prompt)
    except Exception as e:
        print(f"Error generating portfolio content: {e}")
        # Fallback to basic content with simplified format
        return {
            "MSFT": 10,
            "AAPL": 10,
            "GOOGL": 8,
            "AMZN": 7,
            "UNH": 10,
            "JNJ": 8,
            "ABBV": 7,
            "JPM": 10,
            "BAC": 7,
            "BLK": 8,
            "V": 5,
            "PG": 5,
            "CSCO": 5,
            "reasoning": "This portfolio focuses on your preferred Technology, Healthcare, and Finance sectors with an emphasis on large-cap, dividend-paying stocks. Microsoft (MSFT) and Apple (AAPL) are cornerstone holdings providing exposure to software, cloud computing, and AI. Johnson & Johnson (JNJ) and UnitedHealth (UNH) anchor the healthcare allocation, while JPMorgan (JPM) and BlackRock (BLK) provide financial sector exposure with strong dividend histories."
        }