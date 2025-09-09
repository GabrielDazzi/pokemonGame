# move.py
import requests

class Move:
    def __init__(self, move_name):
        self.name = move_name
        self.power = 40  # Poder padrão
        self.damage_class = 'physical'
        self.heal_percentage = 0
        self.stat_changes = []
        self._fetch_move_data()

    def _fetch_move_data(self):
        try:
            url = f'https://pokeapi.co/api/v2/move/{self.name.lower()}'
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            self.power = data.get('power', 40) or 40
            self.damage_class = data['damage_class']['name']
            self.stat_changes = data.get('stat_changes', [])

            healing_moves = ['absorb', 'mega-drain', 'giga-drain', 'leech-life', 'draining-kiss']
            if self.name.lower() in healing_moves:
                self.heal_percentage = 0.5 
                
        except requests.RequestException:
            print(f"Não foi possível buscar os dados do golpe: {self.name}")
    
    def __repr__(self):
        return f"<Move {self.name.capitalize()}>"