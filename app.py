from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret'

# DB 초기화
def init_db():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            password TEXT,
            approved INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 홈
@app.route('/')
def home():
    return render_template('login.html')

# 회원가입
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['id']
        pw = request.form['pw']

        # 학번/사번 검증 (숫자만)
        if not user_id.isdigit():
            return '학번/사번은 숫자만 입력하세요'

        conn = sqlite3.connect('users.db')
        cur = conn.cursor()

        try:
            cur.execute('INSERT INTO users VALUES (?, ?, ?)', (user_id, pw, 0))
            conn.commit()
        except:
            conn.close()
            return '이미 존재하는 ID입니다'

        conn.close()
        return '가입 완료! 관리자 승인 후 사용 가능합니다.'

    return render_template('register.html')

# 로그인
@app.route('/login', methods=['POST'])
def login():
    user_id = request.form['id']
    pw = request.form['pw']

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE id=? AND password=?', (user_id, pw))
    user = cur.fetchone()
    conn.close()

    if user:
        if user[2] == 0:
            return '관리자 승인 대기중입니다.'
        session['user'] = user_id
        return redirect('/change_pw')

    return '로그인 실패'

# 관리자 승인
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = sqlite3.connect('users.db')
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
        user_id = session.get('user')
        new_pw = request.form['pw']

        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute('UPDATE users SET password=? WHERE id=?', (new_pw, user_id))
        conn.commit()
        conn.close()

        return '비밀번호 변경 완료'

    return render_template('change_pw.html')

if __name__ == '__main__':
    app.run()