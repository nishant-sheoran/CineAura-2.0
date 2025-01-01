from flask import Flask, render_template, request, url_for, flash, redirect, session, jsonify
import sqlite3
import random

app = Flask(__name__)
app.secret_key = 'this_is_my_secret_key'

# Database setup
def init_db():
    with sqlite3.connect('booking.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            theater TEXT,
                            movie TEXT,
                            screen TEXT,
                            food_items TEXT,
                            total_price REAL
                          )''')
        conn.commit()

init_db()

# Basic route
@app.route("/", methods=["GET"])
def home():
    return render_template('index.html')

# Booking tickets
@app.route("/book_tickets", methods=['GET', 'POST'])
def book_tickets():
    if request.method == "POST":
        theater = request.form.get("theater")
        movie = request.form.get("movie")
        screen = request.form.get("screen")

        session['theater'] = theater
        session['movie'] = movie
        session['screen'] = screen

        return redirect(url_for("select_beverages"))

    return render_template("bookTickets.html")

# Select beverages
@app.route("/select_beverages", methods=['GET', 'POST'])
def select_beverages():
    if request.method == 'POST':
        food_items = request.form.getlist('foodandbeverages')
        session['food_items'] = ','.join(food_items)  # Store as comma-separated string
        return redirect(url_for("confirm_booking"))

    return render_template("selectBeverages.html")

# Confirm booking
@app.route("/confirm_booking", methods=['GET', 'POST'])
def confirm_booking():
    theater = session.get('theater', 'Not Selected')
    movie = session.get('movie', 'Not Selected')
    screen = session.get('screen', 'Not Selected')
    food_items = session.get('food_items', '').split(',')

    if request.method == 'POST':
        return redirect(url_for("payment"))

    return render_template('confirmBooking.html',
                           theater=theater,
                           movie=movie,
                           screen=screen,
                           food_items=food_items)

# Payment
@app.route("/payment", methods=['GET', 'POST'])
def payment():
    screen = session.get('screen', 'Not Selected')
    food_items = session.get('food_items', '').split(',')

    total_amount = 0
    discount = 0
    final_price = 0

    if screen == 'gold':
        if 'Popcorn' in food_items:
            total_amount += 250
        if 'Sandwich' in food_items:
            total_amount += 100
        discount = 0.1 * total_amount
        total_amount -= discount
        final_price = total_amount + 400

    elif screen == 'max':
        if 'Popcorn' in food_items:
            total_amount += 250
        if 'Sandwich' in food_items:
            total_amount += 100
        discount = 0.05 * total_amount
        total_amount -= discount
        final_price = total_amount + 300

    elif screen == 'general':
        if 'Popcorn' in food_items:
            total_amount += 450
        if 'Sandwich' in food_items:
            total_amount += 300
        final_price = total_amount

    else:
        return jsonify({"error": "Invalid screen type selected."}), 400

    if request.method == 'POST':
        # Save booking to database
        with sqlite3.connect('booking.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO bookings (theater, movie, screen, food_items, total_price)
                              VALUES (?, ?, ?, ?, ?)''',
                           (session['theater'], session['movie'], session['screen'], session['food_items'], final_price))
            conn.commit()

        return redirect(url_for('finalBookTickets'))

    return render_template('payment.html', final_price=final_price)

# Book Tickets - FINAL
@app.route('/finalBookTickets', methods=['GET', 'POST'])
def finalBookTickets():
    booking_no = random.randint(250, 5670)
    return render_template('finalBookTickets.html', booking_no=booking_no)

# API route to fetch bookings
@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    with sqlite3.connect('booking.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bookings')
        rows = cursor.fetchall()
        bookings = [
            {
                "id": row[0],
                "theater": row[1],
                "movie": row[2],
                "screen": row[3],
                "food_items": row[4],
                "total_price": row[5]
            }
            for row in rows
        ]
    return jsonify(bookings)

if __name__ == "__main__":
    app.run(debug=True)