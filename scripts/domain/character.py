
import random
import re

class Character:
    attrNames = [
        'dex',
        'agi',
        'int',
        'vit',
        'str',
    ]

    def __init__(self, name, isPlayer=False, weapons=[], armor=0, **kw):
        self.name = name
        self.isPlayer = isPlayer
        self.attrs = Character.distributeAttributes(kw, 25)
        self.weapons = [w for wstr in (weapons or ['1d4']) for w in Character._parseWeapon(wstr)]
        self.armor = armor
        self.stats = self.defaultStats()
        self.team = kw.pop('team', 'players' if isPlayer else 'monsters')

    def attack(self, dices=[]):
        if self.stats['disabled']:
            return {'hit_chance': 0, 'dmg': 0}

        if dices:
            if len(dices[1:]) != len(self.weapons):
                raise Exception(
                    'unexpected number of dices (%s), expected %s' % (
                        dices,
                        ['1d%s' % w for w in [20] + self.weapons],
                    )
                )

            return {
                'hit_chance': int(dices[0]),
                'dmg': sum([int(d) for d in dices[1:]]),
            }

        hit = random.randint(1,20)
        dmg = 0
        for maxDmg in self.weapons:
            dmg += random.randint(1, maxDmg)

        return {'hit_chance': hit, 'dmg': dmg}

    def defend(self, dmg, dodge=True):
        if dodge:
            if dmg <= self.stats['balance']:
                self.stats['balance'] -= dmg
                return 'dodged'

            dmg -= self.stats['balance']
            self.stats['balance'] = 0

        dmg -= self.armor
        if dmg <= 0:
            return 'blocked'

        self.stats['hp'] -= dmg

        self.stats['disabled'] = self.stats['hp'] <= 0
        self.stats['dead'] = self.stats['hp'] <= -self.attrs['vit']

        return dmg

    def dispute(self, attrName):
        offset = self.modif(attrName)
        return random.randint(1, 8) + offset

    def restore(self, stat='all'):
        if stat == 'all':
            self.stats = self.defaultStats()
        else:
            self.stats[stat] = self.defaultStats()[stat]

    def defaultStats(self):
        return {
            'balance': self.attrs['agi'],
            'mana': self.attrs['int'],
            'hp': self.attrs['vit'],
            'disabled': False,
            'dead': False,
        }

    def modif(self, attrName, avgPts=5):
        return self.attrs[attrName]-avgPts

    @staticmethod
    def distributeAttributes(baseAttrs, points, minPts=3, maxPts=8):
        attrs = {k: baseAttrs[k] for k in Character.attrNames if k in baseAttrs}
        missing = [x for x in Character.attrNames if x not in baseAttrs]

        for k in attrs:
            points -= attrs[k]

        if points < minPts*len(missing):
            raise Exception('Not enough points to produce a valid character!')

        if points > maxPts*len(missing):
            raise Exception('Too much points to produce a valid character!')

        for k in missing:
            attrs[k] = minPts
            points -= minPts

        while points > 0:
            key = random.choice(missing)
            attrs[key] += 1
            points -= 1
            if attrs[key] == maxPts:
                missing.remove(key)

        return attrs

    @staticmethod
    def _parseWeapon(s):
        match = re.match('(\d*)d(\d+)', s)
        if not match:
            raise Exception("invalid weapon received: '%s'" % s)

        numDices = int(match.group(1) or '1')
        dice = int(match.group(2))

        if dice > 12 or dice < 4 or dice % 2 != 0:
            raise Exception("invalid dice for use as a weapon: '%s'" % s)

        return numDices * [dice]

    def __repr__(self):
        return str(self)

    def __str__(self):
        weaponsStr = {
            4: '1d4',
            6: '1d6',
            8: '1d8',
            10: '1d10',
            12: '1d12',
        }

        return '{\n  "name": "%s",\n  "attrs": %s,\n  "weapons": %s,\n  "armor": %s,\n  "stats": %s\n}' % (
            self.name,
            self.attrs,
            [weaponsStr[w] for w in self.weapons],
            self.armor,
            self.stats,
        )
