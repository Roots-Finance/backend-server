from flask import jsonify

from server.app import api_router as app


@app.route("/test", methods=["GET"])
def test():
    """
    Defines the test API route for the Flask app.
    Upon receiving a GET request, it will return 418.

    Returns:
        A JSON response with a status code of 418.

    """
    return jsonify({"status": 1, "error": 0, "message": "It works!"}), 418
