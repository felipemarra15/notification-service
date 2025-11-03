from flask import Flask, request, jsonify

app = Flask(__name__)

@app.post("/notify")
def notify():
    data = request.get_json(force=True)
    print("[notify] recibido:", data)  # log para ver que llega
    return jsonify({"ok": True}), 200

if __name__ == "__main__":
    # podés cambiar el puerto con: export PORT=5001
    import os
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
