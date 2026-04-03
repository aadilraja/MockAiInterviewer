import os
import traceback
from werkzeug.utils import secure_filename
from flask import current_app
from models import db, InterviewAnswer
from moviepy import VideoFileClip

from AnalysisService import analyze_video, analyze_audio,evaluate_answer

def save_video_chunk_logic(form, files):
    """
    Saves a video chunk sent from the frontend into a session-specific folder,
    and automatically extracts the audio into a separate .wav file.
    """
    try:
        video_file = files.get('video')
        question_id = form.get('question_id')
        session_id = form.get('session_id')
        question_text = form.get('question_text', 'Unknown Question') 
        user_id = form.get('user_id')

        # 1. Validate inputs (Returns dict, 400 Bad Request)
        if not all([video_file, question_id, session_id]):
            return {"error": "Missing video, question_id, or session_id"}, 400

        # 2. Define Folder Hierarchy
        session_dir = os.path.join(current_app.root_path, "uploads", "sessions", str(session_id))
        video_dir = os.path.join(session_dir, "video")
        audio_dir = os.path.join(session_dir, "audio")
        
        # Ensure the directories exist
        os.makedirs(video_dir, exist_ok=True)
        os.makedirs(audio_dir, exist_ok=True)

        # 3. Sanitize and build file paths
        safe_filename = secure_filename(video_file.filename)
        if not safe_filename:
            safe_filename = f"q_{question_id}.webm"
            
        video_path = os.path.join(video_dir, safe_filename)
        
        # Create matching audio filename (replace .webm with .wav)
        audio_filename = safe_filename.rsplit('.', 1)[0] + '.wav'
        audio_path = os.path.join(audio_dir, audio_filename)

        # 4. Save the video to the disk
        video_file.save(video_path)

        print(f"\n[💾] Saved Video Chunk:")
        print(f"     Session  : {session_id}")
        print(f"     Question : {question_id}")
        print(f"     Video    : {video_path}")

        # 5. Extract and save the audio
        try:
            print(f"[🎵] Extracting audio...")
            video_clip = VideoFileClip(video_path)
            
            # Check if the video actually has an audio track
            if video_clip.audio is not None:
                video_clip.audio.write_audiofile(
                    audio_path, 
                    codec='pcm_s16le', # Standard 16-bit WAV (Perfect for Whisper/ML)
                 
                )
                print(f"[✅] Audio saved : {audio_path}\n")
            else:
                audio_path = None
                print(f"[⚠️] No audio track found in the video chunk.\n")
                
            video_clip.close() # Free up memory
            
        except Exception as e:
            print(f"[❌] Failed to extract audio: {e}")
            traceback.print_exc()
            audio_path = None # We still return success for the video even if audio fails

        # ---------------------------------------------------------
        # 🤖 ML INTEGRATION POINT
        # ---------------------------------------------------------
        print("\n--- Starting ML Analysis ---")
        
        # 1. Run Vision Analysis
        video_metrics = analyze_video(video_path)
        print(f"[📊] Vision Results: {video_metrics}")
        
        # 2. Run Audio Analysis
        audio_metrics = analyze_audio(audio_path)
        print(f"[📝] Transcript: {audio_metrics['transcript']}")
        
   
       # 3. Grade the Answer using Ollama!
        ai_grading = evaluate_answer(question_text, audio_metrics['transcript'])
        
        # ---------------------------------------------------------
        # 💾 DATABASE INTEGRATION POINT
        # ---------------------------------------------------------
        print("[💾] Saving AI results to database...")
        
        new_answer = InterviewAnswer(
            session_id=str(session_id),
            user_id=str(user_id),
            question_id=str(question_id),
            question_text=question_text,
            video_path=video_path,
            audio_path=audio_path,
            
            transcript=audio_metrics['transcript'],
            eye_contact_percentage=video_metrics['eye_contact_percentage'],
            dominant_emotion=video_metrics['dominant_emotion'],
            
            holistic_score=ai_grading.get('holistic_score', 0),
            feedback=ai_grading.get('feedback', ''),
            expected_concepts=ai_grading.get('expected_concepts', []),
            hit_concepts=ai_grading.get('hit_concepts', []),
            missing_concepts=ai_grading.get('missing_concepts', []),
            strengths=ai_grading.get('strengths', []),
            improvements=ai_grading.get('improvements', [])
        )
        
        db.session.add(new_answer)
        db.session.commit()
        
        print("[✅] Saved successfully to DB!")
        print("----------------------------\n")

        # 6. Return success
        return new_answer.to_dict(),201

     

    except Exception as e:
        traceback.print_exc()
        return {"error": f"Failed to save media: {str(e)}"}, 500