# 도서관 공용PC 예약 관리 프로그램 (웹 기반 + GUI + 관리자 기능)
# 초보자도 실행 가능하도록 최대한 간단하게 구성
# 실행 방법:
# 1) Python 설치
# 2) 터미널에서: pip install flask
# 3) 이 파일 실행: python app.py
# 4) 인터넷 브라우저에서: http://127.0.0.1:5000 접속

from flask import Flask, render_template_string, request, redirect, session
import csv, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret'

USERS = 'users.csv'
RES = 'reservations.csv'
LOG = 'log.csv'

# ---------------- 초기 파일 생성 ----------------
def init():
    if not os.path.exists(USERS):
        with open(USERS,'w',newline='') as f:
            csv.writer(f).writerows([['id','pw','role'],['admin','1234','admin']])
    if not os.path.exists(RES):
        with open(RES,'w',newline='') as f:
            csv.writer(f).writerow(['user','pc','date','time'])
    if not os.path.exists(LOG):
        with open(LOG,'w',newline='') as f:
            csv.writer(f).writerow(['user','start','end','program'])

# ---------------- 로그인 ----------------
@app.route('/', methods=['GET','POST'])
def login():
    if request.method=='POST':
        uid=request.form['id']
        pw=request.form['pw']
        with open(USERS) as f:
            for r in csv.DictReader(f):
                if r['id']==uid and r['pw']==pw:
                    session['user']=uid
                    session['role']=r['role']
                    return redirect('/main')
    return render_template_string('''
    <h2>로그인</h2>
    <form method=post>
    ID:<input name=id><br>
    PW:<input name=pw type=password><br>
    <button>로그인</button>
    </form>
    ''')

# ---------------- 메인 ----------------
@app.route('/main')
def main():
    if 'user' not in session: return redirect('/')
    return render_template_string('''
    <h2>메인</h2>
    <a href='/reserve'>PC 예약</a><br>
    <a href='/view'>예약 조회</a><br>
    <a href='/log'>사용 기록</a><br>
    {% if session['role']=='admin' %}
    <a href='/admin'>관리자</a><br>
    {% endif %}
    ''')

# ---------------- PC 선택 UI ----------------
@app.route('/reserve', methods=['GET','POST'])
def reserve():
    if request.method=='POST':
        pc=request.form['pc']
        date=request.form['date']
        time=request.form['time']

        # 중복 방지
        with open(RES) as f:
            for r in csv.DictReader(f):
                if r['pc']==pc and r['date']==date and r['time']==time:
                    return '이미 예약됨'

        with open(RES,'a',newline='') as f:
            csv.writer(f).writerow([session['user'],pc,date,time])
        return redirect('/view')

    buttons = ''.join([f"<button name='pc' value='{i}'>PC {i}</button>" for i in range(1,11)])

    return render_template_string(f'''
    <h2>PC 선택</h2>
    <form method=post>
    {buttons}<br><br>
    날짜:<input name=date type=date required><br>
    시간:<input name=time placeholder='10:00~11:00' required><br>
    <button>예약</button>
    </form>
    ''')

# ---------------- 예약 조회 ----------------
@app.route('/view')
def view():
    rows = ''
    with open(RES) as f:
        for r in csv.reader(f):
            rows += '<tr>' + ''.join([f'<td>{c}</td>' for c in r]) + '</tr>'

    return render_template_string(f'''
    <h2>예약 목록</h2>
    <table border=1>
    {rows}
    </table>
    ''')

# ---------------- 사용 기록 ----------------
@app.route('/log', methods=['GET','POST'])
def log():
    if request.method=='POST':
        program=request.form['program']
        start=datetime.now()
        end=datetime.now()
        with open(LOG,'a',newline='') as f:
            csv.writer(f).writerow([session['user'],start,end,program])

    return render_template_string('''
    <h2>사용 기록</h2>
    <form method=post>
    프로그램:<input name=program>
    <button>저장</button>
    </form>
    ''')

# ---------------- 관리자 ----------------
@app.route('/admin', methods=['GET','POST'])
def admin():
    if session.get('role')!='admin': return '권한 없음'

    if request.method=='POST':
        uid=request.form['id']
        pw=request.form['pw']
        with open(USERS,'a',newline='') as f:
            csv.writer(f).writerow([uid,pw,'user'])

    users=''
    with open(USERS) as f:
        for r in csv.reader(f):
            users += '<tr>' + ''.join([f'<td>{c}</td>' for c in r]) + '</tr>'

    return render_template_string(f'''
    <h2>관리자</h2>
    <form method=post>
    ID:<input name=id>
    PW:<input name=pw>
    <button>사용자 추가</button>
    </form>
    <table border=1>{users}</table>
    ''')

# ---------------- 실행 ----------------
if __name__=='__main__':
    app.run()
