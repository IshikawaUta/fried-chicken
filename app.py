from flask import Flask, render_template, request, redirect, url_for, session
import os
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Nomor WhatsApp tujuan (ganti dengan nomor Anda)
WHATSAPP_NUMBER = '62895701060973'

# Contoh data produk (idealnya dari database)
products = [
    {'id': 1, 'name': 'dada', 'price': 12000, 'image': 'static/images/p_dada.jpg'},
    {'id': 2, 'name': 'sayap', 'price': 10000, 'image': 'static/images/p_sayap.jpg'},
    {'id': 3, 'name': 'paha atas', 'price': 12000, 'image': 'static/images/p_paha_atas.jpg'},
    {'id': 3, 'name': 'paha bawah', 'price': 8000, 'image': 'static/images/p_paha_bawah.jpg'},
]

@app.before_request
def before_request():
    if 'cart' not in session:
        session['cart'] = {}
    print(f"Sesi di awal request: {session}") # Tambahkan ini

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def product_list():
    return render_template('product_list.html', products=products)

@app.route('/product/<int:id>')
def product_detail(id):
    product = next((p for p in products if p['id'] == id), None)
    if product:
        return render_template('product_detail.html', product=product)
    return render_template('404.html'), 404

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        product_id_str = str(product_id)  # Kunci selalu string
        if product_id_str in session['cart']:
            session['cart'][product_id_str]['quantity'] += quantity
        else:
            session['cart'][product_id_str] = {'name': product['name'], 'price': product['price'], 'quantity': quantity}
        session.modified = True
        print(f"Sesi di add_to_cart (sesudah): {session}")  # Debugging
        return redirect(url_for('cart'))
    print("Produk tidak ditemukan.")
    return render_template('404.html'), 404

@app.route('/cart')
def cart():
    print(f"Sesi di cart: {session}")  # Debugging
    cart_items = []
    total_price = 0
    for product_id_str, details in session['cart'].items():
        product_id = int(product_id_str)
        product = next((p for p in products if p['id'] == product_id), None)
        if product:
            total_price += details['price'] * details['quantity']
            cart_items.append({'id': product_id, 'name': details['name'], 'price': details['price'], 'quantity': details['quantity']})
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    product_id_str = str(product_id)  # Kunci selalu string
    if product_id_str in session['cart']:
        session['cart'][product_id_str]['quantity'] = quantity
        if quantity <= 0:
            del session['cart'][product_id_str]
        session.modified = True
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    product_id_str = str(product_id)  # Kunci selalu string
    if product_id_str in session['cart']:
        del session['cart'][product_id_str]
        session.modified = True
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    if session['cart']:
        order_details = []
        total = 0
        for item_id_str, details in session['cart'].items():
            product_id = int(item_id_str)
            product = next((p for p in products if p['id'] == product_id), None)
            if product:
                order_details.append({'name': product['name'], 'quantity': details['quantity'], 'price': details['price']})
                total += details['price'] * details['quantity']

        whatsapp_message = "Pesanan Baru:\n"
        for item in order_details:
            whatsapp_message += f"- {item['name']} (Jumlah: {item['quantity']}, Harga: Rp {item['price']})\n"
        whatsapp_message += f"Total Harga: Rp {total}\nTerima kasih atas pesanan Anda!"
        whatsapp_link = f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(whatsapp_message)}"

        session['cart'] = {}
        return render_template('checkout.html', message='Pesanan Anda telah berhasil diproses! Silakan kirim konfirmasi melalui WhatsApp.', whatsapp_link=whatsapp_link)
    else:
        return redirect(url_for('cart'))

if __name__ == '__main__':
    app.run(debug=True)