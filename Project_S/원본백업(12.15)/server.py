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
    now = time.time()
    return user_ban.get(username, 0) > now

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
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/api/status')
def get_status():
    username = session.get('username', '')
    with status_lock:
        connected_mcus = [mcu_id for mcu_id in MCU_IDS if mcu_id in status_data]

        filtered_reservation_data = {}
        filtered_reservation_timers = {}
        filtered_red_alert = {}
        reservation_owners = {}
        for mcu_id in connected_mcus:
            filtered_reservation_data[mcu_id] = reservation_data.get(mcu_id, False)
            filtered_reservation_timers[mcu_id] = reservation_timers.get(mcu_id, 0)
            filtered_red_alert[mcu_id] = RED_ALERT.get(mcu_id, 0)
            reservation_owners[mcu_id] = reservation_owner.get(mcu_id, '')

        current_status = {k: status_data.get(k, 0) for k in connected_mcus}
        current_ban_data = {} 

    banned = is_user_banned(username)

    return jsonify({
        'status': current_status,
        'reservations': filtered_reservation_data,
        'reservation_owners': reservation_owners,
        'timers': filtered_reservation_timers,
        'red_alerts': filtered_red_alert,
        'ban_user': banned,
        'ban_data': current_ban_data
    })

@app.route('/reserve/<mcu_id>', methods=['POST'])
def reserve(mcu_id):
    username = session.get('username', '')
    if is_user_banned(username):
        return jsonify({'success': False, 'message': 'You are banned from reserving spots.'})
    with status_lock:
        if reservation_data.get(mcu_id):
            return jsonify({'success': False, 'message': 'Already reserved.'})
        if username in reservation_owner.values():
            return jsonify({'success': False, 'message': 'You already have a reservation.'})
        reservation_data[mcu_id] = True
        reservation_owner[mcu_id] = username
        reservation_timers[mcu_id] = 1800
    return jsonify({'success': True})


@app.route('/complete/<mcu_id>', methods=['POST'])
def complete_parking(mcu_id):
    username = session.get('username', '')
    with status_lock:
        if reservation_owner.get(mcu_id) != username:
            return jsonify({'success': False, 'message': 'Not your reservation.'})
        if RED_ALERT.get(mcu_id) == 2:
            RED_ALERT[mcu_id] = 1
            reservation_data[mcu_id] = False
            reservation_timers[mcu_id] = 0
            reservation_owner[mcu_id] = None
            status_data[mcu_id] = 0
    return jsonify({'success': True})

@app.route('/update', methods=['POST'])
def update_status():
    data = request.get_json()
    mcu_id = data.get('id')
    signal = data.get('signal')
    if not mcu_id or mcu_id not in MCU_IDS:
        return 'Invalid MCU ID', 400

    with status_lock:
        prev_signal = previous_signals.get(mcu_id, None)
        count = signal_counters.get(mcu_id, 0)

        if prev_signal == signal:
            count += 1
        else:
            count = 1
            prev_signal = signal

        previous_signals[mcu_id] = prev_signal
        signal_counters[mcu_id] = count

        if count >= 3:
            status_data[mcu_id] = signal

            if signal == 3:
                RED_ALERT[mcu_id] = 0
            else:
                if reservation_data.get(mcu_id):
                    if signal == 1:
                        RED_ALERT[mcu_id] = 2
                    else:
                        RED_ALERT[mcu_id] = 0
                else:
                    if signal == 1:
                        RED_ALERT[mcu_id] = 1
                    elif signal == 0:
                        RED_ALERT[mcu_id] = 0

    return 'OK'
    
@app.route('/api/led_status/<mcu_id>')
def get_led_status(mcu_id):
    with status_lock:
        if mcu_id not in status_data:
            return jsonify({'color': 'green'})
        signal = status_data[mcu_id]
        reserved = reservation_data.get(mcu_id, False)
        red_alert = RED_ALERT.get(mcu_id, 0)

        if signal == 3:
            return jsonify({'color': 'blue'})
        elif red_alert == 1:
            return jsonify({'color': 'red'})
        elif reserved:
            return jsonify({'color': 'yellow'})
        elif signal == 1:
            return jsonify({'color': 'red'})
        else:
            return jsonify({'color': 'green'})


def update_timers():
    with status_lock:
        for mcu_id in list(reservation_timers.keys()):
            if reservation_timers[mcu_id] > 0:
                reservation_timers[mcu_id] -= 1
            else:
                if reservation_data.get(mcu_id):
                    owner = reservation_owner.get(mcu_id)
                    if owner:
                        ban_user(owner, 600)
                    reservation_data[mcu_id] = False
                    reservation_owner[mcu_id] = None
                reservation_timers[mcu_id] = 0

def timer_thread():
    while True:
        update_timers()
        time.sleep(1)

threading.Thread(target=timer_thread, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1557)
