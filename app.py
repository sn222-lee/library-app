from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret'

# DB 초기화
def init_db():
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()

    # 사용자 테이블
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            password TEXT,
            approved INTEGER
        )
    ''')

    # 예약 테이블
    cur.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            pc_number TEXT,
            res_date TEXT,
            res_time TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# 첫 화면
@app.route('/')
def home():
    return render_template('login.html')

# 회원가입
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['id']
        pw = request.form['pw']

        if not user_id.isdigit():
            return '학번/사번은 숫자만 입력하세요.'

        conn = sqlite3.connect('library.db')
        cur = conn.cursor()

        try:
            cur.execute(
                'INSERT INTO users (id, password, approved) VALUES (?, ?, ?)',
                (user_id, pw, 0)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return '이미 존재하는 ID입니다.'

        conn.close()
        return '가입 완료! 관리자 승인 후 로그인 가능합니다.'

    return render_template('register.html')

# 로그인
@app.route('/login', methods=['POST'])
def login():
    user_id = request.form['id']
    pw = request.form['pw']

    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    cur.execute(
        'SELECT * FROM users WHERE id=? AND password=?',
        (user_id, pw)
    )
    user = cur.fetchone()
    conn.close()

    if user:
        if user[2] == 0:
            return '관리자 승인 대기중입니다.'
        session['user'] = user_id
        return redirect('/reserve')

    return '로그인 실패'

# 예약 페이지
@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        pc_number = request.form.get('pc_number')
        res_date = request.form.get('res_date')
        res_time = request.form.get('res_time')

        if not pc_number or not res_date or not res_time:
            return 'PC 번호, 날짜, 시간을 모두 입력하세요.'

        conn = sqlite3.connect('library.db')
        cur = conn.cursor()

        # 중복 예약 확인
        cur.execute('''
            SELECT * FROM reservations
            WHERE pc_number=? AND res_date=? AND res_time=?
        ''', (pc_number, res_date, res_time))

        exists = cur.fetchone()
        if exists:
            conn.close()
            return '이미 예약된 자리입니다.'

        cur.execute('''
            INSERT INTO reservations (user_id, pc_number, res_date, res_time)
            VALUES (?, ?, ?, ?)
        ''', (session['user'], pc_number, res_date, res_time))
        conn.commit()
        conn.close()

        return redirect('/my_reservations')

    return render_template('reserve.html', user=session['user'])

# 내 예약 보기
@app.route('/my_reservations')
def my_reservations():
    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    cur.execute('''
        SELECT pc_number, res_date, res_time
        FROM reservations
        WHERE user_id=?
        ORDER BY res_date, res_time
    ''', (session['user'],))
    rows = cur.fetchall()
    conn.close()

    return render_template('my_reservations.html', rows=rows, user=session['user'])

# 관리자 승인
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()

    if request.method == 'POST':
        user_id = request.form['id']
        cur.execute('UPDATE users SET approved=1 WHERE id=?', (user_id,))
        conn.commit()

    cur.execute('SELECT * FROM users WHERE approved=0')
    users = cur.fetchall()
    conn.close()

    return render_template('admin.html', users=users)

# 비밀번호 변경
@app.route('/change_pw', methods=['GET', 'POST'])
def change_pw():
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        new_pw = request.form['pw']

        conn = sqlite3.connect('library.db')
        cur = conn.cursor()
        cur.execute(
            'UPDATE users SET password=? WHERE id=?',
            (new_pw, session['user'])
        )
        conn.commit()
        conn.close()

        return '비밀번호가 변경되었습니다.'

    return render_template('change_pw.html')

# 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run()