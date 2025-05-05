import requests
import random

def get_pokemon(name, level):
    url = f'https://pokeapi.co/api/v2/pokemon/{name.lower()}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # status a partir do nivel escolhido
        stats = {stat['stat']['name']: int((stat['base_stat'] * 2 * level) / 100 + level + 10)
                 for stat in data['stats']}

        # verifica os ataques presentes ate certo nivel
        level_up_moves = []
        for move_entry in data['moves']:
            for detail in move_entry['version_group_details']:
                if detail['move_learn_method']['name'] == 'level-up' and detail['level_learned_at'] <= level:
                    level_up_moves.append(move_entry['move']['name'])

        # caso no nivel nao tenha 4 golpes, repetir um deles
        if len(level_up_moves) < 4:
            level_up_moves = [move['move']['name'] for move in data['moves']]

        # 4 golpes aleatorios
        random_moves = random.sample(level_up_moves, min(4, len(level_up_moves)))

        return {
            'name': data['name'].capitalize(),
            'hp': stats['hp'],
            'attack': stats['attack'],
            'defense': stats['defense'],
            'moves': random_moves
        }
    else:
        print(f"Pokémon '{name}' não encontrado!")
        return None

def get_move_power(move_name):
    url = f'https://pokeapi.co/api/v2/move/{move_name}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data['power']:
            return data['power']  # ataque da api
        else:
            return 40  
    else:
        return 40  # valor padrao para caso a api de erro

def calculate_damage(attacker, defender, move_name):
    power = get_move_power(move_name)  # força do golpe

    # dano baseado nos status
    base_damage = ((attacker['attack'] / defender['defense']) * power) / 5

    # variaçao aleatoria no dano
    return max(1, int(random.uniform(base_damage * 0.85, base_damage * 1.15)))

def battle(pokemon1, pokemon2):
    print(f"\nBATALHA: {pokemon1['name']} VS {pokemon2['name']}!")

    hp1 = pokemon1['hp']
    hp2 = pokemon2['hp']
    turn = 0  

    while hp1 > 0 and hp2 > 0:
        # troca de player de acordo com turno
        attacker = pokemon1 if turn % 2 == 0 else pokemon2
        defender = pokemon2 if turn % 2 == 0 else pokemon1

        # mostra os ataques
        print(f"\n{attacker['name']}, escolha seu ataque:")
        for i, move in enumerate(attacker['moves'], 1):
            print(f"{i}. {move}")

        while True:
            try:
                choice = int(input("Digite o número do ataque: "))
                if 1 <= choice <= len(attacker['moves']):
                    move = attacker['moves'][choice - 1]
                    break
                else:
                    print("Escolha inválida. Tente novamente.")
            except ValueError:
                print("Digite um número válido.")

        damage = calculate_damage(attacker, defender, move)
        if attacker == pokemon1:
            hp2 -= damage
            hp2 = max(0, hp2)  # nao ter hp negativo
        else:
            hp1 -= damage
            hp1 = max(0, hp1)

        print(f"{attacker['name']} usa {move}! Causa {damage} de dano!")

        # vida atual e dano tomadp
        print(f"[STATUS] {pokemon1['name']}: {hp1} HP | {pokemon2['name']}: {hp2} HP")

        turn += 1

    # determina quem ganhou
    winner = pokemon1['name'] if hp1 > 0 else pokemon2['name']
    print(f"\n{winner} venceu a batalha!")


def main():
    # nomes e niveis
    poke1_name = input("Escolha o primeiro Pokémon: ")
    poke1_level = int(input(f"Escolha o nível de {poke1_name} (1-100): "))
    poke2_name = input("Escolha o segundo Pokémon: ")
    poke2_level = int(input(f"Escolha o nível de {poke2_name} (1-100): "))

    poke1 = get_pokemon(poke1_name, poke1_level)
    poke2 = get_pokemon(poke2_name, poke2_level)

    # começa a batalha se achar os 2
    if poke1 and poke2:
        battle(poke1, poke2)

if __name__ == "__main__":
    main()
