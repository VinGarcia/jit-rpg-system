
from domain import Character
from domain.combat import fight

monster = Character(
    name='Zim',
    weapons=[1, 2],
)

player = Character(
    name='Fox',
    weapons=[2, 2],
    isPlayer=True,
)

fight([player], [monster])
