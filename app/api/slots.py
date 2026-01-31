"""API routes for slot management"""
from flask import jsonify, request
from flask_login import login_required, current_user
from app.api import api_bp
from app.models import InterviewSlot, SlotBooking
from app import db
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)


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


@api_bp.route('/slots/<int:slot_id>/book', methods=['POST'])
@login_required
def ajax_book_slot(slot_id):
    """AJAX endpoint for booking with instant feedback"""
    if current_user.role != 'candidate':
        return jsonify({'success': False, 'message': 'Only candidates can book slots'}), 403
    
    # Check if candidate already has a slot
    existing_booking = SlotBooking.query.filter_by(user_id=current_user.id).first()
    if existing_booking:
        return jsonify({
            'success': False, 
            'message': 'You have already booked a slot. Cancel it first to book a new one.',
            'error_type': 'already_booked'
        }), 400
    
    try:
        # Use database-level locking 
        slot = InterviewSlot.query.with_for_update().get(slot_id)
        
        if not slot:
            return jsonify({'success': False, 'message': 'Slot not found'}), 404
        
        if not slot.is_open:
            return jsonify({
                'success': False, 
                'message': 'This slot is no longer open for booking.',
                'error_type': 'slot_closed'
            }), 400
        
        if slot.current_bookings >= slot.capacity:
            return jsonify({
                'success': False, 
                'message': 'Sorry, this slot was just booked by someone else. Please select a different slot.',
                'error_type': 'slot_full',
                'slot': {
                    'id': slot.id,
                    'is_available': False,
                    'is_full': True,
                    'available_spots': 0
                }
            }), 409  # Conflict status
        
        # Check if slot is in the past
        now = datetime.now()
        slot_datetime = datetime.combine(slot.date, slot.start_time)
        if slot_datetime < now:
            return jsonify({
                'success': False, 
                'message': 'Cannot book a slot in the past',
                'error_type': 'past_slot'
            }), 400
        
        # Create booking
        booking = SlotBooking(
            slot_id=slot_id,
            user_id=current_user.id,
            confirmed=True
        )
        db.session.add(booking)
        
        # Increment counters
        slot.current_bookings += 1
        slot.version += 1
        
        # Update application status
        if current_user.application:
            current_user.application.status = 'slot_selected'
        
        db.session.commit()
        
        logger.info(f"User {current_user.id} booked slot {slot_id}")
        
        return jsonify({
            'success': True,
            'message': 'Interview slot booked successfully!',
            'booking': {
                'id': booking.id,
                'slot': {
                    'id': slot.id,
                    'date': slot.date.strftime('%Y-%m-%d'),
                    'start_time': slot.start_time.strftime('%H:%M'),
                    'end_time': slot.end_time.strftime('%H:%M')
                }
            }
        })
    
    except IntegrityError:
        db.session.rollback()
        logger.error(f"Integrity error booking slot {slot_id} for user {current_user.id}")
        return jsonify({
            'success': False, 
            'message': 'Booking failed. You may already have a booking.',
            'error_type': 'integrity_error'
        }), 409
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error booking slot {slot_id} for user {current_user.id}: {str(e)}")
        return jsonify({
            'success': False, 
            'message': 'An error occurred. Please try again.',
            'error_type': 'server_error'
        }), 500
