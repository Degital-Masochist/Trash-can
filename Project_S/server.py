from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from threading import Lock
import threading
import time
from account import USERS, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

status_data = {}
status_lock = Lock()
reservation_data = {}
reservation_owner = {}
previous_signals = {}
signal_counters = {}
reservation_timers = {}
RED_ALERT = {}
MCU_COUNT = 30 #Number of MCU
MCU_IDS = [str(i) for i in range(1, MCU_COUNT + 1)]

users = USERS
user_ban = {}

def is_user_banned(username):
    return user_ban.get(username, 0) > time.time()

def ban_user(username, duration=600):
    user_ban[username] = time.time() + duration

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('status.html', username=session.get('username', ''))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        if u in users and users[u] == p:
            session['logged_in'] = True
            session['username'] = u
            return redirect(url_for('index'))
        error = 'Invalid username or password'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/status')
def get_status():
    username = session.get('username', '')
    with status_lock:
        connected = [i for i in MCU_IDS if i in status_data]
        return jsonify({
            'status': {i: status_data[i] for i in connected},
            'reservations': {i: reservation_data.get(i, False) for i in connected},
            'reservation_owners': {i: reservation_owner.get(i, '') for i in connected},
            'timers': {i: reservation_timers.get(i, 0) for i in connected},
            'red_alerts': {i: RED_ALERT.get(i, 0) for i in connected},
            'ban_user': is_user_banned(username)
        })
        
@app.route('/reserve/<mcu_id>', methods=['POST'])
def reserve(mcu_id):
    username = session.get('username', '')
    if is_user_banned(username):
        return jsonify({'success': False})
    with status_lock:
        if reservation_data.get(mcu_id):
            return jsonify({'success': False})
        if username in reservation_owner.values():
            return jsonify({'success': False})
        reservation_data[mcu_id] = True
        reservation_owner[mcu_id] = username
        reservation_timers[mcu_id] = 1800
    return jsonify({'success': True})

@app.route('/complete/<mcu_id>', methods=['POST'])
def complete(mcu_id):
    username = session.get('username', '')
    with status_lock:
        if reservation_owner.get(mcu_id) != username:
            return jsonify({'success': False})
        reservation_data[mcu_id] = False
        reservation_owner[mcu_id] = None
        reservation_timers[mcu_id] = 0
        RED_ALERT[mcu_id] = 0
    return jsonify({'success': True})

@app.route('/report/<mcu_id>', methods=['POST'])
def report(mcu_id):
    username = session.get('username', '')
    with status_lock:
        if reservation_owner.get(mcu_id) != username:
            return jsonify({'success': False})
        status_data[mcu_id] = 4
        RED_ALERT[mcu_id] = 0
    return jsonify({'success': True})

@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()
    mcu_id = data.get('id')
    signal = data.get('signal')

    if mcu_id not in MCU_IDS:
        return 'BAD', 400

    with status_lock:
        if status_data.get(mcu_id) == 4:
            if signal == 0:
                status_data[mcu_id] = 0
            return 'OK'

        prev = previous_signals.get(mcu_id)
        cnt = signal_counters.get(mcu_id, 0)

        if prev == signal:
            cnt += 1
        else:
            cnt = 1

        previous_signals[mcu_id] = signal
        signal_counters[mcu_id] = cnt

        if cnt >= 3:
            status_data[mcu_id] = signal
            if signal == 1:
                RED_ALERT[mcu_id] = 1
            else:
                RED_ALERT[mcu_id] = 0

    return 'OK'

@app.route('/api/led_status/<mcu_id>')
def led_status(mcu_id):
    with status_lock:
        signal = status_data.get(mcu_id, 0)
        reserved = reservation_data.get(mcu_id, False)
        red_alert = RED_ALERT.get(mcu_id, 0)

        if signal == 4:
            return jsonify({'color': 'blue'})
        if signal == 3:
            return jsonify({'color': 'off'})
        if red_alert == 1:
            return jsonify({'color': 'red'})
        if reserved:
            return jsonify({'color': 'yellow'})
        if signal == 1:
            return jsonify({'color': 'red'})
        return jsonify({'color': 'green'})

def timer_thread():
    while True:
        with status_lock:
            for mcu in list(reservation_timers.keys()):
                if reservation_timers[mcu] > 0:
                    reservation_timers[mcu] -= 1
                else:
                    if reservation_data.get(mcu):
                        ban_user(reservation_owner.get(mcu), 600)
                        reservation_data[mcu] = False
                        reservation_owner[mcu] = None
        time.sleep(1)

threading.Thread(target=timer_thread, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1557)
