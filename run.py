from flask import Flask, request, jsonify, abort
from config_manager import read_conf, write_conf
import cv2
import numpy as np
import os
import cv
app = Flask(__name__, static_folder='ui')


@app.route("/config", methods=["POST", "GET"])
def config():
    if request.method == "GET":
        return jsonify(read_conf())
    else:
        write_conf(request.get_json())
        return jsonify(read_conf())


@app.route("/refresh", methods=["POST"])
def refresh():
    path = os.path.join(os.getcwd(), "ui", "img")
    image_path = os.path.join(path, "input_image")

    img = cv2.imread(image_path, 1)
    # convert format
    try:
        processed, data = cv.process(img)
    except:
        abort(500)
    cv2.imwrite(os.path.join(path, "output.jpg"), processed)
    return jsonify(data)


@app.route("/process", methods=["POST"])
def process():
    img = request.files['file']
    path = os.path.join(os.getcwd(), "ui", "img")
    image_path = os.path.join(path, "input_image")
    img.save(image_path)

    img = cv2.imread(image_path, 1)
    # convert format
    cv2.imwrite(os.path.join(path, "input.jpg"), img)
    try:
        processed, data = cv.process(img)
    except BaseException as err:
        print(err)
        abort(500)
    cv2.imwrite(os.path.join(path, "output.jpg"), processed)
    return jsonify(data)


@app.route('/')
def index():
    return app.send_static_file("index.html")


@app.route('/<path:path>')
def static_files(path):
    return app.send_static_file(path)


if __name__ == '__main__':
    app.config.update(
        PROPAGATE_EXCEPTIONS=True
    )
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

