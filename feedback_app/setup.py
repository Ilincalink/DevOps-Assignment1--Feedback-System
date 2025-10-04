from models import FeedbackModel

import os


def setup_database():
    """Initialise the dbase and create sample data for some tests."""
    print("Setting up the feedback database...")
    
    feedback_model = FeedbackModel()
    
    # sample feedback 
    sample_feedback = [
        {
            "user": "ilinca",
            "comment": "Great! Very enice."
        },
        {
            "user": "John", 
            "comment": "I love it."
        },
        {
            "user": "mcDonalds",
            "comment": "I'm lovin' it."
        }
    ]
    
    # Check database already has data
    existing_feedback = feedback_model.read_all()
    
    if not existing_feedback:
        print("Adding sample feedback data...")
        for feedback in sample_feedback:
            feedback_model.create(feedback)
        print(f"Added {len(sample_feedback)} sample feedback entries.")
    else:
        print(f"Database already has {len(existing_feedback)} feedback entries.")
    
    print("Database setup complete!")
    

def main():
    """Main setup function."""
    print("=" * 50)
    print("  FEEDBACK APPLICATION SETUP")
    print("=" * 50)
    
    setup_database()
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nTo run the application:")
    print("1. Activate your virtual environment")
    print("2. Run: python app.py")
    print("3. Open http://localhost:5001 in your browser")
    print("=" * 50)


if __name__ == "__main__":
    main()
