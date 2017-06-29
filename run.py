from flask import Flask, request, jsonify
from config_manager import read_conf, write_conf
import cv2
import numpy as np
import io
app = Flask(__name__)


@app.route("/config", methods=["POST", "GET"])
def config():
    if request.method == "GET":
        return jsonify(read_conf())
    else:
        write_conf(request.get_json())
        return jsonify(read_conf())

@app.route("/process", methods=["POST"])
def process():
    img = request.data
    mime = request.headers.get("content-type")
    in_memory_file = io.BytesIO()
    in_memory_file.write(img)
    data = np.fromstring(in_memory_file.getvalue(), dtype=np.uint8)
    color_image_flag = 1
    img = cv2.imdecode(data, color_image_flag)
    cv2.imshow("img", img)
    cv2.waitKey()
    return "1"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True, threaded=True)
