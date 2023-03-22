import json
import os

world = input("World: ")
level = input("Level: ")
info = {}
filepath = "./tiled level jsons/{}/level{}.json".format(world,level)
with open(filepath,"r") as file:
    data = json.load(file)
    info["world"] = world
    info["level"] = level
    info["backgroundColor"] = data["backgroundcolor"]
    info["height"] = data["height"]
    info["width"] = data["width"]
    info["tileScale"] = data["tilewidth"]
    info["sky"] = "./levels/{}/level{}/level{}_sky.csv".format(world,level,level)
    info["background"] = "./levels/{}/level{}/level{}_background.csv".format(world,level,level)
    info["ground"] = "./levels/{}/level{}/level{}_ground.csv".format(world,level,level)
    info["renderOnTop"] = "./levels/{}/level{}/level{}_renderOnTop.csv".format(world,level,level)
    for layer in data["layers"]:
        if layer["name"] == "zones":
            zones = []
            for obj in layer["objects"]:
                zone = {}
                zone["name"] = obj["name"]
                zone["x"] = obj["x"]
                zone["y"] = obj["y"]
                zone["width"] = obj["width"]
                zone["height"] = obj["height"]
                zone["theme"] = obj["properties"][0]["value"]
                zone["music"] = obj["properties"][1]["value"]
                zones.append(zone)
            info["zones"] = zones
        elif layer["name"] == "spawns":
            info["spawns"] = layer["objects"]
filepath2 = "./levels/{}/level{}.json".format(world,level)
with open(filepath2,"w",encoding="utf-8") as file:
    json.dump(info,file,indent=4)
