# battle.py
import random
from pokemon import Pokemon

class Battle:
    def __init__(self, pokemon1, pokemon2):
        self.pokemon1 = pokemon1
        self.pokemon2 = pokemon2
        self.turn = 0
        self.log = ["A batalha começou!"]

    @property
    def attacker(self):
        return self.pokemon1 if self.turn % 2 == 0 else self.pokemon2

    @property
    def defender(self):
        return self.pokemon2 if self.turn % 2 == 0 else self.pokemon1

    def execute_turn(self, move_name):
        move = next((m for m in self.attacker.moves if m.name == move_name), None)
        if not move:
            self.log.append(f"{self.attacker.name} tentou usar um golpe que não conhece!")
            return

        log_entry = f"{self.attacker.name} usou {move.name.capitalize()}!"
        
        if move.damage_class == 'status':
            for stat_change in move.stat_changes:
                stat = stat_change['stat']['name']
                change = stat_change['change']
                if stat in self.attacker.stats:
                    boost = int(self.attacker.stats[stat] * (0.25 * change))
                    self.attacker.stats[stat] = max(1, self.attacker.stats[stat] + boost)
                    log_entry += f" O {stat} de {self.attacker.name} aumentou!"
        else:
            damage = int(((self.attacker.stats['attack'] / self.defender.stats['defense']) * move.power) / 8 + 2)
            damage = int(random.uniform(damage * 0.85, damage * 1.15))
            damage = max(1, damage)
            
            self.defender.take_damage(damage)
            log_entry += f" Causou {damage} de dano."

            if move.heal_percentage > 0:
                heal_amount = int(damage * move.heal_percentage)
                self.attacker.heal(heal_amount)
                log_entry += f" {self.attacker.name} recuperou {heal_amount} de HP."
        
        self.log.append(log_entry)
        self.turn += 1

    def is_over(self):
        return self.pokemon1.is_fainted() or self.pokemon2.is_fainted()

    @property
    def winner(self):
        if not self.is_over():
            return None
        return self.pokemon1 if self.pokemon2.is_fainted() else self.pokemon2

    def to_dict(self):
        return {
            'pokemon1': self.pokemon1.to_dict(),
            'pokemon2': self.pokemon2.to_dict(),
            'turn': self.turn,
            'log': self.log,
        }

    @classmethod
    def from_dict(cls, data):
        pokemon1 = Pokemon.from_dict(data['pokemon1'])
        pokemon2 = Pokemon.from_dict(data['pokemon2'])
        battle = cls(pokemon1, pokemon2)
        battle.turn = data['turn']
        battle.log = data['log']
        return battle