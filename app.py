from flask import Flask, render_template, request, url_for,flash, redirect,session

app = Flask(__name__)
app.secret_key='this_is_my_secrect_key'


#basic route
@app.route("/", methods=["GET", "POST"])
def home() :
    return render_template('index.html')

#booking tickets
@app.route("/book_tickets", methods=['GET','POST'])
def book_tickets():
    if request.method == "POST":
        session['theater'] = request.form.get("theater")
        session['movie'] = request.form.get("movie")
        session['screen'] = request.form.get("screen")
        return redirect(url_for("select_beverages"))

    return render_template("bookTickets.html")

#select beverages
@app.route("/select_beverages", methods=['GET','POST'])
def select_beverages() :
    if request.method == 'POST':
        food_items = request.form.getlist('foodandbeverages')
        session['food_items'] = food_items
        return redirect("confirm_booking")   
    return render_template("selectBeverages.html")

#confirm booking
@app.route("/confirm_booking" , methods = ['GET', 'POST'])
def confirm_booking ():
    theater = session.get('theater', 'Not Selected')
    movie = session.get('movie', 'Not Selected')
    screen = session.get('screen','Not Selected')
    food_items = session.get('food_items', [] )
    if request.method == 'POST':
        return redirect("payment")
    return render_template('confirmBooking.html',
        theater = theater ,
        movie = movie,
        screen = screen,
        food_items = food_items
    )

#payment 
@app.route("/payment", methods = ['GET','POST'])
def payment():
    screen = session.get('screen','Not Selected')
    return render_template('payment.html')

if __name__ == "__main__" :
    app.run(debug=True)