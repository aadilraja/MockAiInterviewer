import cv2
import whisper
from deepface import DeepFace
import json
import ollama
from flask import current_app
from collections import Counter

print("[⚙️] Loading Whisper model... (This takes a few seconds)")
whisper_model = whisper.load_model("base")
print("[✅] Whisper model loaded!")

def analyze_video(video_path):
    """
    Analyzes a video chunk using OpenCV for face presence and DeepFace for emotion.
    """
    print(f"[👁️] Starting Vision Analysis on {video_path}")
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"[❌] Error opening video stream: {video_path}")
        return {"dominant_emotion": "neutral", "eye_contact_percentage": 0, "emotion_breakdown": {}}

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or fps != fps: # Catch 0 or NaN
        fps = 30 
    
    # 👈 Use OpenCV's built-in, highly stable face detector
    face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    
    emotions = []
    frames_with_face = 0
    total_sampled_frames = 0
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        
        # Analyze 1 frame per second to save CPU
        if frame_count % int(fps) == 0:
            total_sampled_frames += 1
            
            # 1. OpenCV: Check if they are looking at the camera
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # detectMultiScale returns a list of rectangles where it found faces
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            if len(faces) > 0:
                frames_with_face += 1
            
            # 2. DeepFace: Check their emotion
            try:
                analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False, silent=True)
                result = analysis[0] if isinstance(analysis, list) else analysis
                emotions.append(result['dominant_emotion'])
            except Exception as e:
                pass

    cap.release()
    
    # Calculate Results
    eye_contact_score = (frames_with_face / total_sampled_frames) * 100 if total_sampled_frames > 0 else 0
    dominant_emotion = Counter(emotions).most_common(1)[0][0] if emotions else "neutral"

    return {
        "dominant_emotion": dominant_emotion,
        "eye_contact_percentage": round(eye_contact_score, 2),
        "emotion_breakdown": dict(Counter(emotions))
    }

def analyze_audio(audio_path):
    """
    Transcribes the audio file into text using OpenAI Whisper.
    """
    if not audio_path:
        return {"transcript": "", "error": "No audio file provided"}

    print(f"[👂] Starting Audio Transcription on {audio_path}")
    
    try:
        result = whisper_model.transcribe(audio_path)
        transcript = result["text"].strip()
        
        return {
            "transcript": transcript,
            "filler_words_count": transcript.lower().count(" um ") + transcript.lower().count(" uh ")
        }
    except Exception as e:
        print(f"[❌] Whisper Error: {e}")
        return {"transcript": "", "error": str(e)}

def evaluate_answer(question_text, transcript):
    """
    Feeds the transcribed answer and the original question to Ollama.
    Extracts both a holistic 1-10 score and a strict technical concept breakdown.
    """
    if not transcript or len(transcript.strip()) < 5:
        return {
            "holistic_score": 0,
            "expected_concepts": [],
            "hit_concepts": [],
            "missing_concepts": [],
            "feedback": "No audible answer was provided.",
            "strengths": [],
            "improvements": ["Please ensure your microphone is working and speak clearly."]
        }

    print(f"[🧠] Asking Ollama to grade the answer and extract key concepts...")

    prompt = f"""
You are a strict but fair engineering manager conducting a technical placement interview.

Question Asked: "{question_text}"
Candidate's Answer: "{transcript}"

INSTRUCTIONS:
1. Identify 3 to 5 core technical concepts, keywords, or algorithms that a perfect answer to this question MUST include.
2. Evaluate the candidate's transcript to see how many of those specific concepts they successfully mentioned or clearly explained.
3. Grade their overall communication, clarity, and problem-solving approach on a scale of 1 to 10.

You MUST return EXACTLY a valid JSON object. No markdown, no conversational text.

Return exactly this JSON format:
{{
  "holistic_score": 8,
  "expected_concepts": ["concept 1", "concept 2", "concept 3"],
  "hit_concepts": ["concept 1"],
  "missing_concepts": ["concept 2", "concept 3"],
  "feedback": "Overall evaluation of their technical depth and delivery.",
  "strengths": ["strength 1", "strength 2"],
  "improvements": ["area to improve 1", "area to improve 2"]
}}
    """.strip()

    try:
        response = ollama.chat(
            model=current_app.config.get("OLLAMA_MODEL", "llama3"),
            messages=[{"role": "user", "content": prompt}],
            format="json",
            options={"temperature": 0.2, "num_predict": 700} # Lowered temp for strict, factual grading
        )

        raw_output = response["message"]["content"].strip()
        evaluation = json.loads(raw_output)
        
        hit_count = len(evaluation.get('hit_concepts', []))
        total_count = len(evaluation.get('expected_concepts', []))
        
        print(f"[✅] Graded! Score: {evaluation.get('holistic_score')}/10 | Concepts Hit: {hit_count}/{total_count}")
        return evaluation

    except Exception as e:
        print(f"[❌] Failed to grade answer: {e}")
        return {
            "holistic_score": None,
            "expected_concepts": [],
            "hit_concepts": [],
            "missing_concepts": [],
            "feedback": "AI grading failed to process the transcript.",
            "strengths": [],
            "improvements": []
        }