import json
from fastapi import Request  # used only for type hinting
from logger.logger import Logger
from flask import Flask, jsonify, request
from backend.rag_engine import ask as run_ask
from backend.data_processing import DataProcessing
from backend.models import AskRequest, AskResponse


logger = Logger.get_instance()
# loading config file
logger.info(f"Loading config file")
try:
    config = json.load(open("config/config.json"))
except FileNotFoundError as e:
    logger.warning(f"Config file not found; exception: {str(e)}")

app = Flask(__name__)

# ------------------------------------------------------------------
# Health‑check
# ------------------------------------------------------------------
@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    return jsonify({"status": "ok"}), 200

# ------------------------------------------------------------------
# /ask endpoint
# ------------------------------------------------------------------
@app.route("/ask", methods=["POST"])
def ask():
    # Pydantic validation
    req = AskRequest.model_validate_json(request.get_data())
    answer, sources = run_ask(req.question)

    resp = AskResponse(answer=answer, sources=sources)
    return resp.model_dump_json()

# ------------------------------------------------------------------
# Boilerplate
# ------------------------------------------------------------------
if __name__ == "__main__":
    # make sure Ollama is running before you start the server
    os.environ["OLLAMA_API_URL"] = config["ollama_url"]
    DataProcessing().launch_processing()
    app.run(host="0.0.0.0", port=5000, debug=True)