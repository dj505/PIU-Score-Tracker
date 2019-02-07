import json
import os

if not os.path.isfile("./data/scores.json"):
    with open("./data/scores.json", "a") as f:
        f.write("{}")

with open('./data/scores.json', 'r') as f:
    scores = json.load(f)

name = input("Name: ")
scores[name] = {}
scores[name]['song'] = input("Song name: ")
scores[name]['type'] = input("Chart type: ")
scores[name]['difficulty'] = input("Difficulty: ")
scores[name]['score'] = input("Score: ")
scores[name]['grade'] = input("Letter grade: ")
scores[name]['pass'] = input("Stage pass: ")
scores[name]['maxcombo'] = input("Max combo: ")
scores[name]['perfects'] = input("Perfects: ")
scores[name]['greats'] = input("Greats: ")
scores[name]['goods'] = input("Goods: ")
scores[name]['bads'] = input("Bads: ")
scores[name]['misses'] = input("Misses: ")

with open("./data/scores.json", "w") as f:
    json.dump(scores, f, indent=4)
