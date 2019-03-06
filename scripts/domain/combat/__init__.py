
import random

def fight(*teams):
    players = {}
    for team in teams:
        oponents = [p for t in teams if t != team for p in t]
        for char in team:
            players[char.name] = {
                'char': char,
                'team': team,
                'initiative': random.randint(1, 20) + char.modif('agi'),
                'oponents': oponents,
            }

    commandList = {
        'hit': hitCmd,
        'auto': autoCmd,
        'overview': overviewCmd,
        'run': runCmd,
        '': autoCmd,
    }

    order = sorted(players.values(), key=lambda x: x['initiative'])
    while True:
        for player in order:
            if player['char'].stats['disabled']:
                continue

            player['char'].restore('balance')
            print('%s`s turn!\n' % player['char'].name)
            print('Player:', player['char'])

            while True:
                cmd = ['auto']
                if player['char'].isPlayer:
                    cmd = input(
                        '\nCommands:\n' +
                        '  hit [Name]\n' +
                        '  overview\n' +
                        '  run\n\n'
                    )
                    cmd = cmd.split(' ')

                if cmd[0] in commandList:
                    action = commandList[cmd[0]]
                    try:
                        result = action(player, players, teams, cmd[1:])
                        if result == 'retry':
                            continue
                        if result == 'exit':
                            return
                        break
                    except Exception as e:
                        print(e)

            if fightIsOver(teams):
                return

            input('Hit enter for next turn...\n')

def fightIsOver(teams):
    teamsAlive = 0
    for team in teams:
        for char in team:
            if not char.stats['disabled']:
                teamsAlive += 1
                break

    return teamsAlive == 1

##
# Actions:
#

def autoCmd(player, players, teams, args):
    oponent = random.choice(
        [op for op in player['oponents'] if not op.stats['disabled']]
    )

    hitCmd(player, players, teams, [oponent.name])

    return 'ok'


def hitCmd(player, players, teams, args):
    if len(args) < 1 or type(args[0]) != str or args[0] not in players:
        raise Exception('Invalid or missing target name for `hit` command: %s' % args)
    oponent = players[args[0]]['char']
    print('Oponent chosen:', oponent)

    attack = player['char'].attack()
    print('\nAttack:', attack)
    if attack['hit_chance'] >= 12:
        result = oponent.defend(attack['dmg'])
        if type(result) != int:
            print('Successful hit but it was', result)
        else:
            print('Successful hit of', result)
        if oponent.stats['disabled']:
            print(oponent.name, 'is DOWN!')
    else:
        print('Missed!')
    print()

    return 'ok'

def overviewCmd(player, _players, teams, _args):
    print('\nTeams:')
    for team in teams:
        print(team)
    print()

    return 'retry'

def runCmd(player, _players, teams, _args):
    list(teams).remove(player['team'])

    return 'exit'
