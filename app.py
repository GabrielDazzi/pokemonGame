# app.py
from flask import Flask, render_template, request, redirect, url_for, session
import os
from pokemon import Pokemon
from battle import Battle

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            poke1_name = request.form['poke1_name']
            poke1_level = int(request.form['poke1_level'])
            poke2_name = request.form['poke2_name']
            poke2_level = int(request.form['poke2_level'])

            poke1 = Pokemon(poke1_name, poke1_level)
            poke2 = Pokemon(poke2_name, poke2_level)

            battle = Battle(poke1, poke2)
            session['battle'] = battle.to_dict()

            return redirect(url_for('battle_screen'))
        except (ValueError, KeyError) as e:
            error_message = f"Erro ao criar a batalha. Verifique os nomes e níveis. ({e})"
            return render_template('index.html', error=error_message)
            
    return render_template('index.html')

@app.route('/battle', methods=['GET', 'POST'])
def battle_screen():
    battle_data = session.get('battle')
    if not battle_data:
        return redirect(url_for('index'))

    battle = Battle.from_dict(battle_data)

    if request.method == 'POST':
        move_name = request.form['move']
        battle.execute_turn(move_name)
        session['battle'] = battle.to_dict()

        if battle.is_over():
            return redirect(url_for('result'))
        
        return redirect(url_for('battle_screen'))

    return render_template('battle.html', battle=battle)

@app.route('/result')
def result():
    battle_data = session.get('battle')
    if not battle_data or not Battle.from_dict(battle_data).is_over():
        return redirect(url_for('index'))

    winner_name = Battle.from_dict(battle_data).winner.name
    session.clear()
    return render_template('result.html', winner=winner_name)

@app.route('/new_game')
def new_game():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)