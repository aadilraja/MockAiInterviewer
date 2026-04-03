from flask import Blueprint, request, jsonify
from auth_service import register_user_logic, login_user_logic
from dashboard_service import user_dashBoard_logic
from interviewSetup import generate_questions_logic, get_session_logic, ollama_health_logic
from InterviewService import save_video_chunk_logic
from HealthService import get_health
from sqlalchemy import func 
from models import db, InterviewAnswer 


auth_bp      = Blueprint('auth', __name__)
users_bp     = Blueprint('users', __name__)
interview_bp = Blueprint('interview', __name__)
health_bp = Blueprint('health',__name__)





# ─── Auth ─────────────────────────────────────────────────────────────────────

@auth_bp.route('/register', methods=['POST'])
def register():
    response, status = register_user_logic(request.json)
    return jsonify(response), status


@auth_bp.route('/login', methods=['POST'])
def login():
    response, status = login_user_logic(request.json)
    return jsonify(response), status


# ─── Users ────────────────────────────────────────────────────────────────────

@users_bp.route('/<userId>', methods=['GET'])
def userDashBoard(userId):
    response, status = user_dashBoard_logic(int(userId))
    return jsonify(response), status


# ─── Interview ────────────────────────────────────────────────────────────────

@interview_bp.route('/generate-questions', methods=['POST'])
def generateQuestions():
    response, status = generate_questions_logic(
        raw_settings    = request.form.get("settings", "{}"),
        document_choice = request.form.get("document_choice", "both"),
        files           = request.files,         # ← pass the uploaded files
    )
    return jsonify(response), status


@interview_bp.route('/session/<session_id>', methods=['GET'])
def getSession(session_id):
    response, status = get_session_logic(session_id)
    return jsonify(response), status


@interview_bp.route('/ollama-health', methods=['GET'])
def ollamaHealth():
    response, status = ollama_health_logic()
    return jsonify(response), status

@health_bp.route('/health',methods=['GET'])
def getHealth():
    response,status=get_health()
    return jsonify(response), status

@interview_bp.route('/upload-answer', methods=['POST'])
def saveVideoChunkLogic():
    response,status=save_video_chunk_logic(request.form, request.files)
    return jsonify(response), status




@interview_bp.route('/results/<session_id>', methods=['GET'])
def get_session_results(session_id):
    try:
        # Query the database for all answers tied to this specific interview session
        answers = InterviewAnswer.query.filter_by(session_id=session_id).all()
        
        if not answers:
            return jsonify({"error": "No results found for this session."}), 404
            
        # Convert the SQL objects into JSON dictionaries using our helper function
        results_data = [answer.to_dict() for answer in answers]
        
        return jsonify({"results": results_data}), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch results: {str(e)}"}), 500
    


@interview_bp.route('/history/<user_id>', methods=['GET'])
def get_user_history(user_id):
    """
    Fetches a summarized list of all interview sessions completed by a specific user.
    """
    try:
        # Group answers by session_id to get a list of unique sessions.
        # We calculate the average score and count how many questions they answered in that session.
        history = db.session.query(
            InterviewAnswer.session_id,
            func.avg(InterviewAnswer.holistic_score).label('avg_score'),
            func.count(InterviewAnswer.id).label('questions_answered'),
            func.max(InterviewAnswer.created_at).label('created_at') # Get the latest date
        ).filter(InterviewAnswer.user_id == str(user_id)) \
         .group_by(InterviewAnswer.session_id) \
         .order_by(func.max(InterviewAnswer.created_at).desc()).all()

        sessions_data = []
        for row in history:
            sessions_data.append({
                "session_id": row.session_id,
                # Round the average score to 1 decimal place (e.g., 8.5), default to 0 if None
                "avg_score": round(row.avg_score, 1) if row.avg_score is not None else 0,
                "questions_answered": row.questions_answered,
                # Format the date so React can easily read it
                "created_at": row.created_at.isoformat() if row.created_at else None
            })

        return jsonify({"sessions": sessions_data}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch user history: {str(e)}"}), 500