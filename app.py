from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
from flask import send_file
from datetime import date
import os
from datetime import datetime
from openpyxl import Workbook
from flask import send_file
import io
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

import io
import random

import os
import subprocess

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

app = Flask(__name__)
app.config.from_object("config.Config")
app.secret_key = "warehouse123"

db = SQLAlchemy(app)

# Model User
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(255))
    nama = db.Column(db.String(100))
    role = db.Column(db.String(20))
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime)


# Model Product
class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(50))
    sku = db.Column(db.String(50))
    nama_barang = db.Column(db.String(200))
    kategori = db.Column(db.String(100))
    satuan = db.Column(db.String(50))
    stok = db.Column(db.Integer)
    stok_minimum = db.Column(db.Integer)
    lead_time = db.Column(db.Integer)
    lokasi_rak = db.Column(db.String(50))
    harga_beli = db.Column(db.Numeric(15,2))
    harga_jual = db.Column(db.Numeric(15,2))

class GoodsReceipt(db.Model):
    __tablename__ = "goods_receipts"

    id = db.Column(db.Integer, primary_key=True)
    nomor_gr = db.Column(db.String(50))
    supplier_id = db.Column(db.Integer)
    tanggal = db.Column(db.Date)
    user_id = db.Column(db.Integer)

class TransactionHistory(db.Model):
    __tablename__ = "transaction_history"

    id = db.Column(db.Integer, primary_key=True)

    tanggal = db.Column(
        db.DateTime,
        default=datetime.now
    )

    jenis = db.Column(db.String(20))
    product_id = db.Column(db.Integer)
    qty = db.Column(db.Integer)
    keterangan = db.Column(db.String(255))
    user_id = db.Column(db.Integer)

def save_log(user_id, aktivitas):

    db.session.execute(
        db.text("""
            INSERT INTO audit_logs
            (
                user_id,
                aktivitas
            )
            VALUES
            (
                :user_id,
                :aktivitas
            )
        """),
        {
            "user_id": user_id,
            "aktivitas": aktivitas
        }
    )

def check_role(roles):

    if "user_id" not in session:

        return False

    if session["role"] not in roles:

        return False

    return True


@app.route("/")
def home():

    if "user_id" not in session:
        return redirect("/login")

    total_produk = db.session.execute(
        db.text("SELECT COUNT(*) FROM products")
    ).scalar()

    total_supplier = db.session.execute(
        db.text("SELECT COUNT(*) FROM suppliers")
    ).scalar()

    total_agen = db.session.execute(
        db.text("SELECT COUNT(*) FROM agents")
    ).scalar()

    total_stok = db.session.execute(
        db.text("SELECT COALESCE(SUM(stok),0) FROM products")
    ).scalar()

    low_stock = db.session.execute(
        db.text("""
           SELECT *
           FROM products
           WHERE stok <= stok_minimum
           ORDER BY stok ASC
        """)
    ).mappings()

    monthly_in = db.session.execute(
        db.text("""
            SELECT
                DATE_FORMAT(tanggal,'%Y-%m') bulan,
                SUM(qty) total
            FROM transaction_history
            WHERE jenis='MASUK'
            GROUP BY bulan
            ORDER BY bulan
        """)
    ).mappings().all()

    monthly_out = db.session.execute(
        db.text("""
            SELECT
                DATE_FORMAT(tanggal,'%Y-%m') bulan,
                SUM(qty) total
            FROM transaction_history
            WHERE jenis='KELUAR'
            GROUP BY bulan
            ORDER BY bulan
        """)
    ).mappings().all()

    top_products = db.session.execute(
        db.text("""
            SELECT
                p.nama_barang,
                SUM(t.qty) total_keluar

            FROM transaction_history t

            LEFT JOIN products p
            ON p.id = t.product_id

            WHERE t.jenis='KELUAR'

            GROUP BY p.id

            ORDER BY total_keluar DESC

            LIMIT 10
        """)
    ).mappings().all()

    inventory_value = db.session.execute(
        db.text("""
            SELECT
                COALESCE(
                SUM(stok * harga_beli),
                0
                )
            FROM products
        """)
    ).scalar()

    slow_moving = db.session.execute(
        db.text("""
            SELECT
               p.nama_barang,

               MAX(t.tanggal) last_transaction,

               DATEDIFF(
                   CURDATE(),
                   MAX(t.tanggal)
                ) days_idle

            FROM products p

            LEFT JOIN transaction_history t
            ON t.product_id = p.id

            GROUP BY p.id

            HAVING days_idle >= 30

            ORDER BY days_idle DESC

            LIMIT 10
        """)
    ).mappings().all()

    monthly_revenue = db.session.execute(
        db.text("""
            SELECT
                COALESCE(
                   SUM(
                    qty * harga_jual
                   ),
                   0
                )
            FROM delivery_order_details
        """)
    ).scalar()

    gross_profit = db.session.execute(
        db.text("""
            SELECT
                COALESCE(
                    SUM(
                       qty *
                       (
                           harga_jual -
                           (
                               SELECT harga_beli
                               FROM products p
                               WHERE p.id =
                               delivery_order_details.product_id
                            )
                        )
                    ),
                    0
                )
            FROM delivery_order_details
        """)
    ).scalar()

    top_agents = db.session.execute(
        db.text("""
            SELECT
                a.nama_agen,
                SUM(dod.subtotal) total_penjualan

            FROM delivery_order_details dod

            JOIN delivery_orders doo
            ON doo.id = dod.delivery_order_id

            JOIN agents a
            ON a.id = doo.agent_id

            GROUP BY a.id

            ORDER BY total_penjualan DESC

            LIMIT 10
        """)
    ).mappings().all()

    top_suppliers = db.session.execute(
        db.text("""
            SELECT
                s.nama_supplier,
                SUM(pod.subtotal) total_pembelian

            FROM purchase_order_details pod

            JOIN purchase_orders po
            ON po.id = pod.purchase_order_id

            JOIN suppliers s
            ON s.id = po.supplier_id

            GROUP BY s.id

            ORDER BY total_pembelian DESC

            LIMIT 10
        """)
    ).mappings().all()

    return render_template(
        "dashboard.html",
        total_produk=total_produk,
        total_supplier=total_supplier,
        total_agen=total_agen,
        total_stok=total_stok,
        inventory_value=inventory_value,
        monthly_revenue=monthly_revenue,
        gross_profit=gross_profit,
        low_stock=low_stock,
        monthly_in=monthly_in,
        monthly_out=monthly_out,
        top_products=top_products,
        slow_moving=slow_moving,
        top_agents=top_agents,
        top_suppliers=top_suppliers
    )

@app.route("/users")
def users():

    if not check_role(["admin"]):

        flash(
            "Akses ditolak",
            "danger"
        )

        return redirect("/")

    data = User.query.all()

    return render_template(
        "users.html",
        users=data
    )

@app.route(
    "/users/add",
    methods=["GET","POST"]
)
def users_add():

    if not check_role(["admin"]):
        return redirect("/")

    if request.method == "POST":

        user = User(
            nama=request.form["nama"],
            username=request.form["username"],
            password=generate_password_hash(
                request.form["password"]
            ),
            role=request.form["role"],
            status=1
        )

        db.session.add(user)
        db.session.commit()

        save_log(
            session["user_id"],
            f"Menambah user {user.username}"
        )

        db.session.commit()

        flash(
            "User berhasil dibuat",
            "success"
        )

        return redirect("/users")

    return render_template(
        "users_add.html"
    )

@app.route(
    "/users/edit/<int:user_id>",
    methods=["GET","POST"]
)
def users_edit(user_id):

    if not check_role(["admin"]):
        return redirect("/")

    user = User.query.get_or_404(user_id)

    if request.method == "POST":

        user.nama = request.form["nama"]
        user.username = request.form["username"]
        user.role = request.form["role"]

        if request.form["password"]:
            user.password = generate_password_hash(
                request.form["password"]
            )

        db.session.commit()

        save_log(
            session["user_id"],
            f"Edit User {user.username}"
        )

        db.session.commit()

        flash(
            "User berhasil diupdate",
            "success"
        )

        return redirect("/users")

    return render_template(
        "users_edit.html",
        user=user
    )

@app.route("/users/delete/<int:user_id>")
def users_delete(user_id):

    if not check_role(["admin"]):
        return redirect("/")

    user = User.query.get_or_404(user_id)

    if user.id == session["user_id"]:

        flash(
            "Tidak bisa menghapus akun sendiri",
            "danger"
        )

        return redirect("/users")

    username = user.username

    db.session.delete(user)
    db.session.commit()

    save_log(
        session["user_id"],
        f"Hapus User {username}"
    )

    db.session.commit()

    flash(
        "User berhasil dihapus",
        "success"
    )

    return redirect("/users")

@app.route("/users/reset-password/<int:user_id>")
def users_reset_password(user_id):

    if not check_role(["admin"]):
        return redirect("/")

    user = User.query.get_or_404(user_id)

    user.password = "123456"

    db.session.commit()

    save_log(
        session["user_id"],
        f"Reset Password User {user.username}"
    )

    db.session.commit()

    flash(
        f"Password {user.username} berhasil direset menjadi 123456",
        "success"
    )

    return redirect("/users")

@app.route("/users/toggle/<int:id>")
def users_toggle(id):

    if not check_role(["admin"]):
        return redirect("/")

    user = User.query.get_or_404(id)

    user.status = 0 if user.status == 1 else 1

    db.session.commit()

    flash(
        "Status user berhasil diubah",
        "success"
    )

    return redirect("/users")

@app.route("/backup")
def backup_database():

    if not check_role(["admin","owner"]):

        flash(
            "Akses ditolak",
            "danger"
        )

        return redirect("/")

    filename = (
        "backup_" +
        datetime.now().strftime("%Y%m%d_%H%M%S")
        + ".sql"
    )

    backup_folder = "backup"

    os.makedirs(
        backup_folder,
        exist_ok=True
    )

    filepath = os.path.join(
        backup_folder,
        filename
    )

    command = [
        r"C:\xampp\mysql\bin\mysqldump.exe",
        "-u",
        "root",
        "--routines",
        "--triggers",
        "--events",
        "warehouse_db"
    ]

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as f:

        result = subprocess.run(
            command,
            stdout=f,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:

            flash(
                "Backup gagal",
                "danger"
            )

            return redirect("/")

    save_log(
        session["user_id"],
        f"Backup Database {filename}"
    )

    db.session.execute(
        db.text("""
            INSERT INTO backup_logs
            (
                tanggal,
                user_id,
                nama_file
            )
            VALUES
            (
                NOW(),
                :user_id,
                :nama_file
            )
        """),
        {
            "user_id": session["user_id"],
            "nama_file": filename
        }
    )

    db.session.commit()

    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename
    )

@app.route("/backup/logs")
def backup_logs():

    if not check_role(
        ["admin","owner"]
    ):

        flash(
            "Akses ditolak",
            "danger"
        )

        return redirect("/")

    data = db.session.execute(
        db.text("""
            SELECT
                b.*,
                u.nama

            FROM backup_logs b

            LEFT JOIN users u
            ON u.id = b.user_id

            ORDER BY b.id DESC
        """)
    ).mappings().all()

    return render_template(
        "backup_logs.html",
        data=data
    )

@app.route(
    "/backup/log/delete/<int:id>"
)
def backup_log_delete(id):

    db.session.execute(
        db.text("""
            DELETE
            FROM backup_logs
            WHERE id=:id
        """),
        {"id": id}
    )

    db.session.commit()

    flash(
        "Log berhasil dihapus",
        "success"
    )

    return redirect(
        "/backup/logs"
    )

@app.route(
    "/restore",
    methods=["GET","POST"]
)
def restore_database():

    if not check_role(["admin"]):

        flash(
            "Akses ditolak",
            "danger"
        )

        return redirect("/")

    if request.method == "POST":

        file = request.files["file"]

        if file.filename == "":

            flash(
                "Pilih file backup",
                "danger"
            )

            return redirect("/restore")

        upload_folder = "restore"

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        filepath = os.path.join(
            upload_folder,
            file.filename
        )

        file.save(filepath)

        command = (
            r'C:\xampp\mysql\bin\mysql.exe '
            '-u root warehouse_db '
            f'< "{filepath}"'
        )

        os.system(command)

        save_log(
            session["user_id"],
            f"Restore Database {file.filename}"
        )

        db.session.commit()

        flash(
            "Database berhasil direstore",
            "success"
        )

        return redirect("/")
    
    return render_template(
        "restore.html"
    )

from werkzeug.security import check_password_hash

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username
        ).first()

        if user:

            if user.status == 0:

                flash(
                    "User tidak aktif",
                    "danger"
                )

                return redirect("/login")

            password_valid = (
                user.password == password
                or
                check_password_hash(
                    user.password,
                    password
                )
            )

            if password_valid:

                session["user_id"] = user.id
                session["nama"] = user.nama
                session["role"] = user.role

                save_log(
                    user.id,
                    "Login ke sistem"
                )

                db.session.commit()

                flash(
                    "Login berhasil",
                    "success"
                )

                return redirect("/")

        flash(
            "Username atau Password salah",
            "danger"
        )

        return redirect("/login")

    return render_template(
        "login.html"
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route(
    "/change-password",
    methods=["GET","POST"]
)
def change_password():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        old_password = request.form["old_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        user = User.query.get(
            session["user_id"]
        )

        if user.password != old_password:

            flash(
                "Password lama salah",
                "danger"
            )

            return redirect(
                "/change-password"
            )

        if new_password != confirm_password:

            flash(
                "Konfirmasi password tidak sama",
                "danger"
            )

            return redirect(
                "/change-password"
            )

        user.password = new_password

        db.session.commit()

        save_log(
            session["user_id"],
            "Mengubah password"
        )

        db.session.commit()

        flash(
            "Password berhasil diubah",
            "success"
        )

        return redirect("/")

    return render_template(
        "change_password.html"
    )

@app.route("/products")
def products():

    if session.get("role") != "admin":

        flash(
            "Anda tidak memiliki akses",
            "danger"
        )

        return redirect("/")

    keyword = request.args.get("keyword", "")

    if keyword:

        data_produk = Product.query.filter(
            Product.nama_barang.contains(keyword)
        ).all()

    else:

        data_produk = Product.query.all()

    return render_template(
        "products.html",
        products=data_produk,
        keyword=keyword
    )

@app.route("/products/add", methods=["GET","POST"])
def add_product():

    if request.method == "POST":

        product = Product(
            barcode=request.form["barcode"],
            sku=request.form["sku"],
            nama_barang=request.form["nama_barang"],
            kategori=request.form["kategori"],
            satuan=request.form["satuan"],
            stok=request.form["stok"],
            stok_minimum=request.form["stok_minimum"],
            lead_time=request.form["lead_time"],
            lokasi_rak=request.form["lokasi_rak"],
            harga_beli=request.form["harga_beli"],
            harga_jual=request.form["harga_jual"]
        )

        db.session.add(product)
        db.session.commit()

        return redirect("/products")

    return render_template("add_product.html")

@app.route("/products/delete/<int:id>")
def delete_product(id):

    product = Product.query.get_or_404(id)

    db.session.delete(product)

    db.session.commit()

    return redirect("/products")

@app.route("/products/edit/<int:id>", methods=["GET", "POST"])
def edit_product(id):

    product = Product.query.get_or_404(id)

    if request.method == "POST":

        product.barcode = request.form["barcode"]
        product.sku = request.form["sku"]
        product.nama_barang = request.form["nama_barang"]
        product.kategori = request.form["kategori"]
        product.satuan = request.form["satuan"]
        product.stok = request.form["stok"]
        product.stok_minimum = request.form["stok_minimum"]
        product.lead_time = int(
            request.form.get(
                "lead_time",
                7
            )
        )
        product.lokasi_rak = request.form["lokasi_rak"]
        product.harga_beli = request.form["harga_beli"]
        product.harga_jual = request.form["harga_jual"]

        db.session.commit()

        return redirect("/products")

    return render_template(
        "edit_product.html",
        product=product
    )

@app.route("/goods-receipt/add", methods=["GET", "POST"])
def add_goods_receipt():

    suppliers = db.session.execute(
        db.text("SELECT * FROM suppliers")
    ).mappings()

    products = Product.query.all()

    if request.method == "POST":

        product_id = request.form["product_id"]
        qty = int(request.form["qty"])

        product = Product.query.get(product_id)

        product.stok += qty

        history = TransactionHistory(
           jenis="MASUK",
           product_id=product.id,
           qty=qty,
           keterangan="Barang Masuk",
           user_id=session["user_id"]
        )

        db.session.add(history)

        db.session.commit()

        return redirect("/products")

    return render_template(
        "goods_receipt_add.html",
        suppliers=suppliers,
        products=products
    )

@app.route("/delivery/add", methods=["GET", "POST"])
def add_delivery():

    agents = db.session.execute(
        db.text("SELECT * FROM agents")
    ).mappings()

    products = Product.query.all()

    if request.method == "POST":

        product_id = int(request.form["product_id"])
        qty = int(request.form["qty"])

        product = Product.query.get(product_id)

        if product.stok < qty:

            return "Stok tidak mencukupi"

        product.stok -= qty

        history = TransactionHistory(
           jenis="KELUAR",
           product_id=product.id,
           qty=qty,
           keterangan="Pengiriman Agen",
           user_id=session["user_id"]
        )

        db.session.add(history)

        db.session.commit()

        return redirect("/products")

    return render_template(
       "delivery_add.html",
       agents=agents,
       products=products
    )

@app.route("/history")
def history():

    data = db.session.execute(

        db.text("""

        SELECT
            h.id,
            h.tanggal,
            h.jenis,
            p.nama_barang,
            h.qty,
            h.keterangan

        FROM transaction_history h

        LEFT JOIN products p
        ON h.product_id = p.id

        ORDER BY h.id DESC

        """)

    ).mappings()

    return render_template(
        "history.html",
        history=data
    )

@app.route("/audit-log")
def audit_log():

    logs = db.session.execute(
        db.text("""
            SELECT
                a.id,
                u.nama,
                a.aktivitas,
                a.created_at

            FROM audit_logs a

            LEFT JOIN users u
            ON u.id = a.user_id

            ORDER BY a.id DESC
        """)
    ).mappings().all()

    return render_template(
        "audit_log.html",
        logs=logs
    )

@app.route("/audit-log/excel")
def audit_log_excel():

    logs = db.session.execute(
        db.text("""
            SELECT
                a.created_at,
                u.nama,
                a.aktivitas

            FROM audit_logs a

            LEFT JOIN users u
            ON u.id = a.user_id

            ORDER BY a.id DESC
        """)
    ).mappings().all()

    rows = []

    for log in logs:

        rows.append({
            "Waktu": log["created_at"],
            "User": log["nama"],
            "Aktivitas": log["aktivitas"]
        })

    df = pd.DataFrame(rows)

    filename = "audit_log.xlsx"

    df.to_excel(
        filename,
        index=False
    )

    return send_file(
        filename,
        as_attachment=True,
        download_name=filename
    )

@app.route("/suppliers")
def suppliers():

    if not check_role(["admin"]):

        flash(
            "Akses ditolak",
            "danger"
        )

        return redirect("/")

    data_supplier = db.session.execute(
        db.text("""
            SELECT *
            FROM suppliers
            ORDER BY id DESC
        """)
    ).mappings()

    keyword = request.args.get("keyword","")

    if keyword:

       data_supplier = db.session.execute(
           db.text("""
               SELECT *
               FROM suppliers
               WHERE nama_supplier
               LIKE :keyword
            """),
            {
               "keyword": f"%{keyword}%"
            }
        ).mappings()

    else:

        data_supplier = db.session.execute(
            db.text("""
                SELECT *
                FROM suppliers
                ORDER BY id DESC
            """)
        ).mappings()

    return render_template(
        "suppliers.html",
        suppliers=data_supplier,
        keyword=keyword
    )
        
@app.route("/supplier/add", methods=["GET","POST"])
def add_supplier():

    if not check_role(["admin"]):

        flash(
            "Akses ditolak",
            "danger"
        )

        return redirect("/")

    if request.method == "POST":

        nama_supplier = request.form["nama_supplier"]
        telepon = request.form["telepon"]
        email = request.form["email"]
        alamat = request.form["alamat"]

        db.session.execute(
            db.text("""
                INSERT INTO suppliers
                (
                    nama_supplier,
                    telepon,
                    email
                )
                VALUES
                (
                    :nama_supplier,
                    :telepon,
                    :email
                )
            """),
            {
                "nama_supplier": nama_supplier,
                "telepon": telepon,
                "email": email
            }
        )

        db.session.commit()

        save_log(
            session["user_id"],
            f"Menambah Supplier {nama_supplier}"
        )

        db.session.commit()

        return redirect("/suppliers")

    return render_template("supplier_add.html")

@app.route("/supplier/edit/<int:id>", methods=["GET", "POST"])
def edit_supplier(id):

    if not check_role(["admin"]):

        flash(
            "Akses ditolak",
            "danger"
        )

        return redirect("/")

    supplier = db.session.execute(
        db.text("SELECT * FROM suppliers WHERE id=:id"),
        {"id": id}
    ).mappings().first()

    if request.method == "POST":

        nama_supplier = request.form["nama_supplier"]
        telepon = request.form["telepon"]
        email = request.form["email"]
        alamat = request.form["alamat"]

        db.session.execute(
            db.text("""
                UPDATE suppliers
                SET
                    nama_supplier=:nama_supplier,
                    telepon=:telepon,
                    email=:email
                WHERE id=:id
            """),
            {
                "id": id,
                "nama_supplier": nama_supplier,
                "telepon": telepon,
                "email": email
            }
        )

        db.session.commit()

        save_log(
            session["user_id"],
            f"Edit Supplier {nama_supplier}"
        )

        db.session.commit()

        return redirect("/suppliers")

    return render_template(
        "supplier_edit.html",
        supplier=supplier
    )

@app.route("/supplier/delete/<int:id>")
def delete_supplier(id):

    if not check_role(["admin"]):

        flash(
            "Akses ditolak",
            "danger"
        )

        return redirect("/")
    
    supplier = db.session.execute(
        db.text("""
            SELECT *
            FROM suppliers
            WHERE id=:id
        """),
        {"id": id}
    ).mappings().first()

    db.session.execute(
        db.text(
            "DELETE FROM suppliers WHERE id=:id"
        ),
        {"id": id}
    )

    db.session.commit()

    save_log(
        session["user_id"],
        f"Hapus Supplier {supplier['nama_supplier']}"
    )

    db.session.commit()

    return redirect("/suppliers")

@app.route("/agents")
def agents():

    data_agen = db.session.execute(
        db.text("SELECT * FROM agents ORDER BY nama_agen")
    ).mappings()

    return render_template(
        "agents.html",
        agents=data_agen
    )

@app.route("/agent/add", methods=["GET","POST"])
def add_agent():

    if request.method == "POST":

        kode_agen = request.form["kode_agen"]
        nama_agen = request.form["nama_agen"]
        telepon = request.form["telepon"]

        db.session.execute(
            db.text("""
                INSERT INTO agents
                (kode_agen,nama_agen,telepon)
                VALUES
                (:kode,:nama,:telp)
            """),
            {
                "kode": kode_agen,
                "nama": nama_agen,
                "telp": telepon
            }
        )

        db.session.commit()

        return redirect("/agents")

    return render_template("agent_add.html")

@app.route(
    "/agents/edit/<int:id>",
    methods=["GET","POST"]
)
def edit_agent(id):

    agent = db.session.execute(
        db.text("""
            SELECT *
            FROM agents
            WHERE id=:id
        """),
        {"id": id}
    ).mappings().first()

    if request.method == "POST":

        db.session.execute(
            db.text("""
                UPDATE agents
                SET
                    kode_agen=:kode_agen,
                    nama_agen=:nama_agen,
                    alamat=:alamat,
                    telepon=:telepon
                WHERE id=:id
            """),
            {
                "id": id,
                "kode_agen": request.form["kode_agen"],
                "nama_agen": request.form["nama_agen"],
                "alamat": request.form["alamat"],
                "telepon": request.form["telepon"]
            }
        )

        db.session.commit()

        save_log(
            session["user_id"],
            f"Edit Agen {request.form['nama_agen']}"
        )

        db.session.commit()

        flash(
            "Agen berhasil diupdate",
            "success"
        )

        return redirect("/agents")

    return render_template(
        "agents_edit.html",
        agent=agent
    )

@app.route("/agents/delete/<int:id>")
def delete_agent(id):

    agent = db.session.execute(
        db.text("""
            SELECT *
            FROM agents
            WHERE id=:id
        """),
        {"id": id}
    ).mappings().first()

    if not agent:

        flash(
            "Agen tidak ditemukan",
            "danger"
        )

        return redirect("/agents")
    
    used = db.session.execute(
        db.text("""
            SELECT COUNT(*)
            FROM delivery_orders
            WHERE agent_id=:id
        """),
        {"id": id}
    ).scalar()

    if used > 0:

        flash(
            "Agen sudah digunakan dalam Delivery Order",
            "danger"
        )

        return redirect("/agents")

    db.session.execute(
        db.text("""
            DELETE FROM agents
            WHERE id=:id
        """),
        {"id": id}
    )

    db.session.commit()

    save_log(
        session["user_id"],
        f"Hapus Agen {agent['nama_agen']}"
    )

    db.session.commit()

    flash(
        "Agen berhasil dihapus",
        "success"
    )

    return redirect("/agents")

@app.route("/report/stock")
def report_stock():

    products = Product.query.order_by(
        Product.nama_barang
    ).all()

    return render_template(
        "report_stock.html",
        products=products
    )

@app.route("/report/stock/excel")
def report_stock_excel():

    products = Product.query.all()

    data = []

    for p in products:

        data.append({
            "SKU": p.sku,
            "Nama Barang": p.nama_barang,
            "Kategori": p.kategori,
            "Stok": p.stok,
            "Stok Minimum": p.stok_minimum,
            "Lokasi Rak": p.lokasi_rak,
            "Harga Beli": float(p.harga_beli or 0),
            "Harga Jual": float(p.harga_jual or 0),
            "Nilai Persediaan":
            float(p.stok or 0)
            *
            float(p.harga_beli or 0)
        })

    df = pd.DataFrame(data)

    filename = "laporan_stok.xlsx"

    df.to_excel(
        filename,
        index=False
    )

    save_log(
        session["user_id"],
        "Export Laporan Stok"
    )

    return send_file(
        filename,
        as_attachment=True,
        download_name="laporan_stok.xlsx"
    )

@app.route("/report/in")
def report_in():

    data = db.session.execute(
        db.text("""
            SELECT
                h.tanggal,
                p.nama_barang,
                h.qty,
                h.keterangan,
                u.nama AS nama_user

            FROM transaction_history h

            LEFT JOIN products p
            ON p.id = h.product_id
            
            LEFT JOIN users u
            ON u.id = h.user_id

            WHERE h.jenis='MASUK'

            ORDER BY h.tanggal DESC
        """)
    ).mappings()

    return render_template(
        "report_in.html",
        data=data
    )

@app.route("/report/in/excel")
def report_in_excel():

    data = db.session.execute(
        db.text("""
            SELECT
                h.tanggal,
                p.sku,
                p.nama_barang,
                h.qty,
                h.keterangan,
                u.nama AS nama_user

            FROM transaction_history h

            LEFT JOIN products p
            ON p.id = h.product_id
                
            LEFT JOIN users u
            ON u.id = h.user_id

            WHERE h.jenis='MASUK'

            ORDER BY h.tanggal DESC
        """)
    ).mappings().all()

    rows = []

    for d in data:

        rows.append({
            "Tanggal": d["tanggal"],
            "SKU": d["sku"],
            "Nama Barang": d["nama_barang"],
            "Qty": d["qty"],
            "Keterangan": d["keterangan"],
            "User": d["nama_user"]
        })

    df = pd.DataFrame(rows)

    filename = "laporan_barang_masuk.xlsx"

    df.to_excel(
        filename,
        index=False
    )

    save_log(
        session["user_id"],
        "Export Laporan Barang Masuk"
    )

    return send_file(
        filename,
        as_attachment=True,
        download_name=filename
    )

@app.route("/report/out")
def report_out():

    data = db.session.execute(
        db.text("""
            SELECT
                h.tanggal,
                p.nama_barang,
                h.qty,
                h.keterangan,
                u.nama AS nama_user

            FROM transaction_history h

            LEFT JOIN products p
            ON p.id = h.product_id
                
            LEFT JOIN users u
            ON u.id = h.user_id

            WHERE h.jenis='KELUAR'

            ORDER BY h.tanggal DESC
        """)
    ).mappings()

    return render_template(
        "report_out.html",
        data=data
    )

@app.route("/report/out/excel")
def report_out_excel():

    data = db.session.execute(
        db.text("""
            SELECT
                h.tanggal,
                p.sku,
                p.nama_barang,
                h.qty,
                h.keterangan,
                u.nama AS nama_user

            FROM transaction_history h

            LEFT JOIN products p
            ON p.id = h.product_id
                
            LEFT JOIN users u
            ON u.id = h.user_id

            WHERE h.jenis='KELUAR'

            ORDER BY h.tanggal DESC
        """)
    ).mappings().all()

    rows = []

    for d in data:

        rows.append({
            "Tanggal": d["tanggal"],
            "SKU": d["sku"],
            "Nama Barang": d["nama_barang"],
            "Qty": d["qty"],
            "Keterangan": d["keterangan"],
            "User": d["nama_user"]
        })

    df = pd.DataFrame(rows)

    filename = "laporan_barang_keluar.xlsx"

    df.to_excel(
        filename,
        index=False
    )

    save_log(
        session["user_id"],
        "Export Laporan Barang Keluar"
    )

    return send_file(
        filename,
        as_attachment=True,
        download_name=filename
    )

@app.route("/po")
def po_list():

    data = db.session.execute(
        db.text("""
            SELECT
                p.id,
                p.nomor_po,
                p.tanggal,
                s.nama_supplier,
                p.status

            FROM purchase_orders p

            LEFT JOIN suppliers s
            ON s.id = p.supplier_id

            ORDER BY p.id DESC
        """)
    ).mappings()

    return render_template(
        "po_list.html",
        data=data
    )

@app.route("/po/add", methods=["GET","POST"])
def po_add():

    suppliers = db.session.execute(
        db.text("SELECT * FROM suppliers")
    ).mappings()

    if request.method == "POST":

        supplier_id = request.form["supplier_id"]

        today = datetime.now().strftime("%Y%m%d")

        last_po = db.session.execute(
            db.text("""
                SELECT nomor_po
                FROM purchase_orders
                WHERE nomor_po LIKE :prefix
                ORDER BY id DESC
                LIMIT 1
            """),
            {"prefix": f"PO-{today}%"}
        ).mappings().first()

        if last_po:

           urut = int(
               last_po["nomor_po"].split("-")[-1]
           ) + 1

        else:

           urut = 1

        nomor_po = f"PO-{today}-{urut:03d}"

        db.session.execute(
            db.text("""
                INSERT INTO purchase_orders
                (
                    nomor_po,
                    tanggal,
                    supplier_id,
                    status,
                    user_id
                )
                VALUES
                (
                    :nomor_po,
                    CURDATE(),
                    :supplier_id,
                    'draft',
                    :user_id
                )
            """),
            {
                "nomor_po": nomor_po,
                "supplier_id": supplier_id,
                "user_id": session["user_id"]
            }
        )

        db.session.commit()

        save_log(
            session["user_id"],
            f"Membuat PO {nomor_po}"
        )

        db.session.commit()

        flash(
            "PO berhasil dibuat",
            "success"
        )

        return redirect("/po")

    return render_template(
        "po_add.html",
        suppliers=suppliers
    )

@app.route("/po/detail/<int:po_id>")
def po_detail(po_id):

    po = db.session.execute(
        db.text("""
            SELECT
                po.*,
                s.nama_supplier

            FROM purchase_orders po

            LEFT JOIN suppliers s
            ON s.id = po.supplier_id

            WHERE po.id=:id
        """),
        {"id": po_id}
    ).mappings().first()

    details = db.session.execute(
        db.text("""
            SELECT
                d.id,
                p.nama_barang,
                d.qty,
                d.harga,
                d.subtotal

            FROM purchase_order_details d

            LEFT JOIN products p
            ON p.id = d.product_id

            WHERE d.purchase_order_id=:id
        """),
        {"id": po_id}
    ).mappings()

    total = db.session.execute(
        db.text("""
            SELECT SUM(subtotal) total
            FROM purchase_order_details
            WHERE purchase_order_id=:id
        """),
        {"id": po_id}
    ).mappings().first()

    return render_template(
        "po_detail.html",
        po=po,
        details=details,
        total=total
    )

@app.route("/po/detail/add/<int:po_id>",
methods=["GET","POST"])
def po_detail_add(po_id):

    products = Product.query.all()

    if request.method == "POST":

        product_id = request.form["product_id"]
        qty = int(request.form["qty"])

        product = Product.query.get(product_id)

        harga = float(product.harga_beli)
        subtotal = harga * qty

        db.session.execute(
            db.text("""
                INSERT INTO purchase_order_details
                (
                    purchase_order_id,
                    product_id,
                    qty,
                    harga,
                    subtotal
                )
                VALUES
                (
                    :purchase_order_id,
                    :product_id,
                    :qty,
                    :harga,
                    :subtotal
                )
            """),
            {
                "purchase_order_id": po_id,
                "product_id": product_id,
                "qty": qty,
                "harga": harga,
                "subtotal": subtotal
            }
        )

        db.session.commit()

        return redirect(
            f"/po/detail/{po_id}"
        )

    return render_template(
        "po_detail_add.html",
        products=products
    )

@app.route(
    "/po/detail/edit/<int:id>",
    methods=["GET","POST"]
)
def po_detail_edit(id):

    detail = db.session.execute(
        db.text("""
            SELECT *
            FROM purchase_order_details
            WHERE id=:id
        """),
        {"id": id}
    ).mappings().first()

    if not detail:

        flash(
            "Data tidak ditemukan",
            "danger"
        )

        return redirect("/po")

    po = db.session.execute(
        db.text("""
            SELECT status
            FROM purchase_orders
            WHERE id=:id
        """),
        {
            "id":
            detail["purchase_order_id"]
        }
    ).mappings().first()

    if po["status"] not in ["draft","open"]:

        flash(
            "PO tidak dapat diedit",
            "danger"
        )

        return redirect(
            f"/po/detail/{detail['purchase_order_id']}"
        )

    if request.method == "POST":

        qty = int(
            request.form["qty"]
        )

        harga = float(
            request.form["harga"]
        )

        subtotal = qty * harga

        db.session.execute(
            db.text("""
                UPDATE purchase_order_details
                SET
                    qty=:qty,
                    harga=:harga,
                    subtotal=:subtotal
                WHERE id=:id
            """),
            {
                "id": id,
                "qty": qty,
                "harga": harga,
                "subtotal": subtotal
            }
        )

        db.session.commit()

        flash(
            "Barang berhasil diupdate",
            "success"
        )

        return redirect(
            f"/po/detail/{detail['purchase_order_id']}"
        )

    return render_template(
        "po_detail_edit.html",
        detail=detail
    )

@app.route("/po/detail/delete/<int:id>")
def po_detail_delete(id):

    detail = db.session.execute(
        db.text("""
            SELECT *
            FROM purchase_order_details
            WHERE id=:id
        """),
        {"id": id}
    ).mappings().first()

    if not detail:

        flash(
            "Data tidak ditemukan",
            "danger"
        )

        return redirect("/po")

    po = db.session.execute(
        db.text("""
            SELECT status
            FROM purchase_orders
            WHERE id=:id
        """),
        {
            "id":
            detail["purchase_order_id"]
        }
    ).mappings().first()

    if po["status"] not in ["draft","open"]:

        flash(
            "PO tidak dapat dihapus",
            "danger"
        )

        return redirect(
            f"/po/detail/{detail['purchase_order_id']}"
        )

    db.session.execute(
        db.text("""
            DELETE FROM purchase_order_details
            WHERE id=:id
        """),
        {"id": id}
    )

    db.session.commit()

    flash(
        "Barang berhasil dihapus",
        "success"
    )

    return redirect(
        f"/po/detail/{detail['purchase_order_id']}"
    )

@app.route("/po/submit/<int:po_id>")
def po_submit(po_id):

    db.session.execute(
        db.text("""
            UPDATE purchase_orders
            SET status='open'
            WHERE id=:id
        """),
        {"id": po_id}
    )

    db.session.commit()

    save_log(
        session["user_id"],
        f"Submit PO ID {po_id}"
    )

    db.session.commit()

    flash(
        "PO berhasil disubmit",
        "success"
    )

    return redirect(
        f"/po/detail/{po_id}"
    )

@app.route("/po/approve/<int:po_id>")
def po_approve(po_id):

    if not check_role(
        ["admin","owner"]
    ):

        flash(
            "Akses ditolak",
            "danger"
        )

        return redirect("/")

    po = db.session.execute(
        db.text("""
            SELECT *
            FROM purchase_orders
            WHERE id=:id
        """),
        {"id": po_id}
    ).mappings().first()

    if po["status"].lower() != "open":

        flash(
            "PO harus berstatus OPEN",
            "danger"
        )

        return redirect(
            f"/po/detail/{po_id}"
        )

    db.session.execute(
        db.text("""
            UPDATE purchase_orders
            SET status='approved'
            WHERE id=:id
        """),
        {"id": po_id}
    )

    db.session.commit()

    save_log(
        session["user_id"],
        f"Approve PO ID {po_id}"
    )

    db.session.commit()

    flash(
        "PO berhasil diapprove",
        "success"
    )

    return redirect(
        f"/po/detail/{po_id}"
    )

@app.route("/po/unapprove/<int:po_id>")
def po_unapprove(po_id):

    if not check_role(["admin","owner"]):

        flash(
            "Akses ditolak",
            "danger"
        )

        return redirect("/")

    po = db.session.execute(
        db.text("""
            SELECT status
            FROM purchase_orders
            WHERE id=:id
        """),
        {"id": po_id}
    ).mappings().first()

    if po["status"] != "approved":

        flash(
            "PO tidak dapat dibatalkan",
            "danger"
        )

        return redirect(
            f"/po/detail/{po_id}"
        )

    db.session.execute(
        db.text("""
            UPDATE purchase_orders
            SET status='open'
            WHERE id=:id
        """),
        {"id": po_id}
    )

    db.session.commit()

    flash(
        "Approval PO dibatalkan",
        "warning"
    )

    return redirect(
        f"/po/detail/{po_id}"
    )

@app.route("/po/receive/<int:po_id>")
def po_receive(po_id):

    if not check_role(
        ["admin","gudang"]
    ):

        flash(
            "Akses ditolak",
            "danger"
        )

        return redirect("/")

    if "user_id" not in session:
        return redirect("/login")

    po = db.session.execute(
        db.text("""
            SELECT *
            FROM purchase_orders
            WHERE id=:id
        """),
        {"id": po_id}
    ).mappings().first()

    if po["status"].lower() != "approved":

        flash(
            "PO harus diapprove terlebih dahulu",
            "danger"
        )

        return redirect(
            f"/po/detail/{po_id}"
        )

    details = db.session.execute(
        db.text("""
            SELECT
                product_id,
                qty
            FROM purchase_order_details
            WHERE purchase_order_id=:id
        """),
        {"id": po_id}
    ).mappings()

    for d in details:

        product = Product.query.get(
            d["product_id"]
        )

        product.stok += d["qty"]

        history = TransactionHistory(
            jenis="MASUK",
            product_id=product.id,
            qty=d["qty"],
            keterangan="Receive PO",
            user_id=session["user_id"]
        )

        db.session.add(history)

    db.session.execute(
        db.text("""
            UPDATE purchase_orders
            SET status='received'
            WHERE id=:id
        """),
        {"id": po_id}
    )

    db.session.commit()

    save_log(
        session["user_id"],
        f"Receive PO ID {po_id}"
    )

    db.session.commit()

    flash(
        "PO berhasil diterima",
        "success"
    )

    return redirect("/products")

@app.route("/po/print/<int:po_id>")
def po_print(po_id):

    po = db.session.execute(
        db.text("""
            SELECT
                p.*,
                s.nama_supplier

            FROM purchase_orders p

            LEFT JOIN suppliers s
            ON s.id = p.supplier_id

            WHERE p.id=:id
        """),
        {"id": po_id}
    ).mappings().first()

    details = db.session.execute(
        db.text("""
            SELECT
                pr.nama_barang,
                d.qty,
                d.harga,
                d.subtotal

            FROM purchase_order_details d

            LEFT JOIN products pr
            ON pr.id = d.product_id

            WHERE d.purchase_order_id=:id
        """),
        {"id": po_id}
    ).mappings()

    total = db.session.execute(
        db.text("""
            SELECT SUM(subtotal) total
            FROM purchase_order_details
            WHERE purchase_order_id=:id
        """),
        {"id": po_id}
    ).mappings().first()

    return render_template(
        "po_print.html",
        po=po,
        details=details,
        total=total
    )

@app.route("/stock-card/<int:product_id>")
def stock_card(product_id):

    product = Product.query.get_or_404(
        product_id
    )

    history = db.session.execute(
        db.text("""
            SELECT
                tanggal,
                jenis,
                qty,
                keterangan

            FROM transaction_history

            WHERE product_id=:id

            ORDER BY tanggal ASC
        """),
        {"id": product_id}
    ).mappings()

    return render_template(
        "stock_card.html",
        product=product,
        history=history
    )

@app.route("/do")
def do_list():

    data = db.session.execute(
        db.text("""
            SELECT
                d.*,
                a.nama_agen

            FROM delivery_orders d

            LEFT JOIN agents a
            ON a.id = d.agent_id

            ORDER BY d.id DESC
        """)
    ).mappings()

    return render_template(
        "do_list.html",
        data=data
    )

@app.route("/do/add", methods=["GET","POST"])
def do_add():

    agents = db.session.execute(
        db.text("SELECT * FROM agents")
    ).mappings()

    if request.method == "POST":

        agent_id = request.form["agent_id"]

        today = datetime.now().strftime("%Y%m%d")

        last_do = db.session.execute(
            db.text("""
                SELECT nomor_do
                FROM delivery_orders
                WHERE nomor_do LIKE :prefix
                ORDER BY id DESC
                LIMIT 1
            """),
            {"prefix": f"DO-{today}%"}
        ).mappings().first()

        if last_do:

            urut = int(
                last_do["nomor_do"].split("-")[-1]
            ) + 1

        else:

            urut = 1

        nomor_do = f"DO-{today}-{urut:03d}"

        db.session.execute(
            db.text("""
                INSERT INTO delivery_orders
                (
                    nomor_do,
                    tanggal,
                    agent_id,
                    status,
                    user_id
                )
                VALUES
                (
                    :nomor_do,
                    CURDATE(),
                    :agent_id,
                    'draft',
                    :user_id
                )
            """),
            {
                "nomor_do": nomor_do,
                "agent_id": agent_id,
                "user_id": session["user_id"]
            }
        )

        db.session.commit()

        save_log(
            session["user_id"],
            f"Membuat DO {nomor_do}"
        )

        db.session.commit()

        flash(
            "DO berhasil dibuat",
            "success"
        )

        return redirect("/do")

    return render_template(
        "do_add.html",
        agents=agents
    )

@app.route("/do/detail/<int:do_id>")
def do_detail(do_id):

    do = db.session.execute(
        db.text("""
            SELECT
                d.*,
                a.nama_agen

            FROM delivery_orders d

            LEFT JOIN agents a
            ON a.id = d.agent_id

            WHERE d.id=:id
        """),
        {"id": do_id}
    ).mappings().first()

    details = db.session.execute(
        db.text("""
            SELECT
                dd.id,
                p.nama_barang,
                dd.qty,
                dd.harga_jual,
                dd.subtotal

            FROM delivery_order_details dd

            LEFT JOIN products p
            ON p.id = dd.product_id

            WHERE dd.delivery_order_id=:id
        """),
        {"id": do_id}
    ).mappings()

    total = db.session.execute(
        db.text("""
            SELECT
                SUM(subtotal) total
            FROM delivery_order_details
            WHERE delivery_order_id=:id
        """),
        {"id": do_id}
    ).mappings().first()

    total_item = db.session.execute(
        db.text("""
            SELECT COUNT(*)
            FROM delivery_order_details
            WHERE delivery_order_id=:id
        """),
        {"id": do_id}
    ).scalar()

    total_qty = db.session.execute(
        db.text("""
            SELECT
                COALESCE(
                    SUM(qty),
                    0
                )
            FROM delivery_order_details
            WHERE delivery_order_id=:id
        """),
        {"id": do_id}
    ).scalar()

    profit = db.session.execute(
        db.text("""
            SELECT
                COALESCE(
                    SUM(
                        dd.qty *
                        (
                            dd.harga_jual -
                            p.harga_beli
                        )
                    ),
                    0
                ) profit
            FROM delivery_order_details dd

            LEFT JOIN products p
            ON p.id = dd.product_id

            WHERE dd.delivery_order_id=:id
        """),
        {"id": do_id}
    ).mappings().first()

    return render_template(
        "do_detail.html",
        do=do,
        details=details,
        total=total,
        total_item=total_item,
        total_qty=total_qty,
        profit=profit
    )

@app.route("/do/detail/add/<int:do_id>",
methods=["GET","POST"])
def do_detail_add(do_id):

    products = Product.query.all()

    if request.method == "POST":

        product_id = int(
            request.form["product_id"]
        )

        qty = int(
            request.form["qty"]
        )

        product = Product.query.get(
            product_id
        )

        harga_jual = float(
            product.harga_jual
        )

        subtotal = harga_jual * qty

        db.session.execute(
            db.text("""
                INSERT INTO delivery_order_details
                (
                    delivery_order_id,
                    product_id,
                    qty,
                    harga_jual,
                    subtotal
                )
                VALUES
                (
                    :delivery_order_id,
                    :product_id,
                    :qty,
                    :harga_jual,
                    :subtotal
                )
            """),
            {
                "delivery_order_id": do_id,
                "product_id": product_id,
                "qty": qty,
                "harga_jual": harga_jual,
                "subtotal": subtotal
            }
        )

        db.session.commit()

        flash(
            "Barang berhasil ditambahkan",
            "success"
        )

        return redirect(
            f"/do/detail/{do_id}"
        )

    return render_template(
        "do_detail_add.html",
        products=products
    )

@app.route(
    "/do/detail/edit/<int:id>",
    methods=["GET","POST"]
)
def do_detail_edit(id):

    detail = db.session.execute(
        db.text("""
            SELECT *
            FROM delivery_order_details
            WHERE id=:id
        """),
        {"id": id}
    ).mappings().first()

    do_data = db.session.execute(
        db.text("""
            SELECT status
            FROM delivery_orders
            WHERE id=:id
        """),
        {
            "id":
            detail["delivery_order_id"]
        }
    ).mappings().first()

    if do_data["status"] != "draft":

        flash(
            "DO yang sudah diapprove tidak dapat diedit",
            "danger"
        )

        return redirect(
            f"/do/detail/{detail['delivery_order_id']}"
        )

    if request.method == "POST":

        qty = int(
            request.form["qty"]
        )

        harga_jual = float(
            request.form["harga_jual"]
        )

        subtotal = qty * harga_jual

        db.session.execute(
            db.text("""
                UPDATE delivery_order_details
                SET
                    qty=:qty,
                    harga_jual=:harga_jual,
                    subtotal=:subtotal
                WHERE id=:id
            """),
            {
                "id": id,
                "qty": qty,
                "harga_jual": harga_jual,
                "subtotal": subtotal
            }
        )

        db.session.commit()

        flash(
            "Barang berhasil diupdate",
            "success"
        )

        return redirect(
            f"/do/detail/{detail['delivery_order_id']}"
        )

    return render_template(
        "do_detail_edit.html",
        detail=detail
    )

@app.route("/do/detail/delete/<int:id>")
def do_detail_delete(id):

    detail = db.session.execute(
        db.text("""
            SELECT *
            FROM delivery_order_details
            WHERE id=:id
        """),
        {"id": id}
    ).mappings().first()

    if do_data["status"] != "draft":

        flash(
            "DO yang sudah diapprove tidak dapat diedit",
            "danger"
        )

        return redirect(
            f"/do/detail/{detail['delivery_order_id']}"
        )

    db.session.execute(
        db.text("""
            DELETE FROM delivery_order_details
            WHERE id=:id
        """),
        {"id": id}
    )

    db.session.commit()

    flash(
        "Barang berhasil dihapus",
        "success"
    )

    return redirect(
        f"/do/detail/{detail['delivery_order_id']}"
    )

@app.route("/do/submit/<int:do_id>")
def do_submit(do_id):

    if not check_role(
        ["admin","gudang","kasir"]
    ):
        flash("Akses ditolak", "danger")
        return redirect("/")

    db.session.execute(
        db.text("""
            UPDATE delivery_orders
            SET status='open'
            WHERE id=:id
        """),
        {"id": do_id}
    )

    db.session.commit()

    save_log(
        session["user_id"],
        f"Submit DO ID {do_id}"
    )

    db.session.commit()

    flash(
        "DO berhasil disubmit",
        "success"
    )

    return redirect(
        f"/do/detail/{do_id}"
    )

@app.route("/do/approve/<int:do_id>")
def do_approve(do_id):

    if not check_role(
        ["admin","owner"]
    ):

        flash(
            "Akses ditolak",
            "danger"
        )

        return redirect("/")

    db.session.execute(
        db.text("""
            UPDATE delivery_orders
            SET status= 'approved'
            WHERE id=:id
        """),
        {"id": do_id}
    )

    db.session.commit()

    save_log(
        session["user_id"],
        f"Approve DO ID {do_id}"
    )

    db.session.commit()

    flash(
        "DO berhasil diapprove",
        "success"
    )

    return redirect(
        f"/do/detail/{do_id}"
    )

@app.route("/do/unapprove/<int:do_id>")
def do_unapprove(do_id):

    if not check_role(["admin","owner"]):

        flash(
            "Akses ditolak",
            "danger"
        )

        return redirect("/")

    do_data = db.session.execute(
        db.text("""
            SELECT status
            FROM delivery_orders
            WHERE id=:id
        """),
        {"id": do_id}
    ).mappings().first()

    if do_data["status"].lower() == "sent":

        flash(
            "DO yang sudah dikirim tidak bisa dibatalkan",
            "danger"
        )

        return redirect(
            f"/do/detail/{do_id}"
        )

    db.session.execute(
        db.text("""
            UPDATE delivery_orders
            SET status='draft'
            WHERE id=:id
        """),
        {"id": do_id}
    )

    db.session.commit()

    save_log(
        session["user_id"],
        f"Batalkan approval DO ID {do_id}"
    )

    flash(
        "Status DO dikembalikan ke Draft",
        "warning"
    )

    return redirect(
        f"/do/detail/{do_id}"
    )

@app.route("/do/send/<int:do_id>")
def do_send(do_id):

    if not check_role(
        ["admin","gudang"]
    ):
        flash(
            "Akses ditolak",
            "danger"
        )
        return redirect("/")

    do_data = db.session.execute(
        db.text("""
            SELECT *
            FROM delivery_orders
            WHERE id=:id
        """),
        {"id": do_id}
    ).mappings().first()

    if do_data["status"].lower() != "approved":

        flash(
            "DO harus diapprove terlebih dahulu",
            "danger"
        )

        return redirect(
            f"/do/detail/{do_id}"
        )

    details = db.session.execute(
        db.text("""
            SELECT
                product_id,
                qty
            FROM delivery_order_details
            WHERE delivery_order_id=:id
        """),
        {"id": do_id}
    ).mappings()

    for d in details:

        product = Product.query.get(
            d["product_id"]
        )

        if product.stok < d["qty"]:

            flash(
                f"Stok {product.nama_barang} tidak mencukupi",
                "danger"
            )

            return redirect(
                f"/do/detail/{do_id}"
            )

        product.stok -= d["qty"]

        history = TransactionHistory(
            jenis="KELUAR",
            product_id=product.id,
            qty=d["qty"],
            keterangan=f"DO #{do_id}",
            user_id=session["user_id"]
        )

        db.session.add(history)

    db.session.execute(
        db.text("""
            UPDATE delivery_orders
            SET status='sent'
            WHERE id=:id
        """),
        {"id": do_id}
    )

    db.session.commit()

    save_log(
        session["user_id"],
        f"Kirim DO ID {do_id}"
    )

    db.session.commit()

    flash(
        "Delivery Order berhasil dikirim",
        "success"
    )

    return redirect(
        f"/do/detail/{do_id}"
    )

@app.route("/do/print/<int:do_id>")
def do_print(do_id):

    do = db.session.execute(
        db.text("""
            SELECT
                d.*,
                a.nama_agen,
                a.alamat,
                a.telepon

            FROM delivery_orders d

            LEFT JOIN agents a
            ON a.id = d.agent_id

            WHERE d.id=:id
        """),
        {"id": do_id}
    ).mappings().first()

    details = db.session.execute(
        db.text("""
            SELECT
                p.nama_barang,
                dd.qty,
                dd.harga_jual,
                dd.subtotal

            FROM delivery_order_details dd

            LEFT JOIN products p
            ON p.id = dd.product_id

            WHERE dd.delivery_order_id=:id
        """),
        {"id": do_id}
    ).mappings()

    total_qty = db.session.execute(
        db.text("""
            SELECT
                COALESCE(SUM(qty),0) total_qty
            FROM delivery_order_details
            WHERE delivery_order_id=:id
        """),
        {"id": do_id}
    ).mappings().first()

    return render_template(
        "do_print.html",
        do=do,
        details=details,
        total_qty=total_qty
    )

@app.route("/stock-opname")
def stock_opname():

    data = db.session.execute(
        db.text("""
            SELECT
                s.*,
                p.nama_barang,
                u.nama AS petugas

            FROM stock_opname s

            LEFT JOIN products p
            ON p.id = s.product_id
                
            LEFT JOIN users u
            ON u.id = s.user_id

            ORDER BY s.id DESC
        """)
    ).mappings().all()

    return render_template(
        "stock_opname.html",
        data=data
    )

@app.route(
    "/stock-opname/add",
    methods=["GET","POST"]
)
def stock_opname_add():

    products = Product.query.all()

    if request.method == "POST":

        product_id = int(
            request.form["product_id"]
        )

        stok_fisik = int(
            request.form["stok_fisik"]
        )

        product = Product.query.get(
            product_id
        )

        stok_sistem = product.stok

        selisih = (
            stok_fisik -
            stok_sistem
        )

        keterangan = request.form.get(
            "keterangan",
            ""
        )

        db.session.execute(
            db.text("""
                INSERT INTO stock_opname
                (
                    product_id,
                    stok_sistem,
                    stok_fisik,
                    selisih,
                    user_id,
                    keterangan
                )
                VALUES
                (
                    :product_id,
                    :stok_sistem,
                    :stok_fisik,
                    :selisih,
                    :user_id,
                    :keterangan
                )
            """),
            {
                "product_id": product_id,
                "stok_sistem": stok_sistem,
                "stok_fisik": stok_fisik,
                "selisih": selisih,
                "user_id": session["user_id"],
                "keterangan": keterangan
            }
        )

        product.stok = stok_fisik

        history = TransactionHistory(
            jenis="OPNAME",
            product_id=product.id,
            qty=abs(selisih),
            keterangan=f"Stock Opname - {keterangan}",
            user_id=session["user_id"]
        )

        db.session.add(history)

        db.session.commit()

        flash(
            "Stock opname berhasil",
            "success"
        )

        return redirect(
            "/stock-opname"
        )

    return render_template(
        "stock_opname_add.html",
        products=products
    )

@app.route("/stock-opname/print/<int:id>")
def stock_opname_print(id):

    data = db.session.execute(
        db.text("""
            SELECT
                s.*,
                p.nama_barang,
                u.nama petugas

            FROM stock_opname s

            LEFT JOIN products p
            ON p.id = s.product_id

            LEFT JOIN users u
            ON u.id = s.user_id

            WHERE s.id=:id
        """),
        {"id": id}
    ).mappings().first()

    return render_template(
        "stock_opname_print.html",
        data=data
    )

@app.route("/reorder")
def reorder():

    data = db.session.execute(
        db.text("""

            SELECT

                p.id,
                p.sku,
                p.nama_barang,
                p.stok,
                p.stok_minimum,
                p.lead_time,

                COALESCE(
                    SUM(th.qty),
                    0
                ) AS penjualan_30_hari

            FROM products p

            LEFT JOIN transaction_history th
            ON th.product_id = p.id
            AND th.jenis='KELUAR'
            AND th.tanggal >=
                DATE_SUB(
                    CURDATE(),
                    INTERVAL 30 DAY
                )

            GROUP BY p.id

            ORDER BY p.nama_barang

        """)
    ).mappings().all()

    suggestions = []

    for p in data:

        avg_daily = (
            p["penjualan_30_hari"] / 30
        )

        kebutuhan = int(
            avg_daily * p["lead_time"]
        )

        suggested_qty = max(
            0,
            kebutuhan - p["stok"]
        )

        if suggested_qty > 0:

            suggestions.append({
                "id": p["id"],
                "sku": p["sku"],
                "nama_barang": p["nama_barang"],
                "stok": p["stok"],
                "lead_time": p["lead_time"],
                "penjualan_30_hari":
                    p["penjualan_30_hari"],
                "saran_beli":
                    suggested_qty
            })

    return render_template(
        "reorder.html",
        suggestions=suggestions
    )

@app.route("/reorder/create-po/<int:product_id>")
def reorder_create_po(product_id):

    product = Product.query.get(product_id)

    if not product:
        return "Produk tidak ditemukan"

    supplier = db.session.execute(
        db.text("""
            SELECT *
            FROM suppliers
            LIMIT 1
        """)
    ).mappings().first()

    if not supplier:
        return "Supplier belum ada"
    
    today = datetime.now().strftime("%Y%m%d")

    nomor_po = (
        f"PO-{today}-{random.randint(1000,9999)}"
    )

    db.session.execute(
        db.text("""
            INSERT INTO purchase_orders
            (
                nomor_po,
                tanggal,
                supplier_id,
                status,
                user_id
            )
            VALUES
            (
                :nomor_po,
                CURDATE(),
                :supplier_id,
                'draft',
                :user_id
            )
        """),
        {
            "nomor_po": nomor_po,
            "supplier_id": supplier["id"],
            "user_id": session["user_id"]
        }
    )

    db.session.commit()

    po = db.session.execute(
        db.text("""
            SELECT id
            FROM purchase_orders
            WHERE nomor_po=:nomor_po
        """),
        {
            "nomor_po": nomor_po
        }
    ).mappings().first()

    flash(
        f"PO {nomor_po} berhasil dibuat",
        "success"
    )

    return redirect(
        f"/po/detail/{po['id']}"
    )

@app.route("/api/product-by-barcode/<barcode>")
def product_by_barcode(barcode):

    product = Product.query.filter_by(
        barcode=barcode
    ).first()

    if not product:

        return {
            "success": False
        }

    return {
        "success": True,
        "id": product.id,
        "nama_barang": product.nama_barang,
        "stok": product.stok,
        "harga_jual": float(product.harga_jual or 0)
    }

@app.route("/owner")
def owner_dashboard():

    if not check_role(["owner","admin"]):

        flash(
            "Akses ditolak",
            "danger"
        )

        return redirect("/")

    inventory_value = db.session.execute(
        db.text("""
            SELECT
                COALESCE(
                    SUM(stok * harga_beli),
                    0
                )
            FROM products
        """)
    ).scalar()

    monthly_revenue = db.session.execute(
        db.text("""
            SELECT
                COALESCE(
                    SUM(qty * harga_jual),
                    0
                )
            FROM delivery_order_details
        """)
    ).scalar()

    gross_profit = db.session.execute(
        db.text("""
            SELECT
                COALESCE(
                    SUM(
                        qty *
                        (
                            harga_jual -
                            (
                                SELECT harga_beli
                                FROM products p
                                WHERE p.id =
                                delivery_order_details.product_id
                            )
                        )
                    ),
                    0
                )
            FROM delivery_order_details
        """)
    ).scalar()

    low_stock = db.session.execute(
        db.text("""
            SELECT *
            FROM products
            WHERE stok <= stok_minimum
            ORDER BY stok ASC
            LIMIT 10
        """)
    ).mappings().all()

    total_produk = Product.query.count()

    total_supplier = db.session.execute(
        db.text("SELECT COUNT(*) FROM suppliers")
    ).scalar()

    total_agen = db.session.execute(
        db.text("SELECT COUNT(*) FROM agents")
    ).scalar()

    total_user = User.query.count()

    sales_chart = db.session.execute(
        db.text("""
            SELECT
                DATE_FORMAT(
                    tanggal,
                    '%Y-%m'
                ) bulan,

                SUM(subtotal) omzet

            FROM delivery_order_details dd

            LEFT JOIN delivery_orders d
            ON d.id = dd.delivery_order_id

            GROUP BY bulan

            ORDER BY bulan
        """)
    ).mappings().all()

    top_products = db.session.execute(
        db.text("""
            SELECT
                p.nama_barang,
                COALESCE(SUM(h.qty),0) total_jual

            FROM transaction_history h

            LEFT JOIN products p
            ON p.id = h.product_id

            WHERE h.jenis='KELUAR'

            GROUP BY p.id

            ORDER BY total_jual DESC

            LIMIT 5
        """)
    ).mappings().all()

    top_agents = db.session.execute(
        db.text("""
            SELECT
                a.nama_agen,
                COALESCE(
                    SUM(dd.subtotal),
                    0
                ) omzet

            FROM delivery_orders d

            LEFT JOIN agents a
            ON a.id = d.agent_id

            LEFT JOIN delivery_order_details dd
            ON dd.delivery_order_id = d.id

            WHERE d.status='sent'

            GROUP BY a.id

            ORDER BY omzet DESC

            LIMIT 5
        """)
    ).mappings().all()

    pending_po = db.session.execute(
        db.text("""
            SELECT COUNT(*)
            FROM purchase_orders
            WHERE status='open'
        """)
    ).scalar()

    pending_do = db.session.execute(
        db.text("""
            SELECT COUNT(*)
            FROM delivery_orders
            WHERE status='draft'
        """)
    ).scalar()

    critical_stock = db.session.execute(
        db.text("""
            SELECT COUNT(*)
            FROM products
            WHERE stok <= stok_minimum
        """)
    ).scalar()

    approved_po = db.session.execute(
        db.text("""
            SELECT COUNT(*)
            FROM purchase_orders
            WHERE status='approved'
        """)
    ).scalar()

    return render_template(
        "owner_dashboard.html",
        inventory_value=inventory_value,
        monthly_revenue=monthly_revenue,
        gross_profit=gross_profit,
        low_stock=low_stock,
        top_products=top_products,
        top_agents=top_agents,
        pending_po=pending_po,
        pending_do=pending_do,
        critical_stock=critical_stock,
        approved_po=approved_po
    )

@app.route("/tes")
def tes():
    return "TES BERHASIL"

if __name__ == "__main__":
    app.run(debug=True)