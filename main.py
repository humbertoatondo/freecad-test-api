from flask import Flask, request
from flask_cors import CORS
import base64
import ast
import sys
sys.path.append("/etc/alternatives/freecadlib")
import FreeCAD
import Part
import Mesh
import MeshPart

# sudo ln -s /usr/lib/freecad/Mod /usr/lib/freecad-python3/Mod

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def hello():
    return "Hello World!"

@app.route("/glb", methods=["POST"])
def receive_file(**kwargs):

    print(request.data)
    dict_str = request.data.decode("UTF-8")
    dict_data = ast.literal_eval(dict_str)

    print(dict_data["file"])

    bytes_file = base64.b64decode(dict_data["file"])

    # print(bytes_file)

    f = open("/workspaces/freecad-backend/server-test.stp", "wb")
    f.write(dict_data["file"])
    f.close()

    return "Received"


@app.route("/step", methods=["POST"])
def receive_step_file(**kwargs):
    dict_str = request.data.decode("UTF-8")
    dict_data = ast.literal_eval(dict_str)

    print("WRITING")

    f = open("/workspaces/freecad-backend/server-test.stp", "w")
    f.write(dict_data["file"])
    f.close()

    print("SHAPE READ")

    shape = Part.Shape()
    shape.read("/workspaces/freecad-backend/server-test.stp")
    # doc = FreeCAD.newDocument("Doc")
    # pf = doc.addObject("Part::Feature", "MyShape")
    # pf.Shape = shape
    # v = Mesh.export([pf], "/workspaces/freecad-backend/my_shape.stl")

    print("WRITE FROM MESH")

    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.95, Segments=True)
    mesh.write(Filename="/workspaces/freecad-backend/my_shape.stl", Format="stl")

    print("OPEN AND BASE64")

    file_out = open("/workspaces/freecad-backend/my_shape.stl", "rb")
    file_out_base64 = base64.b64encode(file_out.read())
    file_out_base64_str = file_out_base64.decode("UTF-8")
    print(str(file_out_base64)[0:30])
    print(file_out_base64_str[0:30])
    file_out.close()

    response = {
        "file": "data:application/octet-stream;base64," + file_out_base64_str,
        "type": ".stl",
    }

    return response


if __name__ == '__main__':
    # flask run --host 0.0.0.0
    app.run(host="0.0.0.0")