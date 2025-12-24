"""
Pytest configuration and shared fixtures
"""
import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Application, InterviewSlot
from app.utils.security import hash_password


@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope='function')
def fresh_app():
    """Create fresh application for each test"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(fresh_app):
    """Create test client"""
    return fresh_app.test_client()


@pytest.fixture
def runner(fresh_app):
    """Create test CLI runner"""
    return fresh_app.test_cli_runner()
