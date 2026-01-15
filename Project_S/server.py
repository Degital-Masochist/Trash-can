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
ILLEGAL_PARKING = {}

MCU_COUNT = 30
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
        connected = [m for m in MCU_IDS if m in status_data]
        return jsonify({
            'status': {m: status_data[m] for m in connected},
            'reservations': {m: reservation_data.get(m, False) for m in connected},
            'reservation_owners': {m: reservation_owner.get(m, '') for m in connected},
            'timers': {m: reservation_timers.get(m, 0) for m in connected},
            'illegal': {m: ILLEGAL_PARKING.get(m, False) for m in connected},
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
        ILLEGAL_PARKING[mcu_id] = False
    return jsonify({'success': True})

@app.route('/report/<mcu_id>', methods=['POST'])
def report(mcu_id):
    with status_lock:
        if reservation_data.get(mcu_id) and status_data.get(mcu_id) == 1:
            ILLEGAL_PARKING[mcu_id] = True
    return jsonify({'success': True})

@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()
    mcu_id = data.get('id')
    signal = data.get('signal')
    
    if mcu_id not in MCU_IDS:
        return 'Invalid', 400
    
    with status_lock:
        prev = previous_signals.get(mcu_id)
        count = signal_counters.get(mcu_id, 0)
        
        if prev == signal:
            count += 1
        else:
            prev = signal
            count = 1
            
        previous_signals[mcu_id] = prev
        signal_counters[mcu_id] = count
        
        if signal == 3:
            if count >= 3:
                status_data[mcu_id] = signal
        else:
            if count >= 3:
                status_data[mcu_id] = signal
        
        if ILLEGAL_PARKING.get(mcu_id) and signal == 0 and count >= 3:
            ILLEGAL_PARKING[mcu_id] = False
                
    return 'OK'

@app.route('/api/led_status/<mcu_id>')
def led_status(mcu_id):
    with status_lock:
        s = status_data.get(mcu_id, 0)
        is_reserved = reservation_data.get(mcu_id, False)
        is_illegal = ILLEGAL_PARKING.get(mcu_id, False)
        
        if s == 3:
            return jsonify({'color': 'blue_blink'})
            
        if is_illegal:
            return jsonify({'color': 'red_blink'})
            
        if s == 1:
            return jsonify({'color': 'red'})
            
        if is_reserved:
            return jsonify({'color': 'blue'})
            
        return jsonify({'color': 'green'})

def timer_thread():
    while True:
        with status_lock:
            for m in list(reservation_timers):
                if reservation_timers[m] > 0:
                    reservation_timers[m] -= 1
                else:
                    if reservation_data.get(m):
                        ban_user(reservation_owner.get(m), 600)
                        reservation_data[m] = False
                        reservation_owner[m] = None
        time.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=timer_thread, daemon=True).start()
    app.run(host='0.0.0.0', port=1557)