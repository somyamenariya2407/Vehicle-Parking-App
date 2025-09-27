
from flask import Blueprint,render_template,redirect,request,url_for,session,flash
from models.models import db,User,ParkingLot,ParkingSpot,Reservation,SpotStatus,datetime
import re , random, json 
from collections import defaultdict
from datetime import datetime
import calendar
from flask import jsonify

user_bp = Blueprint('user', __name__ , url_prefix = "/user")

@user_bp.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash("Please login to continue.")
        return redirect(url_for('auth.login'))
    
    

    current_user=User.query.get(session['user_id'])
    reservations=Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.start_time.desc()).all()
    parking_lots=ParkingLot.query.all()
    
    
    # Add a random image to each lot
    image_links = [
        url_for('static', filename='images/parked_car.jpg'),
        url_for('static', filename='images/parking_lot.jpg'),
        url_for('static', filename='images/parking3.jpg'),
        url_for('static', filename='images/parking1.jpg'),
        url_for('static', filename='images/parking2.jpg')
    ]

    for lot in parking_lots:
        lot.random_image = random.choice(image_links)

    
    return render_template('/user/user_dashboard.html',user=current_user,reservations=reservations,lots=parking_lots,SpotStatus=SpotStatus,now=datetime.now())


@user_bp.route('/book_spot/<int:lot_id>' , methods=['POST'])
def book_spot(lot_id):
    if 'user_id' not in session:
        flash("Please login to continue.",'warning')
        return redirect(url_for('auth.login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)

    vehicle_number=request.form.get('vehicle_number','').strip().upper()
    if not vehicle_number or len(vehicle_number) < 4:
        flash("Invalid Vehicle Number!",'danger')
        return redirect(url_for('user.user_dashboard'))
    
    active_park=Reservation.query.filter_by(vehicle_number=vehicle_number, end_time=None).first()
    if active_park:
        flash("Vehicle is already has active reservation","warning")
        return redirect(url_for('user.user_dashboard'))

    spot= ParkingSpot.query.filter_by(lot_id=lot.id, status=SpotStatus.A).first()
    if not spot:
        flash('No available spots in this lot.','danger')
        return redirect(url_for('user.user_dashboard'))
    
    

    reservations=Reservation(spot_id=spot.id,user_id=session['user_id'],lot_id=lot.id,cost=0,vehicle_number= vehicle_number)
    spot.status=SpotStatus.O
    db.session.add(reservations)
    db.session.commit()

    flash(f'Spot {spot.id} reserved!','success')
    return redirect(url_for('user.history'))



@user_bp.route('/release_spot/<int:reservation_id>', methods=['POST'])
def release_spot(reservation_id):
    if 'user_id' not in session:
        flash("Please login to continue.",'warning')
        return redirect(url_for('auth.login'))

    reservation=Reservation.query.get_or_404(reservation_id)

    if reservation.user_id != session.get('user_id'):
        flash('Unauthorized','danger')
        return redirect(url_for('user.user_dashboard'))
    if reservation.end_time:
        flash("Spot already released!!",'info' )
        return redirect(url_for('user.user_dashboard')) 
    
    reservation.end_time=datetime.now()
    lot=reservation.spot.lot
    
    hours=(reservation.end_time - reservation.start_time).total_seconds()/3600
    
    reservation.cost = round(hours * lot.price, 2)
    reservation.spot.status = SpotStatus.A
    db.session.commit()
    
    flash(f'Total Cost: ₹ {reservation.cost:.2f} ','info')
    flash ('Spot released.','success')
    return redirect(url_for('user.history'))



@user_bp.route('/parking_details/<int:reservation_id>')
def parking_details(reservation_id):
    if 'user_id' not in session:
        flash("Please login to continue.",'warning')
        return redirect(url_for('auth.login'))
    
    reservation=Reservation.query.get_or_404(reservation_id)

    if reservation.user_id != session.get('user_id'):
        flash('Unauthorized','danger')
        return redirect(url_for('user.user_dashboard'))

    if reservation.end_time:
        duration = reservation.end_time - reservation.start_time
    else:
        duration = datetime.now() - reservation.start_time

    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    
    return render_template('/user/parking_details.html',reservation=reservation,hours=hours,minutes=minutes)


@user_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        flash("Please login to continue.",'warning')
        return redirect(url_for('auth.login'))
    
    user=User.query.get(session['user_id'])
    return render_template("/user/profile.html",user=user)

@user_bp.route('/edit_profile', methods=['GET','POST'])
def edit_profile():
    if 'user_id' not in session:
        flash("Please login to continue.",'warning')
        return redirect(url_for('auth.login'))
    
    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        
        email= request.form['email'].strip()
        
        name=request.form['name'].strip()
        address=request.form['address'].strip()
        pincode=request.form['pincode'].strip()
        
        if not name or not email or not address or not pincode:
            flash("All fields are required.",'danger')
            return redirect(url_for('user.edit_profile'))
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+",email):
            flash("Invalid email format")
            return redirect(url_for('user.edit_profile'))
        
        
        if not pincode.isdigit() or len(pincode) != 6:
            flash("Pincode must be a 6 digit number.","danger")
            return redirect(url_for('user.edit_profile'))

        if email != user.email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("This email is already in use.", "warning")
                return redirect(url_for('user.edit_profile'))

        
        user.name = name
        user.email = email
        user.address = address
        user.pincode = pincode

        db.session.commit()
        flash('Profile Updated Successfully!','success')
        return redirect(url_for('user.profile'))

    return render_template('/user/edit_profile.html',user=user)


@user_bp.route('/history')
def history():
    if 'user_id' not in session:
        flash("Please login to view history.", "warning")
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    user = User.query.get(user_id) 
    reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.start_time.desc()).all()

    return render_template('user/Uhistory.html',user=user, reservations=reservations,now=datetime.now())

@user_bp.route('/search')
def search():
    if 'user_id' not in session:
        flash("Please login to view history.", "warning")
        return redirect(url_for('auth.login'))
    
    search_by= request.form.get('search_by','') or request.args.get('search_by','')
    query=  request.form.get('query','').strip() or request.args.get('query','').strip()
    results=[]

    user_id=session.get('user_id')
    user = User.query.get(user_id) 
    user_role=session.get('role')

    if user_role == 'user':
        if search_by=='prime_location_name':
                results=ParkingLot.query.filter(ParkingLot.prime_location_name.ilike(f"%{query}%")).all()
        elif search_by=='lot_address':
                results=ParkingLot.query.filter(ParkingLot.address.ilike(f"%{query}%")).all()
        elif search_by=='pin_code_lot':
                results=ParkingLot.query.filter(ParkingLot.pincode.ilike(f"%{query}%")).all()
        elif search_by=='vehicle_number':
                results=Reservation.query.filter(Reservation.vehicle_number.ilike(f"%{query}%")).all()
        else:
            return render_template('/user/search.html', results=results, search_by=search_by, query=query,user=user)
    else:
        return render_template('/user/search.html', results=results)
    return render_template('/user/search.html', results=results, search_by=search_by, query=query,user=user)

@user_bp.route('/summary_charts')
def summary_charts():
    if 'user_id' not in session:
        flash("Please login to view summary charts.", "warning")
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    user = User.query.get(user_id)
    reservations = Reservation.query.filter_by(user_id=user_id).all()
    date_counts = defaultdict(int)
    for res in reservations:
        date_str = res.start_time.strftime('%Y-%m-%d')
        date_counts[date_str] += 1

    dates = sorted(date_counts.keys())
    counts = [date_counts[d] for d in dates]

    # 2. Parking Lot Usage Distribution
    lot_counts = defaultdict(int)

    for res in reservations:
        if res.lot:
            lot_counts[res.lot.prime_location_name] += 1
        else:
            lot_counts["Deleted Lot"] += 1  # fallback label

    lot_labels = list(lot_counts.keys())
    lot_data = list(lot_counts.values())

    # 3. Monthly Cost Summary
    month_costs = defaultdict(float)
    for res in reservations:
        month = res.start_time.strftime('%B')
        month_costs[month] += res.cost or 0

    months = list(calendar.month_name)[1:]  # January to December
    monthly_costs = [month_costs.get(month, 0) for month in months]

     # 4. Reservation Duration Distribution
    duration_bins = {
        "<1 hr": 0,
        "1-2 hrs": 0,
        "2-4 hrs": 0,
        "4+ hrs": 0
    }

    for res in reservations:
        if res.start_time and res.end_time:
            duration = (res.end_time - res.start_time).total_seconds() / 3600  # in hours
            if duration < 1:
                duration_bins["<1 hr"] += 1
            elif duration < 2:
                duration_bins["1-2 hrs"] += 1
            elif duration < 4:
                duration_bins["2-4 hrs"] += 1
            else:
                duration_bins["4+ hrs"] += 1

    duration_labels = list(duration_bins.keys())
    duration_data = list(duration_bins.values())

    return render_template(
        '/user/charts.html',
        dates=dates,user=user,
        counts=counts,
        lot_labels=lot_labels,
        lot_data=lot_data,
        months=months,
        monthly_costs=monthly_costs,
        duration_labels=duration_labels,
        duration_data=duration_data
    )