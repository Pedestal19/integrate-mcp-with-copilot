"""
High School Management System API

A FastAPI application that allows students to view and sign up
for extracurricular activities with persistent SQLite database.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from sqlalchemy.orm import Session

from database import init_db, get_db
from models import Activity, User, UserRole, activity_participants

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    """Initialize database and seed with sample data."""
    init_db()
    # Seed data will be added if database is empty
    seed_initial_data()


def seed_initial_data():
    """Seed the database with initial sample activities."""
    db = next(get_db())
    
    # Check if activities already exist
    if db.query(Activity).count() > 0:
        db.close()
        return
    
    # Sample activities data (same as before)
    sample_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "location": "Room 101",
            "max_participants": 12,
            "category": "non-technical"
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "location": "Lab 201",
            "max_participants": 20,
            "category": "technical"
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "location": "Gymnasium",
            "max_participants": 30,
            "category": "sports"
        },
        "Soccer Team": {
            "description": "Join the school soccer team and compete in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "location": "Sports Field",
            "max_participants": 22,
            "category": "sports"
        },
        "Basketball Team": {
            "description": "Practice and play basketball with the school team",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "location": "Gymnasium",
            "max_participants": 15,
            "category": "sports"
        },
        "Art Club": {
            "description": "Explore your creativity through painting and drawing",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "location": "Art Studio",
            "max_participants": 15,
            "category": "non-technical"
        },
        "Drama Club": {
            "description": "Act, direct, and produce plays and performances",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "location": "Auditorium",
            "max_participants": 20,
            "category": "non-technical"
        },
        "Math Club": {
            "description": "Solve challenging problems and participate in math competitions",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "location": "Room 202",
            "max_participants": 10,
            "category": "technical"
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "location": "Room 103",
            "max_participants": 12,
            "category": "non-technical"
        }
    },
        "Manga Maniacs": {
            "description": "Explore the fantastic stories of the most interesting characters in Japanese manga (graphic novels)",
            "schedule": "Tuesdays at 7:00 PM",
            "location": "Library",
            "max_participants": 15,
            "category": "non-technical"
        }
    }
    
    # Create activities in database
    for name, data in sample_activities.items():
        activity = Activity(
            name=name,
            description=data["description"],
            schedule=data["schedule"],
            location=data.get("location"),
            max_participants=data["max_participants"],
            category=data["category"]
        )
        db.add(activity)
    
    db.commit()
    db.close()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(db: Session = Depends(get_db)):
    """Get all activities with their details and current participant count."""
    activities = db.query(Activity).filter(Activity.is_active == 1).all()
    result = {}
    for activity in activities:
        result[activity.name] = {
            "description": activity.description,
            "schedule": activity.schedule,
            "location": activity.location,
            "max_participants": activity.max_participants,
            "category": activity.category,
            "participants": [user.email for user in activity.participants],
        }
    return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Sign up a student for an activity."""
    # Validate activity exists
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Check if activity is full
    if activity.is_full:
        raise HTTPException(
            status_code=400,
            detail="Activity is full"
        )
    
    # Find or create user (simplified temporary flow until auth is implemented)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Use a placeholder hash value for now; real password flow comes with auth issue.
        user = User(
            email=email,
            name=email.split("@")[0],
            hashed_password="TEMP_AUTH_NOT_ENABLED",
            role=UserRole.STUDENT
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Validate user is not already signed up
    if user in activity.participants:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )
    
    # Add user to activity
    activity.participants.append(user)
    db.commit()
    
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Unregister a student from an activity."""
    # Validate activity exists
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=400,
            detail="User not found"
        )
    
    # Validate user is signed up
    if user not in activity.participants:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )
    
    # Remove user from activity
    activity.participants.remove(user)
    db.commit()
    
