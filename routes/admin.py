from flask import Blueprint,render_template,redirect,request,url_for,session,flash
from models.models import db,User,ParkingLot,ParkingSpot,Reservation,SpotStatus
from datetime import datetime
from sqlalchemy import extract, func
from collections import defaultdict
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__,url_prefix="/admin")


def createadmin():
    admin_user = User.query.filter_by(role='admin').first()

    if not admin_user:
        hashed_pass= generate_password_hash('admin@123')
        admin = User(email='admin24@gmail.com',password=hashed_pass,name='Admin',role='admin')
        db.session.add(admin)
        db.session.commit()
        print("Admin Created")
    else:
        print("Admin Already Exists")



@admin_bp.route('/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    
    lots=ParkingLot.query.all()
    return render_template('/admin/admin_dashboard.html',lots=lots)


@admin_bp.route('/create_lot', methods=['GET','POST'])
def create_lot():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    
    if request.method=='POST':

        prime_location_name=request.form['prime_location_name']
        price=float(request.form['price'])
        address=request.form['address']
        pincode=request.form['pincode']
        maximum_number_of_spots=int(request.form['maximum_number_of_spots'])


        lot=ParkingLot(prime_location_name=prime_location_name, price=price, address=address, pincode=pincode, maximum_number_of_spots=maximum_number_of_spots )
        db.session.add(lot)
        db.session.commit()

        for i in range(maximum_number_of_spots):
            spot = ParkingSpot(lot_id=lot.id, status=SpotStatus.A)
            db.session.add(spot)
            db.session.commit()

        flash("Parking Lot Added Successfully!!",'success')
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('/admin/create_lot.html')


@admin_bp.route('/lot/<int:lot_id>')
def lot_details(lot_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    
    lot=ParkingLot.query.get_or_404(lot_id)
    spots=ParkingSpot.query.filter_by(lot_id=lot_id).all()
    return render_template('/admin/lot_details.html', lot=lot ,spots=spots)


@admin_bp.route('/lot/<int:lot_id>/add_spot', methods=['GET','POST'])
def add_spot(lot_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))

    lot = ParkingLot.query.get_or_404(lot_id)

    if request.method == 'POST':
        status = request.form.get('status')

        new_spot = ParkingSpot(
            lot_id=lot.id,
            status=status
        )
        db.session.add(new_spot)
        lot.maximum_number_of_spots += 1
        db.session.commit()
        flash("Spot added successfully.")
        return redirect(url_for('admin.lot_details', lot_id=lot.id))

    return render_template('/admin/add_spot.html', lot=lot)



@admin_bp.route('/edit_lot/<int:lot_id>', methods=['GET','POST'])
def edit_lot(lot_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    
    lot=ParkingLot.query.get_or_404(lot_id)

    if request.method=='POST':
        lot.prime_location_name=request.form['prime_location_name']
        lot.price=float(request.form['price'])
        lot.address=request.form['address']
        lot.pincode=request.form['pincode']
        lot.maximum_number_of_spots=int(request.form['maximum_number_of_spots'])


        current_spots= ParkingSpot.query.filter_by(lot_id=lot.id).count()
        new_spot_length=lot.maximum_number_of_spots
        occupied_spots = sum(1 for spot in lot.spots if spot.status == SpotStatus.O)

        if new_spot_length < occupied_spots:
            flash(f"Cannot reduce total spots to {new_spot_length}. {occupied_spots} spots are currently occupied.", "danger")
            return redirect(url_for('admin.admin_dashboard', lot_id=lot.id))

        new_spot_length=lot.maximum_number_of_spots
        
        if new_spot_length > current_spots:
            for i in range(new_spot_length - current_spots):
                new_spot = ParkingSpot(lot_id=lot.id, status=SpotStatus.A)
                db.session.add(new_spot)
        
        elif new_spot_length< current_spots:
            available_spots=[spot for spot in lot.spots if spot.status == SpotStatus.A]
            spot_remove= current_spots-new_spot_length
            for spot in available_spots[:spot_remove]:
                db.session.delete(spot)

        db.session.commit()
        flash("Parking Lot Updated Successfully. ","success")
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('/admin/edit_lot.html',lot=lot)


@admin_bp.route('/delete_lot/<int:lot_id>')

def delete_lot(lot_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    
    lot =ParkingLot.query.get_or_404(lot_id)
    
    occupied_spot=[spot for spot in lot.spots if spot.status == SpotStatus.O]

    if occupied_spot:
        flash('Cannot delete lot!! spots are currently occupied.','danger')
        return redirect(url_for('admin.admin_dashboard'))
    
    ParkingSpot.query.filter_by(lot_id=lot.id).delete()
    db.session.delete(lot)
    db.session.commit()
    flash("Lot Deleted Successfully!", "success")
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/user_list')
def user_list():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    
    users=User.query.all()
    return render_template('/admin/user_list.html', users=users)


@admin_bp.route('/view_spot/<int:spot_id>')
def view_spot(spot_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    
    spot = ParkingSpot.query.get_or_404(spot_id)
    active_cost=Reservation.query.filter_by(spot_id=spot.id, end_time=None).first()
    cur_reserv=Reservation.query.filter_by(spot_id=spot_id, end_time=None).order_by(Reservation.start_time.desc()).first()

    return render_template('admin/view_spot.html', spot=spot , reservation=active_cost ,resrvation=cur_reserv, now=datetime.now())


@admin_bp.route('/delete_spot/<int:spot_id>')
def delete_spot(spot_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    
    spot = ParkingSpot.query.get_or_404(spot_id)
    if spot.reservation:
        flash('Cannot delete spot! Its reserved.','danger')
        return redirect(url_for('admin.admin_dashboard'))
    
    lot=spot.lot
    
    db.session.delete(spot)
    db.session.commit()
    
    lot.maximum_number_of_spots=len(lot.spots)
    db.session.commit()
    
    flash("Parking Spot deleted successfully!", "success")
    return redirect(url_for('admin.admin_dashboard', lot_id=lot.id))

@admin_bp.route('/search' , methods=['GET','POST'])
def search():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    
    search_by= request.form.get('search_by','') or request.args.get('search_by','')
    query=  request.form.get('query','').strip() or request.args.get('query','').strip()
    results=[]

    user_id=session.get('user_id')
    user = User.query.get(user_id) 
    user_role=session.get('role')

    if user_role == 'admin':
        if search_by == 'user_id' and query.isdigit():
                results = User.query.filter(User.id == int(query)).all()
        elif search_by=='name':
                results=User.query.filter(User.name.ilike(f"%{query}%")).all()
        elif search_by=='user_email':
                results=User.query.filter(User.email.ilike(f"%{query}%")).all()
        elif search_by=='user_address':
                results=User.query.filter(User.address.ilike(f"%{query}%")).all()
        elif search_by=='pin_code':
                results=User.query.filter(User.pincode.ilike(f"%{query}%")).all()
        elif search_by=='lot_id' and query.isdigit():
                results= ParkingLot.query.filter(ParkingLot.id == int(query)).all()
        elif search_by=='prime_location_name':
                results=ParkingLot.query.filter(ParkingLot.prime_location_name.ilike(f"%{query}%")).all()
        elif search_by=='lot_address':
                results=ParkingLot.query.filter(ParkingLot.address.ilike(f"%{query}%")).all()
        elif search_by=='pin_code_lot':
                results=ParkingLot.query.filter(ParkingLot.pincode.ilike(f"%{query}%")).all()
        elif search_by=='reservation_id' and query.isdigit():
                results=Reservation.query.filter(Reservation.id==int(query)).all()
        else:
            return render_template('/admin/search.html', results=results, search_by=search_by, query=query)
         
    else:
        return render_template('/admin/search.html', results=results)        
    return render_template('/admin/search.html', results=results, search_by=search_by, query=query)


@admin_bp.route('/summary')
def summary():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
     
    users=User.query.all()
    total_revenue=0
    user_costs={}
    user_reservations = {}

    for user in users:
        reservations=Reservation.query.filter_by(user_id=user.id).all()
        user_reservations[user]= reservations
        total_cost=0

        for r in reservations:
            if r.end_time and r.start_time:
                hours = (r.end_time - r.start_time).total_seconds() / 3600
                lot=ParkingLot.query.get(r.lot_id)
                if lot:
                    cost=round(hours * lot.price ,2)
                    total_cost+=cost
                    total_revenue+=cost

        user_costs[user.id] = round(total_cost, 2)

    return render_template('/admin/summary.html',user_reservations=user_reservations,user_costs=user_costs,total_revenue=round(total_revenue,2))


@admin_bp.route('/charts')
def charts():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login'))
    

    users = User.query.filter(User.role != 'admin').all()
    
    user_labels = [u.name for u in users]
    user_earnings = []
    user_reservations = []

    for user in users:
        res = Reservation.query.filter_by(user_id=user.id).all()
        earnings = sum(r.cost or 0 for r in res)
        user_earnings.append(earnings)
        user_reservations.append(len(res))

    # Parking lot revenue
    lots = ParkingLot.query.all()
    lot_labels = [l.prime_location_name for l in lots]
    lot_earnings = [
        sum(r.cost or 0 for r in Reservation.query.filter_by(lot_id=l.id).all())
        for l in lots
    ]

    # Monthly revenue
    monthly_data = db.session.query(
        extract('month', Reservation.start_time).label('month'),
        func.sum(Reservation.cost)
    ).join(User).filter(User.role != 'admin').group_by('month').order_by('month').all()

    months = [f'Month {int(month)}' for month, _ in monthly_data]
    monthly_revenue = [round(total, 2) for _, total in monthly_data]

    total_revenue = round(sum(user_earnings), 2)

    chart_data = {
        'user_labels': user_labels,
        'user_earnings': user_earnings,
        'user_reservations': user_reservations,
        'lot_labels': lot_labels,
        'lot_earnings': lot_earnings,
        'months': months,
        'monthly_revenue': monthly_revenue
    }

    return render_template(
        '/admin/Acharts.html',
        chart_data=chart_data,
        total_revenue=total_revenue
    )