from flask import Flask, render_template, request, url_for, flash, redirect, session, jsonify
import sqlite3
import random
import datetime
import string
import json

app = Flask(__name__)
app.secret_key = 'this_is_my_secret_key'

# Load theater data
try:
    with open("theater_data.json", "r") as f:
        theater_data = json.load(f)
except FileNotFoundError:
    print("Error: 'theater_data.json' not found. Ensure the file exists in the correct location.")
    theater_data = {}

# Database setup
def init_db():
    with sqlite3.connect('booking.db') as conn:
        cursor = conn.cursor()
        # Create bookings table
        cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            theater TEXT,
                            movie TEXT,
                            screen TEXT,
                            food_items TEXT,
                            total_price REAL,
                            booking_time DATETIME,
                            seat_number INTEGER,
                            booking_id TEXT,
                            canceled INTEGER DEFAULT 0
                          )''')
        # Create waiting list table
        cursor.execute('''CREATE TABLE IF NOT EXISTS waiting_list (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            theater TEXT,
                            movie TEXT,
                            screen TEXT,
                            user_data TEXT,
                            join_time DATETIME
                          )''')
        # Create seat availability table
        cursor.execute('''CREATE TABLE IF NOT EXISTS seats (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            theater TEXT,
                            screen TEXT,
                            total_seats INTEGER,
                            booked_seats INTEGER
                          )''')
        # Initialize seats using JSON
        cursor.execute('SELECT COUNT(*) FROM seats')
        if cursor.fetchone()[0] == 0 and 'theaters' in theater_data:
            for theater_id, theater_info in theater_data['theaters'].items():
                for screen_type, screen_info in theater_info.get('screens', {}).items():
                    cursor.execute('''INSERT INTO seats (theater, screen, total_seats, booked_seats)
                                      VALUES (?, ?, ?, ?)''',
                                   (theater_id, screen_type, screen_info['total_seats'], 0))
        conn.commit()

init_db()

# Home route
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/book_tickets", methods=['GET', 'POST'])
def book_tickets():
    if request.method == "POST":
        theater = request.form.get("theater")
        movie = request.form.get("movie")
        screen = request.form.get("screen")

        # Ensure all required fields are provided
        if not all([theater, movie, screen]):
            flash('Please select theater, movie, and screen.')
            return redirect(url_for('book_tickets'))

        session['theater'] = theater
        session['movie'] = movie
        session['screen'] = screen

        # Check seat availability
        with sqlite3.connect('booking.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT total_seats, booked_seats FROM seats WHERE theater = ? AND screen = ?', (theater, screen))
            seat_data = cursor.fetchone()

            # Handle invalid or missing seat data
            if not seat_data:
                flash('Invalid theater or screen selection. Please try again.')
                return redirect(url_for('book_tickets'))

            total_seats, booked_seats = seat_data

            # If no seats are available, add to the waitlist
            if booked_seats >= total_seats:
                cursor.execute('''INSERT INTO waiting_list (theater, movie, screen, join_time)
                                  VALUES (?, ?, ?, ?)''',
                               (theater, movie, screen, datetime.datetime.now()))
                conn.commit()
                flash(f"No seats available. You have been added to the waiting list for {movie} at {theater} ({screen}).")
                return redirect(url_for('home'))

        # If seats are available, proceed to the next step
        return redirect(url_for("select_beverages"))

    # Prepare dropdown data for the template
    theaters = [{"id": k, "name": v["name"]} for k, v in theater_data["theaters"].items()]
    movies = [{"id": k, "name": v["name"], "date_time": v["date_time"]} for k, v in theater_data["movies"].items()]
    selected_theater = list(theater_data["theaters"].keys())[0]
    screens = [{"type": k, "price": v["price"], "total_seats": v["total_seats"]}
               for k, v in theater_data["theaters"][selected_theater]["screens"].items()]

    return render_template(
        "bookTickets.html",
        theaters=theaters,
        movies=movies,
        screens=screens
    )

# Select beverages
@app.route("/select_beverages", methods=['GET', 'POST'])
def select_beverages():
    if request.method == 'POST':
        food_items = request.form.getlist('foodandbeverages')
        session['food_items'] = ','.join(food_items)
        return redirect(url_for("confirm_booking"))
    return render_template("selectBeverages.html")

# Confirm booking
@app.route("/confirm_booking", methods=['GET', 'POST'])
def confirm_booking():
    theater = session.get('theater')
    movie = session.get('movie')
    screen = session.get('screen')
    food_items = session.get('food_items', '').split(',')

    if not all([theater, movie, screen]):
        flash('Incomplete booking details.')
        return redirect(url_for('home'))

    # Calculate price
    screen_price = theater_data['theaters'][theater]['screens'][screen]['price']
    food_prices = {"Popcorn": 250, "Sandwich": 100}
    food_total = sum(food_prices.get(item, 0) for item in food_items)

    discount = 0
    if screen == 'gold':
        discount = 0.1 * (screen_price + food_total)
    elif screen == 'max':
        discount = 0.05 * (screen_price + food_total)

    total_price = screen_price + food_total - discount
    session['total_price'] = total_price

    if request.method == 'POST':
        return redirect(url_for("payment"))

    return render_template("confirmBooking.html",
                           theater=theater, movie=movie, screen=screen,
                           food_items=food_items, total_price=total_price)

# Payment
@app.route("/payment", methods=['GET', 'POST'])
def payment():
    theater = session.get('theater')
    movie = session.get('movie')
    screen = session.get('screen')
    food_items = session.get('food_items')
    total_price = session.get('total_price')

    if not all([theater, movie, screen, total_price]):
        flash("Incomplete booking details. Please start again.")
        return redirect(url_for('book_tickets'))

    if request.method == 'POST':
        # Generate booking ID
        booking_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        session['booking_id'] = booking_id

        # Save booking to database
        with sqlite3.connect('booking.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT booked_seats FROM seats WHERE theater = ? AND screen = ?', (theater, screen))
            booked_seats = cursor.fetchone()[0] + 1
            cursor.execute('UPDATE seats SET booked_seats = booked_seats + 1 WHERE theater = ? AND screen = ?', (theater, screen))
            cursor.execute('''INSERT INTO bookings (theater, movie, screen, food_items, total_price, booking_time, seat_number, booking_id)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                           (theater, movie, screen, food_items, total_price, datetime.datetime.now(), booked_seats, booking_id))
            conn.commit()

        return redirect(url_for("final_booking"))

    return render_template("payment.html", total_price=total_price)

# Final booking page
@app.route('/final_booking', methods=['GET'])
def final_booking():
    booking_id = session.get('booking_id', None)
    if not booking_id:
        flash("No booking found!")
        return redirect(url_for("home"))
    return render_template("finalBookTickets.html", booking_id=booking_id)

# Cancel booking
@app.route("/cancel_booking", methods=['POST'])
def cancel_booking():
    booking_id = request.form.get('booking_id')
    with sqlite3.connect("booking.db") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE bookings SET canceled = 1 WHERE booking_id = ?", (booking_id,))
        cursor.execute('UPDATE seats SET booked_seats = booked_seats - 1 WHERE theater = ? AND screen = ?', (session['theater'], session['screen']))
        conn.commit()
    flash("Booking canceled successfully!")
    return redirect(url_for("view_previous_bookings"))

# View previous bookings
@app.route("/view_previous_bookings", methods=["GET"])
def view_previous_bookings():
    with sqlite3.connect('booking.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE canceled = 0")
        rows = cursor.fetchall()
        bookings = []
        now = datetime.datetime.now()
        for row in rows:
            booking_time = datetime.datetime.strptime(row[6], '%Y-%m-%d %H:%M:%S.%f')
            cancelable = (booking_time - now).total_seconds() > 30 * 60
            bookings.append({
                "id": row[0],
                "theater": row[1],
                "movie": row[2],
                "screen": row[3],
                "food_items": row[4],
                "total_price": row[5],
                "booking_time": row[6],
                "seat_number": row[7],
                "booking_id": row[8],
                "cancelable": cancelable
            })
    return render_template("previousBookings.html", previous_bookings=bookings)

if __name__ == "__main__":
    app.run(debug=True)
