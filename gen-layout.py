


import os, json
from pathlib import Path

COMPONENTS = ["handlers","services","models","ports","adapters","other"]

def walk_layout():
    layers = ["surface","domain","infrastructure","domain"]
    found = {}
    root_dir = Path(__file__).resolve().parent.parts[-1]
    for layer in layers:
        layer_path = Path(root_dir).joinpath(layer)
        if os.path.isdir(layer_path):
            comps = {"handlers":[],"services":[],"models":[],"ports":[],"adapters":[],"other":[]}
            for root, dirs, files in os.walk(layer_path):
                for f in files:
                    if f.endswith(".py") and not f.startswith("__"):
                        path = os.path.join(root,f)
                        filepath = Path(path)
                        parent = filepath.parent.parts[-1]
                        if parent in COMPONENTS:
                            comps[str(parent)].append(path)
                        else:
                            comps["other"].append(path)
            for k in comps: comps[k].sort()
            found[layer] = comps
    print(json.dumps(found, indent=2))

def main():
    walk_layout()

if __name__ == "__main__":
    main()
