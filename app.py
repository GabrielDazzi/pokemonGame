from flask import Flask, render_template, request, redirect, url_for, session
import requests
import random
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Gera uma chave secreta aleatória


def get_pokemon(name, level):
    url = f'https://pokeapi.co/api/v2/pokemon/{name.lower()}'
    response = requests.get(url)
    if response.status_code != 200:
        return None

    data = response.json()
    stats = {
        stat['stat']['name']: int((stat['base_stat'] * 2 * level) / 100 + level + 10)
        for stat in data['stats']
    }

    level_up_moves = []
    for move_entry in data['moves']:
        for detail in move_entry['version_group_details']:
            if detail['move_learn_method']['name'] == 'level-up' and detail['level_learned_at'] <= level:
                level_up_moves.append(move_entry['move']['name'])

    if len(level_up_moves) < 4:
        level_up_moves = [move['move']['name'] for move in data['moves']]

    random_moves = random.sample(level_up_moves, min(4, len(level_up_moves)))

    return {
        'name': data['name'].capitalize(),
        'hp': stats['hp'],
        'attack': stats['attack'],
        'defense': stats['defense'],
        'moves': random_moves
    }


def get_move_data(move_name):
    url = f'https://pokeapi.co/api/v2/move/{move_name.lower()}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def calculate_damage(attacker, defender, move_name):
    move = get_move_data(move_name)
    if not move:
        return 0, 0

    power = move.get('power', 40)
    damage = ((attacker['attack'] / defender['defense']) * power) / 5
    damage = int(random.uniform(damage * 0.85, damage * 1.15))
    damage = max(1, damage)

    move_type = move['damage_class']['name']

    healing_moves = ['absorb', 'mega-drain', 'giga-drain', 'leech-life', 'draining-kiss', 'parabolic-charge']
    if move_name.lower() in healing_moves:
        heal = int(damage * 0.5)
        return damage, heal

    if move_name.lower() == 'transform':
        attacker.update({
            'attack': defender['attack'],
            'defense': defender['defense'],
            'hp': defender['hp'],
            'moves': defender['moves']
        })
        return 0, 'Transformou!'

    if move_type == 'status' and 'stat_changes' in move and move['stat_changes']:
        for stat_change in move['stat_changes']:
            stat = stat_change['stat']['name']
            change = stat_change['change']
            if stat in attacker:
                attacker[stat] = max(1, attacker[stat] + int(attacker[stat] * (0.1 * change)))
        return 0, 'Aumentou os status!'

    return damage, 0


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        poke1_name = request.form['poke1_name']
        poke1_level = int(request.form['poke1_level'])
        poke2_name = request.form['poke2_name']
        poke2_level = int(request.form['poke2_level'])

        poke1 = get_pokemon(poke1_name, poke1_level)
        poke2 = get_pokemon(poke2_name, poke2_level)

        if poke1 and poke2:
            session['poke1'] = poke1
            session['poke2'] = poke2
            session['hp1'] = poke1['hp']
            session['hp2'] = poke2['hp']
            session['max_hp1'] = poke1['hp']
            session['max_hp2'] = poke2['hp']
            session['turn'] = 0
            return redirect(url_for('battle'))
        else:
            return f"Erro ao buscar Pokémon {poke1_name} ou {poke2_name}. Verifique os nomes."

    return render_template('index.html')


@app.route('/battle', methods=['GET', 'POST'])
def battle():
    poke1 = session.get('poke1')
    poke2 = session.get('poke2')
    hp1 = session.get('hp1')
    hp2 = session.get('hp2')
    max_hp1 = session.get('max_hp1')
    max_hp2 = session.get('max_hp2')
    turn = session.get('turn')

    attacker = poke1 if turn % 2 == 0 else poke2
    defender = poke2 if turn % 2 == 0 else poke1

    if request.method == 'POST':
        move = request.form['move']
        damage, extra = calculate_damage(attacker, defender, move)

        last_move = {
            'attacker': attacker['name'],
            'move': move,
            'damage': damage,
            'hp1': hp1,
            'hp2': hp2
        }

        if isinstance(extra, str):  # Transform ou Buff
            last_move['effect'] = extra
            if extra == 'Transformou!':
                if turn % 2 == 0:
                    session['max_hp1'] = attacker['hp']
                    session['poke1'] = attacker
                else:
                    session['max_hp2'] = attacker['hp']
                    session['poke2'] = attacker
            elif extra == 'Aumentou os status!':
                if turn % 2 == 0:
                    session['poke1'] = attacker
                else:
                    session['poke2'] = attacker
        else:
            heal = extra
            if turn % 2 == 0:
                hp2 = max(0, hp2 - damage)
                hp1 = min(max_hp1, hp1 + heal)
                session['hp2'] = hp2
                session['hp1'] = hp1
            else:
                hp1 = max(0, hp1 - damage)
                hp2 = min(max_hp2, hp2 + heal)
                session['hp1'] = hp1
                session['hp2'] = hp2
            last_move['heal'] = heal
            last_move['hp1'] = hp1
            last_move['hp2'] = hp2

        session['last_move'] = last_move
        session['turn'] = turn + 1

        if hp1 <= 0 or hp2 <= 0:
            return redirect(url_for('result'))

        return redirect(url_for('battle'))

    # ⚠️ Cálculo das porcentagens de HP
    hp1_percent = int((hp1 / max_hp1) * 100) if max_hp1 > 0 else 0
    hp2_percent = int((hp2 / max_hp2) * 100) if max_hp2 > 0 else 0

    return render_template('battle.html',
                           attacker=attacker,
                           moves=attacker['moves'],
                           hp1=hp1,
                           hp2=hp2,
                           hp1_percent=hp1_percent,
                           hp2_percent=hp2_percent,
                           turn=turn,
                           poke1=poke1,
                           poke2=poke2,
                           last=session.get('last_move'))


@app.route('/result')
def result():
    winner = session['poke1']['name'] if session['hp1'] > 0 else session['poke2']['name']
    session.clear()
    return render_template('result.html', winner=winner)


if __name__ == '__main__':
    app.run(debug=True)
