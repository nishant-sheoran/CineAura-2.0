
# **CineAura** 🎬  
*A Comprehensive Theater Ticket and Food Management System*

---

## **Overview**  
**CineAura** is a Flask-based web application that simplifies ticket booking and food management for a nationwide moving theater company. The system supports seamless booking, automatic seat allocation, food order integration, and waitlist handling, offering a smooth experience for both customers and theater operators.

---

## **Features**  

### 🎟 **Ticket Booking**  
- Multi-screen support:  
  - **Gold**: ₹400/ticket (2 seats/screen)  
  - **Max**: ₹300/ticket (5 seats/screen)  
  - **General**: ₹200/ticket (10 seats/screen)  
- Automatic seat allocation based on availability.  

### 🍿 **Food & Beverage Integration**  
- Options: **Popcorn** and **Sandwich**.  
- Discounts for premium users:  
  - Gold ticket: **10% off on food**  
  - Max ticket: **5% off on food**  

### 🕒 **Booking Cancellation**  
- Easy cancellations up to **30 minutes** before showtime.  

### 📋 **Waitlist Management**  
- Users can join a waitlist if seats are sold out.  
- Canceled tickets are reassigned to waitlisted users on a **first-come, first-serve basis**.  

---

## **Technology Stack**  

- **Backend**: Flask (Python)  
- **Database**: SQLite  
- **Frontend**: HTML, CSS (extendable for future features)  

---

## **Installation**  

1. Clone the repository:  
   ```bash
   git clone https://github.com/nishant-sheoran/CineAura.git
   cd CineAura
   ```

2. Create a virtual environment and activate it:  
   ```bash
   python -m venv venv  
   source venv/bin/activate  # For Linux/MacOS  
   venv\Scripts\activate     # For Windows  
   ```

3. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:  
   ```bash
   flask run
   ```

5. Open the application in your browser:  
   ```
   http://127.0.0.1:5000/
   ```

---

## **Usage**  

### **Booking a Ticket**  
- Select a theater, movie, and ticket category (Gold/Max/General).  
- Optionally, add food items (Popcorn/Sandwich).  
- Confirm your booking and view the summary.  

### **Canceling a Booking**  
- Cancel your booking up to **30 minutes before showtime**.  

### **Waitlist**  
- If the screen is sold out, join the waitlist (available until 30 minutes before showtime).  
- Tickets are reassigned to waitlisted users automatically upon cancellations.  

---

## **Database Schema**  

The application uses SQLite for managing data. Below is a simplified schema:  

### **Tables**  
1. **Theaters**  
   - `id`: Primary key  
   - `name`: Name of the theater  
   - `location`: City/State  

2. **Screens**  
   - `id`: Primary key  
   - `theater_id`: Foreign key linking to a theater  
   - `type`: Screen type (Gold, Max, General)  
   - `seats`: Total seats available  

3. **Bookings**  
   - `id`: Primary key  
   - `user_name`: Name of the user  
   - `screen_id`: Foreign key linking to a screen  
   - `movie_name`: Name of the movie  
   - `show_time`: Showtime of the movie  
   - `food_items`: List of food items ordered (if any)  
   - `status`: Booking status (Confirmed/Cancelled)  

4. **Waitlist**  
   - `id`: Primary key  
   - `screen_id`: Foreign key linking to a screen  
   - `user_name`: Name of the user  
   - `position`: Queue position  

---

## **Future Enhancements**  
- **User Authentication**: Implement login and signup features.  
- **Online Payments**: Integrate payment gateways.  
- **Dynamic Pricing**: Adjust ticket prices based on demand and availability.  
- **Reporting**: Add admin dashboards for sales and performance tracking.  

---

## **Contributing**  

We welcome contributions to improve CineAura!  

1. Fork the repository.  
2. Create a new branch:  
   ```bash
   git checkout -b feature-name
   ```  
3. Commit your changes:  
   ```bash
   git commit -m "Added a new feature"
   ```  
4. Push to your branch:  
   ```bash
   git push origin feature-name
   ```  
5. Open a pull request.

---

## **License**  
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.  

---

## **Contact**  
For questions or feedback, reach out at:  
**Nishant Sheoran**  
GitHub: [nishant-sheoran](https://github.com/nishant-sheoran)  
**Krithi**  
GitHub: [kri1105](https://github.com/kri1105) 

---
