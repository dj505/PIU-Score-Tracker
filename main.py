import json
import os

if not os.path.isfile("./data/scores.json"):
    with open("./data/scores.json", "a") as f:
        f.write("{}")

with open('./data/scores.json', 'r') as f:
    scores = json.load(f)

player = input("What's your name? ")
song = input("Song name? ")
type = input("Singeles or doubles? ")
diff = input("What's the difficulty? ")
score = input("What is your score? ")
grade = input("What is your grade? ")
stagepass = input("Did you stage pass? ")
max_combo = input("Max combo? ")
perfects = input("How many perfects? ")
greats = input("How many greats? ")
goods = input("How many goods? ")
bads = input("How many bads? ")
misses = input("How many misses? ")

scores = {player: {'song': song,
                  'type': type,
                  'difficulty': diff,
                  'score': score,
                  'grade': grade,
                  'stagepass': stagepass,
                  'maxcombo': max_combo,
                  'perfects': perfects,
                  'greats': greats,
                  'goods': goods,
                  'bads': bads,
                  'misses': misses
                  }}

with open("./data/scores.json", "w") as f:
    json.dump(scores, f, indent=4)
