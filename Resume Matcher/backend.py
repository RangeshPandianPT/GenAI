"""
Flask Backend for Resume Matcher
Provides API endpoints for resume-job matching
"""
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import json
import traceback
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime

from config import get_api_config, validate_config
from resume_processor import process_resume, process_multiple_resumes, extract_text_from_pdf
from job_processor import process_job_description
from skill_extractor import extract_skills, extract_job_requirements, calculate_skill_match
from matcher import match_multiple_resumes, get_match_summary

app = Flask(__name__, static_folder='static')
CORS(app)

# Configuration
UPLOAD_FOLDER_RESUMES = 'uploads/resumes'
UPLOAD_FOLDER_JOBS = 'uploads/jobs'
DATA_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(UPLOAD_FOLDER_RESUMES, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_JOBS, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER_RESUMES'] = UPLOAD_FOLDER_RESUMES
app.config['UPLOAD_FOLDER_JOBS'] = UPLOAD_FOLDER_JOBS
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Validate configuration
try:
    validate_config()
    config = get_api_config()
except Exception as e:
    print(f"⚠️ Configuration error: {e}")
    config = None

# In-memory storage for current session
session_data = {
    "resumes": [],
    "job": None,
    "job_requirements": None,
    "match_results": None
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


@app.route('/api/config', methods=['GET'])
def get_config_endpoint():
    """Get current API configuration"""
    if config:
        return jsonify({
            "success": True,
            "api_type": config["api_type"],
            "embedding_model": config.get("embedding_model", ""),
            "chat_model": config.get("chat_model", "")
        })
    else:
        return jsonify({"success": False, "error": "Configuration not loaded"}), 500


@app.route('/api/status', methods=['GET'])
def check_status():
    """Check system status"""
    return jsonify({
        "success": True,
        "resumes_loaded": len(session_data["resumes"]),
        "job_loaded": session_data["job"] is not None,
        "has_results": session_data["match_results"] is not None
    })


@app.route('/api/upload/resume', methods=['POST'])
def upload_resume():
    """Upload one or more resume PDFs"""
    if 'files' not in request.files and 'file' not in request.files:
        return jsonify({"success": False, "error": "No files provided"}), 400
    
    # Handle both single and multiple file uploads
    files = request.files.getlist('files') or [request.files.get('file')]
    files = [f for f in files if f and f.filename]
    
    if not files:
        return jsonify({"success": False, "error": "No valid files provided"}), 400
    
    results = []
    saved_paths = []
    
    for file in files:
        if not allowed_file(file.filename):
            results.append({
                "filename": file.filename,
                "success": False,
                "error": "Only PDF files are allowed"
            })
            continue
        
        try:
            filename = secure_filename(file.filename)
            # Add timestamp to avoid overwrites
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER_RESUMES, unique_filename)
            file.save(filepath)
            saved_paths.append(filepath)
            
            results.append({
                "filename": filename,
                "saved_as": unique_filename,
                "success": True
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
    
    # Process uploaded resumes
    if saved_paths:
        try:
            processed = process_multiple_resumes(saved_paths, config)
            session_data["resumes"].extend(processed)
            
            return jsonify({
                "success": True,
                "message": f"Uploaded {len(saved_paths)} resume(s)",
                "results": results,
                "total_resumes": len(session_data["resumes"])
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Processing error: {str(e)}",
                "results": results
            }), 500
    
    return jsonify({
        "success": False,
        "error": "No files were saved",
        "results": results
    }), 400


@app.route('/api/upload/job', methods=['POST'])
def upload_job():
    """Upload a job description PDF"""
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file provided"}), 400
    
    file = request.files['file']
    
    if not file or not file.filename:
        return jsonify({"success": False, "error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Only PDF files are allowed"}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER_JOBS, filename)
        file.save(filepath)
        
        # Process job description
        job_data = process_job_description(filepath, config, is_file=True)
        
        if job_data["success"]:
            session_data["job"] = job_data
            
            # Extract job requirements
            requirements = extract_job_requirements(job_data["text"], config)
            session_data["job_requirements"] = requirements
            
            return jsonify({
                "success": True,
                "message": "Job description uploaded and processed",
                "filename": filename,
                "char_count": job_data["char_count"],
                "requirements": requirements
            })
        else:
            return jsonify(job_data), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route('/api/job/text', methods=['POST'])
def submit_job_text():
    """Submit job description as text"""
    data = request.get_json()
    job_text = data.get('text', '').strip()
    
    if not job_text:
        return jsonify({"success": False, "error": "No job description provided"}), 400
    
    try:
        # Process job description
        job_data = process_job_description(job_text, config, is_file=False)
        
        if job_data["success"]:
            session_data["job"] = job_data
            
            # Extract job requirements
            requirements = extract_job_requirements(job_text, config)
            session_data["job_requirements"] = requirements
            
            return jsonify({
                "success": True,
                "message": "Job description processed",
                "char_count": job_data["char_count"],
                "requirements": requirements
            })
        else:
            return jsonify(job_data), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route('/api/match', methods=['POST'])
def run_matching():
    """Run matching between uploaded resumes and job description"""
    if not session_data["resumes"]:
        return jsonify({"success": False, "error": "No resumes uploaded"}), 400
    
    if not session_data["job"]:
        return jsonify({"success": False, "error": "No job description provided"}), 400
    
    try:
        # Calculate skill matches for each resume
        skill_matches = []
        job_requirements = session_data["job_requirements"]
        
        for resume in session_data["resumes"]:
            if resume.get("success"):
                # Extract skills from resume
                resume_skills = extract_skills(resume["text"], config)
                # Calculate skill match
                skill_match = calculate_skill_match(resume_skills, job_requirements)
                skill_match["extracted_skills"] = resume_skills
                skill_matches.append(skill_match)
            else:
                skill_matches.append(None)
        
        # Run semantic matching
        results = match_multiple_resumes(
            session_data["resumes"],
            session_data["job"],
            skill_matches
        )
        
        # Get summary
        summary = get_match_summary(results)
        
        session_data["match_results"] = results
        
        return jsonify({
            "success": True,
            "results": results,
            "summary": summary
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route('/api/resumes', methods=['GET'])
def get_resumes():
    """Get list of uploaded resumes"""
    resumes = []
    for r in session_data["resumes"]:
        resumes.append({
            "filename": r.get("filename", "Unknown"),
            "success": r.get("success", False),
            "char_count": r.get("char_count", 0),
            "error": r.get("error", None)
        })
    
    return jsonify({
        "success": True,
        "resumes": resumes,
        "total": len(resumes)
    })


@app.route('/api/resumes/clear', methods=['POST'])
def clear_resumes():
    """Clear all uploaded resumes"""
    session_data["resumes"] = []
    session_data["match_results"] = None
    
    return jsonify({
        "success": True,
        "message": "All resumes cleared"
    })


@app.route('/api/job/clear', methods=['POST'])
def clear_job():
    """Clear the job description"""
    session_data["job"] = None
    session_data["job_requirements"] = None
    session_data["match_results"] = None
    
    return jsonify({
        "success": True,
        "message": "Job description cleared"
    })


@app.route('/api/skills/extract', methods=['POST'])
def extract_skills_endpoint():
    """Extract skills from provided text"""
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({"success": False, "error": "No text provided"}), 400
    
    try:
        skills = extract_skills(text, config)
        return jsonify({
            "success": True,
            "skills": skills
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/results/export', methods=['GET'])
def export_results():
    """Export match results as CSV or JSON"""
    format_type = request.args.get('format', 'json')
    
    if not session_data["match_results"]:
        return jsonify({"success": False, "error": "No results to export"}), 400
    
    try:
        results = session_data["match_results"]
        
        if format_type == 'csv':
            # Prepare data for CSV
            csv_data = []
            for r in results:
                csv_data.append({
                    "Rank": r.get("rank", "N/A"),
                    "Resume": r.get("resume_filename", "Unknown"),
                    "Final Score": r.get("final_score", 0),
                    "Semantic Score": r.get("semantic_score", 0),
                    "Skill Score": r.get("skill_score", 0),
                    "Required Skills Matched": len(r.get("skill_details", {}).get("required_matches", [])),
                    "Required Skills Missing": len(r.get("skill_details", {}).get("required_missing", []))
                })
            
            df = pd.DataFrame(csv_data)
            csv_path = os.path.join(DATA_FOLDER, "match_results.csv")
            df.to_csv(csv_path, index=False)
            
            return send_file(csv_path, as_attachment=True, download_name="match_results.csv")
        
        else:
            # Return JSON
            json_path = os.path.join(DATA_FOLDER, "match_results.json")
            with open(json_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            return send_file(json_path, as_attachment=True, download_name="match_results.json")
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🎯 Resume Matcher - Backend Server")
    print("=" * 60)
    if config:
        print(f"✓ API Type: {config['api_type'].upper()}")
        print(f"✓ Embedding Model: {config.get('embedding_model', 'N/A')}")
        print(f"✓ Chat Model: {config.get('chat_model', 'N/A')}")
    print(f"✓ Server: http://localhost:5001")
    print("=" * 60)
    print("\n🌐 Open http://localhost:5001 in your browser\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
