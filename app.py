from flask import Flask, jsonify, request
import json
import time
import threading
import jwt

app = Flask(__name__)

SECRET_KEY = "secret_for_jwt"
JWT_EXPIRY = 5 * 3600  # 5 ساعات
JWT_TOKEN = None

# بيانات الحساب الضيف الثابتة
GUEST_ACCOUNT = {
    "guest_uid": "4034203948",
    "guest_password": "88BB561E6186A7C6A4D26102CB0FE0437C02D124182C249FFB72612CC4F8CFDD"
}


def generate_jwt(extra_payload=None):
    payload = {
        "iss": "wargood",
        "exp": time.time() + JWT_EXPIRY
    }
    if extra_payload:
        payload.update(extra_payload)
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def update_jwt_periodically():
    global JWT_TOKEN
    while True:
        JWT_TOKEN = generate_jwt()
        print(f"[+] Token updated: {JWT_TOKEN}")
        time.sleep(JWT_EXPIRY)


def fix_num(num):
    return str(num)


@app.route('/5', methods=['POST'])
def handle_skwad_5():
    try:
        data = request.data
        if not data:
            return jsonify({"error": "لم يتم إرسال أي بيانات"}), 400

        hex_head = data.hex()[0:4]

        if "1200" in hex_head and b"//5" in data:
            message = data.decode('utf-8', errors='ignore')
            unwanted_chars = ["(J,", "(J@", "(", ")", "@", ","]
            for ch in unwanted_chars:
                message = message.replace(ch, "")

            iddd = None
            try:
                parts = message.split()
                for part in parts:
                    if '//5' in part:
                        digits = ''.join(filter(str.isdigit, part.split('//5')[1]))
                        if digits:
                            iddd = int(digits)
                            break
                if iddd is None:
                    iddd = 10414593349
            except:
                iddd = 10414593349

            response = {
                "status": "success",
                "message": f"تم فتح سكواد 5 الى الاعب : {fix_num(iddd)}",
                "id": fix_num(iddd),
                "jwt": JWT_TOKEN
            }
            return jsonify(response), 200
        else:
            return jsonify({"error": "البيانات غير صالحة أو لا تحتوي على سكواد 5"}), 400

    except Exception as e:
        return jsonify({"error": "حدث خطأ في المعالجة", "details": str(e)}), 500


@app.route('/guest', methods=['GET'])
def guest_account():
    # يرجع بيانات الحساب + JWT جديد له
    guest_jwt = generate_jwt({"uid": GUEST_ACCOUNT["guest_uid"]})
    response = {
        "status": "success",
        "guest_uid": GUEST_ACCOUNT["guest_uid"],
        "guest_password": GUEST_ACCOUNT["guest_password"],
        "jwt": guest_jwt
    }
    return jsonify(response), 200


if __name__ == "__main__":
    JWT_TOKEN = generate_jwt()
    t = threading.Thread(target=update_jwt_periodically)
    t.daemon = True
    t.start()
    app.run(host="0.0.0.0", port=5000)
