"""API routes for slot management"""
from flask import jsonify, request
from flask_login import login_required, current_user
from app.api import api_bp
from app.models import InterviewSlot, SlotBooking
from datetime import datetime


@api_bp.route('/slots', methods=['GET'])
@login_required
def get_slots():
    """Get all available slots (API endpoint for real-time updates)"""
    date_filter = request.args.get('date')
    
    # Get future slots only
    today = datetime.now().date()
    query = InterviewSlot.query.filter(InterviewSlot.date >= today)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter_by(date=filter_date)
        except ValueError:
            pass
    
    slots = query.order_by(InterviewSlot.date, InterviewSlot.start_time).all()
    
    # Serialize slots
    slots_data = []
    for slot in slots:
        slots_data.append({
            'id': slot.id,
            'date': slot.date.strftime('%Y-%m-%d'),
            'start_time': slot.start_time.strftime('%H:%M'),
            'end_time': slot.end_time.strftime('%H:%M'),
            'capacity': slot.capacity,
            'current_bookings': slot.current_bookings,
            'available_spots': slot.available_spots,
            'is_open': slot.is_open,
            'is_available': slot.is_available,
            'is_full': slot.is_full
        })
    
    return jsonify({
        'success': True,
        'slots': slots_data,
        'total': len(slots_data)
    })


@api_bp.route('/slots/<int:slot_id>', methods=['GET'])
@login_required
def get_slot(slot_id):
    """Get details of a specific slot"""
    slot = InterviewSlot.query.get_or_404(slot_id)
    
    slot_data = {
        'id': slot.id,
        'date': slot.date.strftime('%Y-%m-%d'),
        'start_time': slot.start_time.strftime('%H:%M'),
        'end_time': slot.end_time.strftime('%H:%M'),
        'capacity': slot.capacity,
        'current_bookings': slot.current_bookings,
        'available_spots': slot.available_spots,
        'is_open': slot.is_open,
        'is_available': slot.is_available,
        'is_full': slot.is_full
    }
    
    # If admin, include bookings info
    if current_user.role == 'admin':
        bookings = []
        for booking in slot.bookings:
            bookings.append({
                'user_name': booking.user.name,
                'user_email': booking.user.email,
                'booked_at': booking.booked_at.strftime('%Y-%m-%d %H:%M')
            })
        slot_data['bookings'] = bookings
    
    return jsonify({
        'success': True,
        'slot': slot_data
    })


@api_bp.route('/my-booking', methods=['GET'])
@login_required
def get_my_booking():
    """Get current user's booking"""
    if current_user.role != 'candidate':
        return jsonify({'success': False, 'message': 'Only candidates can have bookings'}), 403
    
    booking = SlotBooking.query.filter_by(user_id=current_user.id).first()
    
    if not booking:
        return jsonify({
            'success': True,
            'has_booking': False
        })
    
    slot = booking.slot
    
    return jsonify({
        'success': True,
        'has_booking': True,
        'booking': {
            'id': booking.id,
            'booked_at': booking.booked_at.strftime('%Y-%m-%d %H:%M'),
            'slot': {
                'id': slot.id,
                'date': slot.date.strftime('%Y-%m-%d'),
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M')
            }
        }
    })


@api_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """Get system statistics (admin only)"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    from app.models import User, Application
    
    stats = {
        'total_candidates': User.query.filter_by(role='candidate').count(),
        'total_slots': InterviewSlot.query.count(),
        'available_slots': InterviewSlot.query.filter_by(is_open=True).filter(
            InterviewSlot.current_bookings < InterviewSlot.capacity
        ).count(),
        'total_bookings': SlotBooking.query.count(),
        'pending_applications': Application.query.filter_by(status='pending').count(),
        'slot_selected': Application.query.filter_by(status='slot_selected').count()
    }
    
    return jsonify({
        'success': True,
        'stats': stats
    })
