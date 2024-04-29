import os
import sys
import unittest
from bs4 import BeautifulSoup
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch('src.googleauth.get_user_info')
    def test_login_success(self, mock_get_user_info):
        mock_get_user_info.return_value = {'name': 'Test User', 'sub': 'user_id'}
        with self.client.session_transaction() as session:
            session['state'] = 'test_state'
            # Set user data directly in session (mock login)
            session['user_id'] = 'test_user_id'
        response = self.client.get('/menu', follow_redirects=False)  # Don't follow redirects
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    def test_login_invalid_authorization(self):
        # Simulate error during user info retrieval
        with patch('src.googleauth.get_user_info', side_effect=Exception('Error')):
            with self.client.session_transaction() as session:
                session['state'] = 'test_state'
            response = self.client.get('/login', follow_redirects=False)
        self.assertEqual(response.status_code, 302)  # Assert for redirect (302)
        self.assertIn(b'Redirecting', response.data)  # Check for error message (optional)
        self.assertNotIn(b'welcome', response.data)

    def test_logout(self, mock_get_user_info=None):  
        with patch('src.googleauth.get_user_info', side_effect=Exception('Error')):
            with self.client.session_transaction() as session:
                session['user_id'] = 'test_user_id'  # Set user_id
            response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)  # Assert redirect
        session['user_id'] = None
        self.assertIsNone(session.get('user_id'))  # Assert session cleared

        if mock_get_user_info:
            mock_get_user_info.assert_called_once()
    
    def test_get_menu_logged_in(self):
        with self.client.session_transaction() as session:
            session['user_id'] = 'test_user_id'
        response = self.client.get('/menu')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'menu', response.data)

    def test_get_menu_not_logged_in(self):
        response = self.client.get('/menu')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.location, '/login')

    @patch('src.calendarAPI.build')  # Patch the build function
    def test_get_range_events_success(self, mock_build):
        """Tests successful retrieval of events for a date range."""
        # Mock the build function to return a service object with expected behavior
        mock_service = MagicMock()
        mock_service.events().list().execute.return_value = {
            'items': [
                {
                    'id': 'event_1_id',
                    'summary': 'Event 1',
                    'start': {'dateTime': '2024-05-01T10:00:00-07:00'}  # Example event with date and time
                },
                {
                    'id': 'event_2_id',
                    'summary': 'Event 2',
                    'start': {'date': '2024-05-02'}  # Example event with only date
                }
            ]
        }
        mock_build.return_value = mock_service

        with self.client.session_transaction() as session:
            session['user_id'] = '1234567890'  # Simulate logged-in user
        response = self.client.post('/rangeEvents', data={'start_date': '2024-05-01', 'end_date': '2024-05-10'})
        soup = BeautifulSoup(response.data, 'html.parser')
        events = soup.find_all('div', class_='event-info') 

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(events), 2)  # Assert two events are present
        self.assertIn("Event 1", str(events[0]))
        self.assertIn("Event 2", str(events[1]))


    @patch('src.calendarAPI.get_events')
    def test_get_range_events_user_not_found(self, mock_get_events):
        with self.client.session_transaction() as session:
            session['user_id'] = 'nonexistent_user_id'  # Set an invalid user ID

        response = self.client.post('/rangeEvents', data={'start_date': '2024-05-01', 'end_date': '2024-05-10'})
        self.assertEqual(response.status_code, 302) # Redirect in case invalid user
        self.assertEqual(response.location, '/login')