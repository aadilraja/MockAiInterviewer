from database import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Stats(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   full_name = db.Column(db.String(100), nullable=False)

class InterviewSession(db.Model):
    __tablename__ = "interview_sessions"
 
    id            = db.Column(db.String(36), primary_key=True)   # uuid
    document_choice = db.Column(db.String(10))                   # resume | jd | both
    settings      = db.Column(db.JSON)                           # interviewSettings dict
    questions     = db.Column(db.JSON)                           # generated questions array
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
 
    def to_dict(self):
        return {
            "session_id":      self.id,
            "document_choice": self.document_choice,
            "settings":        self.settings,
            "questions":       self.questions,
            "created_at":      self.created_at.isoformat(),
        }

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Assuming you already have your db initialized like: db = SQLAlchemy()

class InterviewAnswer(db.Model):
    __tablename__ = 'interview_answers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False, index=True)
    session_id = db.Column(db.String(100), nullable=False, index=True)
    question_id = db.Column(db.String(100), nullable=False)
    question_text = db.Column(db.Text, nullable=True)
    
    # File Paths
    video_path = db.Column(db.String(255), nullable=True)
    audio_path = db.Column(db.String(255), nullable=True)
    
    # Audio & Vision AI
    transcript = db.Column(db.Text, nullable=True)
    eye_contact_percentage = db.Column(db.Float, default=0.0)
    dominant_emotion = db.Column(db.String(50), default="neutral")
    
    # Ollama AI Grading
    holistic_score = db.Column(db.Integer, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    expected_concepts = db.Column(db.JSON, nullable=True) # Stores list of strings
    hit_concepts = db.Column(db.JSON, nullable=True)      # Stores list of strings
    missing_concepts = db.Column(db.JSON, nullable=True)  # Stores list of strings
    strengths = db.Column(db.JSON, nullable=True)         # Stores list of strings
    improvements = db.Column(db.JSON, nullable=True)      # Stores list of strings
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Helper function to easily send this data back to React"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "question_id": self.question_id,
            "original_question": self.question_text,
            "analysis": {
                "vision": {
                    "eye_contact_percentage": self.eye_contact_percentage,
                    "dominant_emotion": self.dominant_emotion
                },
                "speech": {
                    "transcript": self.transcript
                },
                "grading": {
                    "holistic_score": self.holistic_score,
                    "feedback": self.feedback,
                    "expected_concepts": self.expected_concepts or [],
                    "hit_concepts": self.hit_concepts or [],
                    "missing_concepts": self.missing_concepts or [],
                    "strengths": self.strengths or [],
                    "improvements": self.improvements or []
                }
            }
        }