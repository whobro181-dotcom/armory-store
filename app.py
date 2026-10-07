import os, sqlite3, socket
from functools import wraps
from flask import Flask, render_template, request, redirect, session, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

BASE = os.path.dirname(os.path.abspath(__file__))
for p in ["templates/shop","templates/admin","database","static/uploads"]:
    os.makedirs(os.path.join(BASE,p), exist_ok=True)

DB_PATH = os.path.join(BASE,"database/armory.db")
UPLOAD = os.path.join(BASE,"static/uploads")
SECRET = "pisah_simple_no_ngrok_v14"

def get_wifi_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.1.4"

WIFI_IP = get_wifi_ip()

if os.path.exists(DB_PATH):
    try: os.remove(DB_PATH)
    except: pass

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL, stock INTEGER, description TEXT, image_url TEXT, spec TEXT, featured INTEGER, rating REAL, sold INTEGER)")
    c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, email TEXT, password TEXT, phone TEXT, address TEXT, joined TEXT, role TEXT DEFAULT 'buyer')")
    c.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER, customer TEXT, email TEXT, phone TEXT, address TEXT, product TEXT, qty INTEGER, total REAL, status TEXT, date TEXT)")
    items = [
        ("GLOCK 19 GEN5", "Pistol", 549.0, 12, "9mm pistol", "https://images.unsplash.com/photo-1595590424283-b8f17842773f?w=500", "9mm", 1, 4.9, 124),
        ("AR-15 Sport", "Rifle", 1299.0, 5, "M-LOK rifle", "https://images.unsplash.com/photo-1584551246679-0daf3d275d0f?w=500", "5.56mm", 1, 4.8, 89),
        ("Tactical Vest IIIA", "Gear", 199.0, 20, "Kevlar vest", "https://images.unsplash.com/photo-1541889479100-7a45a8a73b4f?w=500", "L/XL", 1, 4.8, 210),
        ("Ammo 9MM 100RD", "Ammo", 49.0, 100, "100 rounds", "https://images.unsplash.com/photo-1595590424283-b8f17842773f?w=500", "9mm", 1, 4.9, 340),
    ]
    c.executemany("INSERT INTO products VALUES (NULL,?,?,?,?,?,?,?,?,?,?)", items)
    from datetime import datetime
    c.execute("INSERT INTO users VALUES (NULL,?,?,?,?,?,?,?)", ("admin","admin@armory.com",generate_password_hash("admin123"),"08123456789","Admin HQ","01-01-2024","admin"))
    c.execute("INSERT INTO users VALUES (NULL,?,?,?,?,?,?,?)", ("buyer1","buyer@test.com",generate_password_hash("123456"),"0811111111","Jakarta","01-01-2024","buyer"))
    conn.commit(); conn.close()

def create_templates():
    open(os.path.join(BASE,"templates/shop/landing.html"),"w",encoding="utf-8").write(f"""
<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>ARMORY - Login Pisah</title>
<style>
body{{margin:0;background:#0a0a0a;color:#fff;font-family:sans-serif;min-height:100vh}}
header{{background:#111;padding:14px 16px;border-bottom:2px solid #ffcc00;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:10}}
.container{{padding:20px;max-width:500px;margin:0 auto}}
.card{{background:#171717;border:1px solid #333;border-radius:20px;padding:24px;margin:16px 0;text-align:center;text-decoration:none;color:#fff;display:block;transition:.15s}}
.card:active{{transform:scale(.97)}} .icon{{font-size:48px;margin-bottom:12px}}
.btn{{width:100%;padding:14px;border-radius:28px;border:0;font-weight:800;font-size:16px;margin-top:14px;cursor:pointer;display:block;text-align:center;text-decoration:none;box-sizing:border-box}}
.y{{background:#ffcc00;color:#000}} .b{{background:#0088ff;color:#fff}} .d{{background:#222;color:#fff}} .g{{background:#00ff88;color:#000}}
.info{{background:#111;border:1px solid #333;border-radius:12px;padding:12px;margin:16px 0;font-size:12px;text-align:left}}
.warn{{background:#ffcc00;color:#000;padding:4px 8px;border-radius:10px;font-size:10px;font-weight:800}}
</style></head><body>
<header><div><b>ARMORY</b> <span style='background:#ffcc00;color:#000;padding:3px 8px;border-radius:10px;font-size:10px;font-weight:800'>PISAH LOGIN</span></div><div style='font-size:10px;background:#222;padding:4px 8px;border-radius:10px'>{WIFI_IP}:5000</div></header>

<div class='container'>
<div style='text-align:center;padding:10px 0'>
<h2 style='margin:8px 0'>Pilih Login - Dipisah</h2>
<p style='opacity:.6;font-size:13px'>Buyer & Admin beda halaman - Super simpel</p>
</div>

<div class='info' style='border-color:#ff4444'>
<b style='color:#ff4444'>⚠️ Ngrok Error? Solusi All WiFi tanpa ngrok:</b><br><br>
Ngrok gak bisa jalan di Pydroid3 (Exec format error).<br><br>
<b style='color:#00ff88'>✅ SOLUSI 1 - Render.com (Gratis, All WiFi Permanen):</b><br>
1. Buka github.com → Upload file app.py ini<br>
2. Buka render.com → New Web Service → Connect GitHub<br>
3. Dapat link https://armory-xxxx.onrender.com<br>
4. Link itu bisa dibuka semua WiFi / paket data selamanya!<br><br>
<b style='color:#ffcc00'>✅ SOLUSI 2 - Tetap Lokal (1 WiFi) - Sudah Jalan:</b><br>
• HP ini: http://127.0.0.1:5000/<br>
• Teman 1 WiFi: http://{WIFI_IP}:5000/<br>
Bisa login Buyer & Admin dipisah!
</div>

<a href='/login' class='card' style='border-color:#ffcc00'>
<div class='icon'>🛒</div>
<div style='font-size:22px;font-weight:800'>Buyer Login</div>
<div style='opacity:.6;font-size:13px;margin:6px 0'>Halaman khusus pembeli - Simple</div>
<div style='background:#222;padding:8px;border-radius:8px;font-size:11px;margin:8px 0;text-align:left'>
📍 URL Buyer:<br>
• Lokal: http://{WIFI_IP}:5000/login<br>
• HP ini: http://127.0.0.1:5000/login
</div>
<div class='btn y'>Masuk sebagai Buyer</div>
<div style='font-size:11px;opacity:.4;margin-top:8px'>Test: buyer1 / 123456</div>
</a>

<a href='/admin/login' class='card' style='border-color:#0088ff'>
<div class='icon'>🛡️</div>
<div style='font-size:22px;font-weight:800'>Admin Login</div>
<div style='opacity:.6;font-size:13px;margin:6px 0'>Halaman khusus admin - Pisah total</div>
<div style='background:#222;padding:8px;border-radius:8px;font-size:11px;margin:8px 0;text-align:left'>
📍 URL Admin:<br>
• Lokal: http://{WIFI_IP}:5000/admin/login<br>
• HP ini: http://127.0.0.1:5000/admin/login
</div>
<div class='btn b'>Masuk sebagai Admin</div>
<div style='font-size:11px;opacity:.4;margin-top:8px'>admin / admin123</div>
</a>

<a href='/shop' class='card'>
<div class='icon'>👁️</div>
<div style='font-size:18px;font-weight:700'>Lihat Toko (Guest)</div>
<div style='opacity:.6;font-size:12px'>Lihat dulu tanpa login</div>
<div class='btn d'>Guest Mode</div>
</a>

<div class='info'>
<b style='color:#ffcc00'>Kenapa login dipisah?</b><br>
• Buyer login di /login → langsung ke Shop<br>
• Admin login di /admin/login → langsung ke Dashboard<br>
• Gak nyampur, gak ada tab-tab, super simpel!<br>
• Session beda, aman!
</div>
</div>
</body></html>
""")
    open(os.path.join(BASE,"templates/shop/login.html"),"w",encoding="utf-8").write("""
<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Buyer Login - Pisah Simple</title>
<style>
body{margin:0;background:#0a0a0a;color:#fff;font-family:sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:16px}
.box{background:#171717;padding:28px;border-radius:20px;width:100%;max-width:360px;border:2px solid #ffcc00}
input{width:100%;padding:14px;background:#222;border:1px solid #333;color:#fff;border-radius:12px;margin:8px 0;box-sizing:border-box;font-size:15px}
.btn{width:100%;padding:14px;border-radius:28px;border:0;font-weight:800;font-size:16px;margin-top:12px;cursor:pointer;display:block;text-align:center;text-decoration:none;box-sizing:border-box}
.y{background:#ffcc00;color:#000} .d{background:#222;color:#fff} .err{background:#ff4444;padding:10px;border-radius:10px;font-size:13px;margin-bottom:12px}
</style></head><body>
<div class='box'>
<div style='text-align:center;margin-bottom:20px'><div style='font-size:48px'>🛒</div><h2 style='margin:6px 0'>Buyer Login</h2><div style='opacity:.5;font-size:13px'>Pisah Simple - Khusus Pembeli</div></div>
{% if error %}<div class='err'>{{error}}</div>{% endif %}
<form method='post' action='/login'><input name='username' placeholder='Username Buyer' required autofocus><input name='password' type='password' placeholder='Password' required><button class='btn y'>Login Buyer</button></form>
<a href='/register' class='btn d'>Belum punya akun? Register</a>
<a href='/' class='btn d' style='font-size:12px;opacity:.6'>← Kembali ke Pilihan Login</a>
<div style='font-size:11px;opacity:.4;text-align:center;margin-top:14px'>Test akun:<br>buyer1 / 123456<br><br>Ini halaman khusus Buyer,<br>beda dengan Admin!</div>
</div>
</body></html>
""")
    open(os.path.join(BASE,"templates/admin/login.html"),"w",encoding="utf-8").write("""
<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Admin Login - Pisah Simple</title>
<style>
body{margin:0;background:#111;color:#fff;font-family:sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:16px}
.box{background:#1a1a1a;padding:28px;border-radius:20px;width:100%;max-width:360px;border:2px solid #0088ff}
input{width:100%;padding:14px;background:#222;border:1px solid #333;color:#fff;border-radius:12px;margin:8px 0;box-sizing:border-box;font-size:15px}
.btn{width:100%;padding:14px;border-radius:28px;border:0;font-weight:800;font-size:16px;margin-top:12px;cursor:pointer;display:block;text-align:center;text-decoration:none;box-sizing:border-box}
.b{background:#0088ff;color:#fff} .d{background:#222;color:#fff} .err{background:#ff4444;padding:10px;border-radius:10px;font-size:13px;margin-bottom:12px}
</style></head><body>
<div class='box'>
<div style='text-align:center;margin-bottom:20px'><div style='font-size:48px'>🛡️</div><h2 style='margin:6px 0'>Admin Login</h2><div style='opacity:.5;font-size:13px'>Pisah Simple - Khusus Admin</div></div>
{% if error %}<div class='err'>{{error}}</div>{% endif %}
<form method='post'><input name='username' placeholder='Username Admin' required value='admin' autofocus><input name='password' type='password' placeholder='Password Admin' required><button class='btn b'>Login Admin</button></form>
<div style='background:#222;padding:10px;border-radius:10px;font-size:12px;opacity:.6;text-align:center;margin-top:12px'>Default:<br><b>admin / admin123</b><br><br>Ini halaman khusus Admin,<br>beda dengan Buyer!</div>
<a href='/' class='btn d' style='font-size:12px;opacity:.6'>← Kembali ke Pilihan Login</a>
</div>
</body></html>
""")
    open(os.path.join(BASE,"templates/shop/register.html"),"w",encoding="utf-8").write("""<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Register Buyer</title><style>body{margin:0;background:#0a0a0a;color:#fff;font-family:sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px} .box{background:#171717;padding:24px;border-radius:20px;width:100%;max-width:380px;border:1px solid #333} input,textarea{width:100%;padding:12px;background:#222;border:1px solid #333;color:#fff;border-radius:12px;margin:6px 0;box-sizing:border-box} label{font-size:11px;color:#ffcc00;font-weight:700;margin-top:8px;display:block} .btn{width:100%;padding:14px;border-radius:28px;border:0;font-weight:800;margin-top:12px;cursor:pointer;display:block;text-align:center;text-decoration:none;box-sizing:border-box} .y{background:#ffcc00;color:#000} .d{background:#222;color:#fff} .err{background:#ff4444;padding:10px;border-radius:10px;font-size:13px;margin-bottom:12px}</style></head><body><div class='box'><h2 style='margin:0'>Register Buyer</h2><p style='opacity:.5;font-size:13px'>Daftar pembeli - Simple</p>{% if error %}<div class='err'>{{error}}</div>{% endif %}<form method='post'><label>Username *</label><input name='username' required><label>Email *</label><input name='email' type='email' required><label>Password *</label><input name='password' type='password' required><label>Phone *</label><input name='phone' required><label>Address *</label><textarea name='address' rows='2' required></textarea><button class='btn y'>Register Buyer</button></form><a href='/login' class='btn d'>Sudah punya akun? Login Buyer</a><a href='/' class='btn d' style='font-size:12px;opacity:.6'>← Home</a></div></body></html>""")
    open(os.path.join(BASE,"templates/shop/index.html"),"w",encoding="utf-8").write("""<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Shop Buyer</title><style>body{margin:0;background:#0a0a0a;color:#fff;font-family:sans-serif} header{background:#111;display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:2px solid #ffcc00;position:sticky;top:0;z-index:10} .grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;padding:10px} @media(min-width:800px){.grid{grid-template-columns:repeat(3,1fr)}} .card{background:#171717;border-radius:12px;overflow:hidden;border:1px solid #222} .card img{width:100%;aspect-ratio:1/1;object-fit:cover;background:#222;display:block} .meta{padding:10px} .price{color:#ffcc00;font-weight:800} .btn{width:100%;background:#ffcc00;color:#000;border:0;padding:8px;border-radius:20px;font-weight:800;cursor:pointer;margin-top:6px} .link{color:#ffcc00;text-decoration:none;font-size:13px}</style></head><body><header><div><b>ARMORY</b> - Buyer</div><div style='display:flex;gap:10px;align-items:center'><a href='/cart' class='link'>Cart ({{cart_count}})</a><span style='font-size:12px'>{{user[1]}}</span><a href='/logout' class='link' style='color:#ff4444'>Logout</a></div></header><div class='grid'>{% for p in products %}<div class='card'><a href='/product/{{p[0]}}' style='text-decoration:none;color:#fff'><img src='{{p[6]}}'><div class='meta'><div style='font-size:13px;font-weight:700'>{{p[1]}}</div><div class='price'>${{p[3]}}</div></div></a><div style='padding:0 10px 10px'><form method='post' action='/add_to_cart/{{p[0]}}'><button class='btn'>Add to Cart</button></form></div></div>{% endfor %}</div></body></html>""")
    open(os.path.join(BASE,"templates/shop/detail.html"),"w",encoding="utf-8").write("""<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>{{p[1]}}</title><style>body{margin:0;background:#0a0a0a;color:#fff;font-family:sans-serif} img{width:100%;aspect-ratio:1/1;object-fit:cover;background:#222} .c{padding:16px} .price{color:#ffcc00;font-size:22px;font-weight:800} .btn{width:100%;padding:12px;border-radius:24px;border:0;font-weight:800;margin:8px 0;display:block;text-align:center;text-decoration:none;box-sizing:border-box} .y{background:#ffcc00;color:#000} .d{background:#222;color:#fff}</style></head><body><img src='{{p[6]}}'><div class='c'><h2>{{p[1]}}</h2><div class='price'>${{p[3]}}</div><p>{{p[5]}}</p><form method='post' action='/add_to_cart/{{p[0]}}'><input name='qty' type='number' value='1' min='1' style='width:100%;padding:10px;background:#1e1e1e;border:1px solid #333;color:#fff;border-radius:8px;box-sizing:border-box'><button class='btn y'>Add to Cart</button></form><a class='btn d' href='/shop'>Back</a></div></body></html>""")
    open(os.path.join(BASE,"templates/shop/cart.html"),"w",encoding="utf-8").write("""<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Cart</title><style>body{margin:0;background:#0a0a0a;color:#fff;font-family:sans-serif} header{background:#111;padding:12px;display:flex;justify-content:space-between;border-bottom:2px solid #ffcc00;position:sticky;top:0} .item{display:flex;gap:10px;background:#171717;margin:10px;padding:10px;border-radius:12px;border:1px solid #222;align-items:center} .item img{width:70px;height:70px;object-fit:cover;border-radius:8px;background:#222} .total{background:#111;padding:16px;border-top:2px solid #ffcc00} .btn{width:100%;padding:12px;border-radius:24px;font-weight:800;border:0;display:block;text-align:center;text-decoration:none;margin:6px 0;box-sizing:border-box;cursor:pointer} .y{background:#ffcc00;color:#000} .d{background:#222;color:#fff} input,textarea{width:100%;padding:11px;background:#1e1e1e;border:1px solid #333;color:#fff;border-radius:10px;margin:5px 0;box-sizing:border-box} label{font-size:11px;color:#ffcc00;font-weight:700;margin-top:8px;display:block}</style></head><body><header><div>Cart ({{cart|length}})</div><div style='font-size:12px'>{{user[1]}} | <a href='/shop' style='color:#ffcc00'>Shop</a></div></header>{% if not cart %}<div style='padding:40px;text-align:center'>Empty<br><a href='/shop' style='background:#ffcc00;color:#000;padding:10px 20px;border-radius:20px;text-decoration:none'>Shop</a></div>{% else %}<div>{% for it in cart %}<div class='item'><img src='{{it.image}}'><div style='flex:1'><b>{{it.name}}</b><br>${{it.price}} x {{it.qty}} = <b style='color:#ffcc00'>${{it.subtotal}}</b></div><a href='/remove/{{it.id}}' style='color:#ff4444;text-decoration:none'>✕</a></div>{% endfor %}</div><div class='total'><div>Total: <b style='color:#ffcc00;font-size:20px'>${{total}}</b></div><div style='background:#1a1a1a;padding:14px;border-radius:12px;margin-top:12px'><form method='post' action='/checkout'><label>Name *</label><input name='customer' required value='{{user[1]}}'><label>Phone *</label><input name='phone' required value='{{user[4]}}'><label>Address *</label><textarea name='address' rows='2' required>{{user[5]}}</textarea><button class='btn y' type='submit'>Checkout ${{total}}</button></form></div><a class='btn d' href='/clear'>Clear</a></div>{% endif %}</body></html>""")
    open(os.path.join(BASE,"templates/shop/my_orders.html"),"w",encoding="utf-8").write("""<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Orders</title><style>body{margin:0;background:#0a0a0a;color:#fff;font-family:sans-serif} header{background:#111;padding:12px;display:flex;justify-content:space-between;border-bottom:2px solid #ffcc00} .order{background:#171717;margin:10px;padding:14px;border-radius:12px;border-left:4px solid #ffcc00} .badge{background:#ffcc00;color:#000;padding:3px 8px;border-radius:10px;font-size:10px;font-weight:800}</style></head><body><header><div>My Orders - {{user[1]}}</div><div><a href='/shop' style='color:#ffcc00'>Shop</a> | <a href='/logout' style='color:#ff4444'>Logout</a></div></header>{% for o in orders %}<div class='order'><div style='display:flex;justify-content:space-between'><b>#{{o[0]}}</b><span class='badge'>{{o[9]}}</span></div><div style='font-size:11px;opacity:.6'>{{o[10]}}</div><hr style='border:0;border-top:1px solid #333'><b>{{o[6]}}</b><br>Total: <span style='color:#ffcc00;font-size:18px'>${{o[8]}}</span></div>{% else %}<div style='padding:40px;text-align:center;opacity:.6'>No orders</div>{% endfor %}</body></html>""")
    open(os.path.join(BASE,"templates/admin/dashboard.html"),"w",encoding="utf-8").write("""<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Admin Dashboard</title><style>body{margin:0;font-family:sans-serif;background:#f2f2f2} .top{background:#111;color:#ffcc00;padding:12px;display:flex;justify-content:space-between} .menu{display:flex;gap:6px;background:#1e1e1e;padding:8px;overflow-x:auto} .menu a{padding:8px 14px;border-radius:20px;text-decoration:none;font-size:12px;font-weight:700;white-space:nowrap} .a{background:#ffcc00;color:#000} .i{background:#333;color:#fff} .grid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;padding:10px} .card{background:#fff;padding:12px;border-radius:10px;text-align:center} table{width:100%;background:#fff;border-collapse:collapse;font-size:12px} th,td{padding:8px;border-bottom:1px solid #eee;text-align:left} img{width:40px;height:40px;object-fit:cover;border-radius:6px;background:#eee} .btn{padding:5px 10px;border-radius:8px;text-decoration:none;font-size:11px;font-weight:700}</style></head><body><div class='top'><div>Admin Dashboard - Pisah</div><div><a href='/admin/logout' style='color:#ff4444;text-decoration:none;font-size:12px'>Logout</a> | <a href='/' style='color:#ffcc00'>Home</a></div></div><div class='menu'><a class='a' href='/admin'>Products ({{stat[0]}})</a><a class='i' href='/admin/orders'>Orders ({{order_count}})</a><a class='i' href='/admin/users'>Users ({{user_count}})</a><a class='i' href='/admin/add'>Add</a></div><div class='grid'><div class='card'><b>{{stat[0]}}</b><br>Products</div><div class='card'><b style='color:red'>{{low}}</b><br>Low</div><div class='card'><b>${{ (stat[1] or 0) | int }}</b><br>Value</div><div class='card'><b>{{order_count}}</b><br>Orders</div></div><table><tr><th>Product</th><th>Stock</th><th>Action</th></tr>{% for p in products %}<tr><td><img src='{{p[6]}}'> {{p[1][:20]}}<br>${{p[3]}}</td><td>{{p[4]}}</td><td><a class='btn' style='background:#111;color:#fff' href='/admin/edit/{{p[0]}}'>Edit</a> <a class='btn' style='background:#e53935;color:#fff' href='/admin/delete/{{p[0]}}'>Del</a></td></tr>{% endfor %}</table></body></html>""")
    open(os.path.join(BASE,"templates/admin/form.html"),"w",encoding="utf-8").write("""<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Form</title><style>body{margin:0;font-family:sans-serif;background:#f2f2f2} .top{background:#111;color:#ffcc00;padding:12px} .box{background:#fff;padding:16px;border-radius:12px;max-width:480px;margin:12px auto} input,textarea,select{width:100%;padding:10px;margin:6px 0 10px;border:1px solid #ccc;border-radius:8px;box-sizing:border-box} .btn{width:100%;padding:12px;background:#ffcc00;border:0;border-radius:20px;font-weight:800}</style></head><body><div class='top'><a href='/admin' style='color:#ffcc00;text-decoration:none'>← Back</a></div><div class='box'><h3>{{ 'Edit' if p else 'Add' }} Product</h3><form method='post' enctype='multipart/form-data'><input name='name' required placeholder='Name' value="{{p[1] if p else ''}}"><select name='category'><option>Gear</option><option>Ammo</option><option>Pistol</option><option>Rifle</option></select><input name='price' type='number' step='0.01' required placeholder='Price' value="{{p[3] if p else ''}}"><input name='stock' type='number' required placeholder='Stock' value="{{p[4] if p else ''}}"><input name='spec' placeholder='Spec' value="{{p[7] if p else ''}}"><textarea name='description' placeholder='Desc'>{{p[5] if p else ''}}</textarea><input name='image_url' placeholder='Image URL' value="{{p[6] if p else ''}}"><input type='file' name='image_file' accept='image/*'><button class='btn'>Save</button></form></div></body></html>""")
    open(os.path.join(BASE,"templates/admin/orders.html"),"w",encoding="utf-8").write("""<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Admin Orders</title><style>body{margin:0;font-family:sans-serif;background:#f2f2f2} .top{background:#111;color:#ffcc00;padding:12px;display:flex;justify-content:space-between} .menu{display:flex;gap:6px;background:#1e1e1e;padding:8px} .menu a{padding:8px 14px;border-radius:20px;text-decoration:none;font-size:12px;font-weight:700} .a{background:#ffcc00;color:#000} .i{background:#333;color:#fff} .order{background:#fff;margin:10px;padding:12px;border-radius:12px;border-left:4px solid #ffcc00}</style></head><body><div class='top'><div>Orders Admin - Pisah</div><div><a href='/admin' style='color:#ffcc00'>Dashboard</a> | <a href='/admin/logout' style='color:#ff4444;text-decoration:none'>Logout</a></div></div><div class='menu'><a class='i' href='/admin'>Products</a><a class='a' href='/admin/orders'>Orders ({{orders|length}})</a><a class='i' href='/admin/users'>Users</a><a class='i' href='/admin/add'>Add</a></div>{% for o in orders %}<div class='order'><b>#{{o[0]}} {{o[10]}}</b> - {{o[9]}}<br>User ID: {{o[1]}}<br><b>{{o[2]}}</b><br>📱 {{o[4]}}<br>Items: {{o[6]}}<br>Total: <b style='color:red'>${{o[8]}}</b></div>{% else %}<div style='padding:30px;text-align:center'>No orders</div>{% endfor %}</body></html>""")
    open(os.path.join(BASE,"templates/admin/users.html"),"w",encoding="utf-8").write("""<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Users</title><style>body{margin:0;font-family:sans-serif;background:#f2f2f2} .top{background:#111;color:#ffcc00;padding:12px} .menu{display:flex;gap:6px;background:#1e1e1e;padding:8px} .menu a{padding:8px 14px;border-radius:20px;text-decoration:none;font-size:12px;font-weight:700} .a{background:#ffcc00;color:#000} .i{background:#333;color:#fff} table{width:100%;background:#fff;border-collapse:collapse;font-size:11px} th,td{padding:8px;border-bottom:1px solid #eee;text-align:left}</style></head><body><div class='top'>Users - {{users|length}} <a href='/admin' style='color:#ffcc00;float:right'>Dashboard</a></div><div class='menu'><a class='i' href='/admin'>Products</a><a class='i' href='/admin/orders'>Orders</a><a class='a' href='/admin/users'>Users</a><a class='i' href='/admin/add'>Add</a></div><table><tr><th>ID</th><th>Username</th><th>Role</th><th>Joined</th></tr>{% for u in users %}<tr><td>{{u[0]}}</td><td><b>{{u[1]}}</b><br>{{u[2]}}</td><td>{{u[7]}}</td><td>{{u[6]}}</td></tr>{% endfor %}</table></body></html>""")

from flask import Flask, render_template, request, redirect, session, jsonify
def get_conn(): return sqlite3.connect(DB_PATH)
def get_cart(): return session.get('cart', {})
def cart_count(): return sum(get_cart().values()) if get_cart() else 0
def cart_details():
    cart = get_cart()
    if not cart: return [], 0
    conn = get_conn(); c = conn.cursor()
    items=[]; total=0
    for pid, qty in cart.items():
        c.execute("SELECT * FROM products WHERE id=?", (pid,)); p=c.fetchone()
        if p:
            img = p[6] or "https://via.placeholder.com/500"
            sub=p[3]*qty
            items.append({'id':p[0],'name':p[1],'price':p[3],'qty':qty,'subtotal':round(sub,2),'image':img})
            total+=sub
    conn.close()
    return items, round(total,2)

def get_current_user():
    uid = session.get('buyer_id')
    if not uid: return None
    conn=get_conn(); c=conn.cursor(); c.execute("SELECT * FROM users WHERE id=?", (uid,)); u=c.fetchone(); conn.close()
    return u

def buyer_login_required(f):
    @wraps(f)
    def d(*args, **kwargs):
        if not session.get('buyer_id'): return redirect('/login')
        return f(*args, **kwargs)
    return d

def admin_login_required(f):
    @wraps(f)
    def d(*args, **kwargs):
        if not session.get('admin_logged_in'): return redirect('/admin/login')
        return f(*args, **kwargs)
    return d

app = Flask(__name__, template_folder=os.path.join(BASE,"templates/shop"), static_folder=os.path.join(BASE,"static"))
app.secret_key = SECRET
app.config['UPLOAD_FOLDER']=UPLOAD

@app.route("/")
def landing(): return render_template("landing.html")

@app.route("/shop")
def shop_home():
    conn=get_conn(); c=conn.cursor(); c.execute("SELECT * FROM products ORDER BY id DESC"); products=c.fetchall(); conn.close()
    user = get_current_user()
    if not user: return render_template("index.html", products=products, cart_count=cart_count(), user=None)
    if user[7]=='admin': return redirect("/admin")
    return render_template("index.html", products=products, cart_count=cart_count(), user=user)

@app.route("/product/<int:pid>")
def detail(pid):
    conn=get_conn(); c=conn.cursor(); c.execute("SELECT * FROM products WHERE id=?", (pid,)); pr=c.fetchone(); conn.close()
    if not pr: return ("Not found",404)
    return render_template("detail.html", p=pr, cart_count=cart_count(), user=get_current_user())

@app.route("/register", methods=["GET","POST"])
def register():
    error=None
    if request.method=="POST":
        username=request.form.get('username','').strip()
        email=request.form.get('email','').strip()
        password=request.form.get('password','')
        phone=request.form.get('phone','').strip()
        address=request.form.get('address','').strip()
        if len(password)<6: error="Password min 6"
        elif not username or not email or not phone or not address: error="Semua wajib isi"
        else:
            conn=get_conn(); c=conn.cursor()
            c.execute("SELECT id FROM users WHERE username=?", (username,))
            if c.fetchone(): error="Username sudah dipakai"
            else:
                from datetime import datetime
                hashed=generate_password_hash(password)
                c.execute("INSERT INTO users VALUES (NULL,?,?,?,?,?,?,?)", (username,email,hashed,phone,address,datetime.now().strftime("%d-%m %Y"),"buyer"))
                conn.commit(); c.execute("SELECT id FROM users WHERE username=?", (username,)); uid=c.fetchone()[0]; conn.close()
                session['buyer_id']=uid; session['buyer_username']=username
                return redirect("/shop")
            conn.close()
    return render_template("register.html", error=error)

@app.route("/login", methods=["GET","POST"])
def buyer_login():
    error=None
    if request.method=="POST":
        username=request.form.get('username','').strip()
        password=request.form.get('password','')
        conn=get_conn(); c=conn.cursor(); c.execute("SELECT * FROM users WHERE username=?", (username,)); u=c.fetchone(); conn.close()
        if u and check_password_hash(u[3], password):
            if u[7]=='admin':
                error="Ini akun Admin. Silakan login di /admin/login"
            else:
                session['buyer_id']=u[0]; session['buyer_username']=u[1]
                session.pop('admin_logged_in', None)
                return redirect("/shop")
        else: error="Username/password salah"
    return render_template("login.html", error=error)

@app.route("/logout")
def buyer_logout():
    session.clear()
    return redirect("/")

@app.route("/add_to_cart/<int:pid>", methods=["POST"])
@buyer_login_required
def add_to_cart(pid):
    user=get_current_user()
    if not user or user[7]=='admin': return redirect("/admin")
    qty=int(request.form.get('qty',1))
    cart=get_cart(); cart[str(pid)]=cart.get(str(pid),0)+qty; session['cart']=cart
    return redirect("/cart")

@app.route("/cart")
@buyer_login_required
def cart_page():
    items,total=cart_details()
    return render_template("cart.html", cart=items, total=total, user=get_current_user())

@app.route("/remove/<int:pid>")
@buyer_login_required
def remove(pid):
    cart=get_cart()
    if str(pid) in cart: del cart[str(pid)]
    session['cart']=cart
    return redirect("/cart")

@app.route("/clear")
@buyer_login_required
def clear():
    session['cart']={}
    return redirect("/cart")

@app.route("/checkout", methods=["POST"])
@buyer_login_required
def checkout():
    items,total=cart_details()
    if not items: return redirect("/shop")
    user=get_current_user()
    customer=request.form.get('customer','').strip() or user[1]
    phone=request.form.get('phone','').strip() or user[4]
    address=request.form.get('address','').strip() or user[5]
    email=user[2]
    conn=get_conn(); c=conn.cursor()
    from datetime import datetime
    prod_summary=", ".join([f"{it['name']} x{it['qty']}" for it in items])
    c.execute("INSERT INTO orders VALUES (NULL,?,?,?,?,?,?,?,?,?,?)", (user[0],customer,email,phone,address,prod_summary,len(items),total,"Paid",datetime.now().strftime("%d-%m %H:%M")))
    for it in items:
        c.execute("UPDATE products SET stock=stock-?, sold=sold+? WHERE id=?", (it['qty'], it['qty'], it['id']))
    conn.commit(); conn.close()
    session['cart']={}
    return f"<div style='font-family:sans-serif;padding:20px;max-width:500px;margin:auto;text-align:center;background:#0a0a0a;color:#fff;min-height:100vh'><h1>✅ Sukses!</h1><p>{customer}<br>{phone}<br>{address}</p><p>Total ${total}</p><a href='/my_orders' style='background:#ffcc00;padding:12px 20px;border-radius:20px;text-decoration:none;color:#000;font-weight:800;display:block'>Lihat Pesanan</a><br><a href='/shop' style='background:#222;color:#fff;padding:10px 20px;border-radius:20px;text-decoration:none;display:block'>Belanja Lagi</a></div>"

@app.route("/my_orders")
@buyer_login_required
def my_orders():
    user=get_current_user()
    if not user or user[7]=='admin': return redirect("/admin")
    conn=get_conn(); c=conn.cursor(); c.execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC", (user[0],)); orders=c.fetchall(); conn.close()
    return render_template("my_orders.html", orders=orders, user=user)

@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    error=None
    if request.method=="POST":
        u=request.form.get('username',''); p=request.form.get('password','')
        conn=get_conn(); c=conn.cursor(); c.execute("SELECT * FROM users WHERE username=?", (u,)); user=c.fetchone(); conn.close()
        if (u=="admin" and p=="admin123") or (user and check_password_hash(user[3], p) and user[7]=='admin'):
            session['admin_logged_in']=True
            if user: session['buyer_id']=user[0]
            else:
                conn=get_conn(); c=conn.cursor(); c.execute("SELECT * FROM users WHERE username='admin'"); adm=c.fetchone(); conn.close()
                if adm: session['buyer_id']=adm[0]
            return redirect("/admin")
        else: error="Salah username/password admin"
    return render_template("login.html", error=error)

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect("/admin/login")

@app.route("/admin")
@admin_login_required
def a_home():
    conn=get_conn(); c=conn.cursor(); c.execute("SELECT COUNT(*), SUM(price*stock) FROM products"); stat=c.fetchone()
    c.execute("SELECT COUNT(*) FROM products WHERE stock<=3"); low=c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM orders"); order_count=c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM users"); user_count=c.fetchone()[0] or 0
    c.execute("SELECT * FROM products ORDER BY id DESC"); products=c.fetchall(); conn.close()
    return render_template("dashboard.html", products=products, stat=stat, low=low, order_count=order_count, user_count=user_count)

@app.route("/admin/orders")
@admin_login_required
def a_orders():
    conn=get_conn(); c=conn.cursor(); c.execute("SELECT * FROM orders ORDER BY id DESC"); orders=c.fetchall(); conn.close()
    return render_template("orders.html", orders=orders)

@app.route("/admin/users")
@admin_login_required
def a_users():
    conn=get_conn(); c=conn.cursor(); c.execute("SELECT * FROM users ORDER BY id DESC"); users=c.fetchall(); conn.close()
    return render_template("users.html", users=users)

@app.route("/admin/add", methods=["GET","POST"])
@app.route("/admin/edit/<int:pid>", methods=["GET","POST"])
@admin_login_required
def a_form(pid=None):
    conn=get_conn(); c=conn.cursor(); pr=None
    if pid: c.execute("SELECT * FROM products WHERE id=?", (pid,)); pr=c.fetchone()
    if request.method=="POST":
        name=request.form['name']; cat=request.form['category']; price=float(request.form['price'] or 0); stock=int(request.form['stock'] or 0)
        spec=request.form.get('spec',''); desc=request.form.get('description',''); img=request.form.get('image_url','')
        if 'image_file' in request.files:
            f=request.files['image_file']
            if f and f.filename!='':
                fn=secure_filename(f.filename); fn=f"{int(time.time())}_{fn}"; path=os.path.join(UPLOAD, fn); f.save(path); img=f"/static/uploads/{fn}"
        if not img: img="https://via.placeholder.com/500"
        if pid: c.execute("UPDATE products SET name=?,category=?,price=?,stock=?,description=?,image_url=?,spec=?,featured=?,rating=?,sold=? WHERE id=?", (name,cat,price,stock,desc,img,spec,1,4.8,0,pid))
        else: c.execute("INSERT INTO products VALUES (NULL,?,?,?,?,?,?,?,?,?,?)", (name,cat,price,stock,desc,img,spec,1,4.8,0))
        conn.commit(); conn.close(); return redirect("/admin")
    conn.close(); return render_template("form.html", p=pr)

@app.route("/admin/delete/<int:pid>")
@admin_login_required
def a_del(pid):
    conn=get_conn(); c=conn.cursor(); c.execute("DELETE FROM products WHERE id=?", (pid,)); conn.commit(); conn.close(); return redirect("/admin")

create_templates()
init_db()

if __name__ == "__main__":
    print("\n" + "="*70)
    print("✅ LOGIN PISAH SIMPLE - NO NGROK ERROR")
    print("="*70)
    print(f"IP: {WIFI_IP}")
    print(f"Local: http://127.0.0.1:5000/")
    print(f"1 WiFi: http://{WIFI_IP}:5000/")
    print("")
    print("PISAH LOGIN:")
    print(f"  Buyer: http://{WIFI_IP}:5000/login  buyer1/123456")
    print(f"  Admin: http://{WIFI_IP}:5000/admin/login  admin/admin123")
    print("")
    print("Untuk ALL WIFI (tanpa ngrok): Deploy ke render.com gratis")
    print("="*70 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
