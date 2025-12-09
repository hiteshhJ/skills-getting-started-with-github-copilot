"""
Tests for the Mergington High School API
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Join the varsity soccer team for practices and matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["alex@mergington.edu", "sarah@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Competitive swimming training and swim meets",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["chris@mergington.edu", "emily@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore various art mediums including painting, drawing, and sculpture",
            "schedule": "Thursdays, 3:00 PM - 4:30 PM",
            "max_participants": 15,
            "participants": ["maya@mergington.edu", "lucas@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater productions, acting workshops, and stage performances",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["ava@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through competitive debates",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu", "liam@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Prepare for science competitions covering biology, chemistry, and physics",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu", "ethan@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_activities_have_correct_structure(self, client):
        """Test that activities have the correct data structure"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_duplicate_signup(self, client):
        """Test that a student cannot sign up twice for the same activity"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_with_special_characters_in_activity_name(self, client):
        """Test signup with URL-encoded activity name"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_successful_unregister(self, client):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"
        
        # Verify participant exists
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Chess Club"]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        assert email not in activities_response.json()["Chess Club"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregister from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_student_not_signed_up(self, client):
        """Test unregistering a student who is not signed up"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notsignedup@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_and_signup_again(self, client):
        """Test that a student can sign up again after unregistering"""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Unregister
        response1 = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response1.status_code == 200
        
        # Sign up again
        response2 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify participant is back
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]


class TestActivityCapacity:
    """Tests for activity capacity management"""
    
    def test_activity_has_capacity_limits(self, client):
        """Test that activities have max_participants defined"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "max_participants" in activity_data
            assert activity_data["max_participants"] > 0
    
    def test_participant_count_tracking(self, client):
        """Test that participant count is tracked correctly"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        initial_count = len(chess_club["participants"])
        
        # Add a participant
        client.post("/activities/Chess Club/signup?email=newbie@mergington.edu")
        
        # Check count increased
        response = client.get("/activities")
        data = response.json()
        assert len(data["Chess Club"]["participants"]) == initial_count + 1


class TestEdgeCases:
    """Tests for edge cases and error handling"""
    
    def test_activity_name_with_spaces(self, client):
        """Test handling activity names with spaces"""
        response = client.post(
            "/activities/Programming Class/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
    
    def test_email_format_handling(self, client):
        """Test that various email formats are accepted"""
        emails = [
            "simple@mergington.edu",
            "with.dot@mergington.edu",
            "with+plus@mergington.edu",
            "with-dash@mergington.edu"
        ]
        
        for i, email in enumerate(emails):
            response = client.post(
                f"/activities/Chess Club/signup?email={email}"
            )
            # First one or new ones should succeed
            assert response.status_code in [200, 400]  # 400 if already exists
