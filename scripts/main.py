
import json
from itertools import groupby

from domain import Character
from domain.combat import fight

with open('sample.json') as file:
    players = json.load(file)

players = [Character(**p) for p in players]
teams = [list(t[1]) for t in groupby(players, key=lambda p: p.team)]

fight(*teams)
