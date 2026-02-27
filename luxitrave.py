from flask import Flask, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "luxitrave_secret"
DB = "database.db"

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        driver_id INTEGER,
        jemput TEXT,
        tujuan TEXT,
        jarak REAL,
        harga REAL,
        status TEXT
    )''')

    conn.commit()
    conn.close()

init_db()

# ================= STYLE =================
def style():
    return """
    <style>
    body{margin:0;font-family:Arial;background:#000;color:white;padding:20px;}
    h2{color:gold;}
    .card{background:#1a1a1a;padding:20px;border-radius:15px;margin-bottom:20px;}
    input,select{width:100%;padding:8px;margin:8px 0;border:none;border-radius:8px;}
    button{padding:8px 12px;background:gold;border:none;border-radius:8px;font-weight:bold;}
    table{width:100%;}
    th,td{padding:8px;text-align:center;}
    th{color:gold;}
    a{color:gold;text-decoration:none;}
    .center{display:flex;justify-content:center;align-items:center;height:100vh;}
    .login-box{width:320px;background:#1a1a1a;padding:30px;border-radius:15px;box-shadow:0 0 20px gold;}
    </style>
    """

# ================= REGISTER =================
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO users (nama,username,password,role) VALUES (?,?,?,?)",
                  (request.form["nama"],
                   request.form["username"],
                   request.form["password"],
                   request.form["role"]))
        conn.commit()
        conn.close()
        return redirect("/")

    return f"""
    {style()}
    <div class="center">
    <div class="login-box">
    <h2>Daftar LuxiTrave</h2>
    <form method="POST">
    <input name="nama" placeholder="Nama" required>
    <input name="username" placeholder="Username" required>
    <input type="password" name="password" placeholder="Password" required>
    <select name="role">
    <option value="user">User</option>
    <option value="driver">Driver</option>
    </select>
    <button>DAFTAR</button>
    </form>
    <a href="/">Kembali Login</a>
    </div></div>
    """

# ================= LOGIN =================
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (request.form["username"], request.form["password"]))
        user = c.fetchone()
        conn.close()

        if user:
            session["id"] = user[0]
            session["role"] = user[4]
            return redirect("/dashboard")

    return f"""
    {style()}
    <div class="center">
    <div class="login-box">
    <h2>LuxiTrave Login</h2>
    <form method="POST">
    <input name="username" placeholder="Username" required>
    <input type="password" name="password" placeholder="Password" required>
    <button>LOGIN</button>
    </form>
    <p>Belum punya akun? <a href="/register">Daftar</a></p>
    </div></div>
    """

# ================= DASHBOARD =================
@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if "role" not in session:
        return redirect("/")

    role = session["role"]

    if role == "user":
        if request.method == "POST":
            jarak = float(request.form["jarak"])
            harga = 10000 + (jarak * 5000)

            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("""INSERT INTO orders 
                         (user_id, driver_id, jemput, tujuan, jarak, harga, status)
                         VALUES (?,?,?,?,?,?,?)""",
                      (session["id"], None,
                       request.form["jemput"],
                       request.form["tujuan"],
                       jarak, harga, "menunggu"))
            conn.commit()
            conn.close()

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT * FROM orders WHERE user_id=?", (session["id"],))
        orders = c.fetchall()
        conn.close()

        rows = ""
        for o in orders:
            rows += f"<tr><td>{o[0]}</td><td>{o[3]}</td><td>{o[4]}</td><td>Rp {o[6]}</td><td>{o[7]}</td></tr>"

        return f"""
        {style()}
        <h2>Dashboard User</h2>
        <a href="/logout">Logout</a>
        <div class="card">
        <h3>Booking Travel</h3>
        <form method="POST">
        <input name="jemput" placeholder="Lokasi Jemput" required>
        <input name="tujuan" placeholder="Lokasi Tujuan" required>
        <input type="number" step="0.1" name="jarak" placeholder="Jarak KM" required>
        <button>Pesan</button>
        </form>
        </div>
        <div class="card">
        <h3>Riwayat Order</h3>
        <table>
        <tr><th>ID</th><th>Jemput</th><th>Tujuan</th><th>Harga</th><th>Status</th></tr>
        {rows}
        </table>
        </div>
        """

    if role == "driver":
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT * FROM orders WHERE status='menunggu'")
        orders = c.fetchall()
        conn.close()

        rows = ""
        for o in orders:
            rows += f"<tr><td>{o[0]}</td><td>{o[3]}</td><td>{o[4]}</td><td>Rp {o[6]}</td><td><a href='/ambil/{o[0]}'><button>Ambil</button></a></td></tr>"

        return f"""
        {style()}
        <h2>Dashboard Driver</h2>
        <a href="/logout">Logout</a>
        <div class="card">
        <table>
        <tr><th>ID</th><th>Jemput</th><th>Tujuan</th><th>Harga</th><th>Aksi</th></tr>
        {rows}
        </table>
        </div>
        """

    if role == "admin":
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        users = c.fetchall()
        conn.close()

        rows = ""
        for u in users:
            rows += f"<tr><td>{u[0]}</td><td>{u[1]}</td><td>{u[2]}</td><td>{u[4]}</td></tr>"

        return f"""
        {style()}
        <h2>Dashboard Admin</h2>
        <a href="/logout">Logout</a>
        <div class="card">
        <table>
        <tr><th>ID</th><th>Nama</th><th>Username</th><th>Role</th></tr>
        {rows}
        </table>
        </div>
        """

# ================= AMBIL ORDER =================
@app.route("/ambil/<int:id>")
def ambil(id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE orders SET driver_id=?, status=? WHERE id=?",
              (session["id"], "diambil", id))
    conn.commit()
    conn.close()
    return redirect("/dashboard")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)