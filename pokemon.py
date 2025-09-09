# pokemon.py
import requests
import random
from move import Move

class Pokemon:
    def __init__(self, name, level):
        self.name = name.capitalize()
        self.level = level
        self.stats = {}
        self.moves = []
        self.current_hp = 0
        self.max_hp = 0
        
        if not self._fetch_pokemon_data():
            raise ValueError(f"Não foi possível encontrar o Pokémon: {name}")

    def _fetch_pokemon_data(self):
        try:
            url = f'https://pokeapi.co/api/v2/pokemon/{self.name.lower()}'
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            base_stats = {stat['stat']['name']: stat['base_stat'] for stat in data['stats']}
            self.stats = {
                'hp': int((base_stats['hp'] * 2 * self.level) / 100 + self.level + 10),
                'attack': int((base_stats['attack'] * 2 * self.level) / 100 + 5),
                'defense': int((base_stats['defense'] * 2 * self.level) / 100 + 5),
            }
            self.max_hp = self.stats['hp']
            self.current_hp = self.max_hp

            possible_moves = [
                move['move']['name']
                for move in data['moves']
                for detail in move['version_group_details']
                if detail['move_learn_method']['name'] == 'level-up' and detail['level_learned_at'] <= self.level
            ]
            
            if len(possible_moves) < 4:
                possible_moves.extend([move['move']['name'] for move in data['moves']])
            
            unique_moves = list(set(possible_moves))
            chosen_moves = random.sample(unique_moves, min(4, len(unique_moves)))
            self.moves = [Move(move_name) for move_name in chosen_moves]
            
            return True
        except requests.RequestException:
            return False

    def take_damage(self, damage):
        self.current_hp = max(0, self.current_hp - damage)

    def heal(self, amount):
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    def is_fainted(self):
        return self.current_hp <= 0

    def get_hp_percent(self):
        if self.max_hp == 0:
            return 0
        return int((self.current_hp / self.max_hp) * 100)
    
    def to_dict(self):
        return {
            'name': self.name,
            'level': self.level,
            'stats': self.stats,
            'moves': [move.name for move in self.moves],
            'current_hp': self.current_hp,
            'max_hp': self.max_hp,
        }

    @classmethod
    def from_dict(cls, data):
        pokemon = cls.__new__(cls)
        pokemon.name = data['name']
        pokemon.level = data['level']
        pokemon.stats = data['stats']
        pokemon.moves = [Move(name) for name in data['moves']]
        pokemon.current_hp = data['current_hp']
        pokemon.max_hp = data['max_hp']
        return pokemon

    def __repr__(self):
        return f"<Pokemon {self.name} (Lvl {self.level})>"