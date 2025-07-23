from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
from pathlib import Path
import requests
import base64

app = Flask(__name__)
CORS(app)

# Configuration
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
PROBLEMS_FILE = DATA_DIR / "problems.json"
CONFIG_FILE = DATA_DIR / "config.json"

class DSATracker:
    def __init__(self):
        self.problems = self.load_problems()
        self.config = self.load_config()
    
    def load_problems(self):
        if PROBLEMS_FILE.exists():
            with open(PROBLEMS_FILE, 'r') as f:
                return json.load(f)
        return {"problems": [], "stats": {"total": 0, "solved": 0}}
    
    def save_problems(self):
        with open(PROBLEMS_FILE, 'w') as f:
            json.dump(self.problems, f, indent=2)
    
    def load_config(self):
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)

# Global tracker instance
tracker = DSATracker()

@app.route('/')
def serve_frontend():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/problems', methods=['GET'])
def get_problems():
    """Get all problems with optional filtering"""
    problems = tracker.problems["problems"]
    
    # Apply filters if provided
    difficulty = request.args.get('difficulty')
    platform = request.args.get('platform')
    category = request.args.get('category')
    search = request.args.get('search', '').lower()
    
    if difficulty:
        problems = [p for p in problems if p['difficulty'] == difficulty]
    if platform:
        problems = [p for p in problems if p['platform'] == platform]
    if category:
        problems = [p for p in problems if p['category'] == category]
    if search:
        problems = [p for p in problems if 
                   search in p['name'].lower() or 
                   search in p['category'].lower() or 
                   search in p['platform'].lower()]
    
    return jsonify({
        "problems": problems,
        "total": len(problems)
    })

@app.route('/api/problems', methods=['POST'])
def add_problem():
    """Add a new problem"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'platform', 'difficulty', 'category']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    problem = {
        "id": len(tracker.problems["problems"]) + 1,
        "name": data['name'],
        "platform": data['platform'],
        "difficulty": data['difficulty'].lower(),
        "category": data['category'],
        "status": "solved",
        "date_solved": datetime.now().isoformat(),
        "solution_path": data.get('solution_path'),
        "notes": data.get('notes', ''),
        "attempts": 1
    }
    
    tracker.problems["problems"].append(problem)
    tracker.problems["stats"]["total"] += 1
    tracker.problems["stats"]["solved"] += 1
    tracker.save_problems()
    
    return jsonify({"message": "Problem added successfully", "problem": problem}), 201

@app.route('/api/problems/<int:problem_id>', methods=['DELETE'])
def delete_problem(problem_id):
    """Delete a problem"""
    problems = tracker.problems["problems"]
    problem_index = None
    
    for i, problem in enumerate(problems):
        if problem['id'] == problem_id:
            problem_index = i
            break
    
    if problem_index is None:
        return jsonify({"error": "Problem not found"}), 404
    
    deleted_problem = problems.pop(problem_index)
    tracker.problems["stats"]["total"] -= 1
    tracker.problems["stats"]["solved"] -= 1
    tracker.save_problems()
    
    return jsonify({"message": "Problem deleted successfully", "problem": deleted_problem})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics"""
    problems = tracker.problems["problems"]
    
    # Calculate statistics
    stats = {
        "total": len(problems),
        "difficulty": {"easy": 0, "medium": 0, "hard": 0},
        "categories": {},
        "platforms": {},
        "recent_problems": []
    }
    
    for problem in problems:
        # Difficulty stats
        if problem['difficulty'] in stats["difficulty"]:
            stats["difficulty"][problem['difficulty']] += 1
        
        # Category stats
        category = problem['category']
        stats["categories"][category] = stats["categories"].get(category, 0) + 1
        
        # Platform stats
        platform = problem['platform']
        stats["platforms"][platform] = stats["platforms"].get(platform, 0) + 1
    
    # Recent problems (last 10)
    recent = sorted(problems, key=lambda x: x["date_solved"], reverse=True)[:10]
    stats["recent_problems"] = recent
    
    return jsonify(stats)

@app.route('/api/github/setup', methods=['POST'])
def setup_github():
    """Setup GitHub configuration"""
    data = request.get_json()
    
    required_fields = ['username', 'token', 'repo']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    tracker.config["github"] = {
        "username": data['username'],
        "token": data['token'],
        "repo": data['repo']
    }
    tracker.save_config()
    
    return jsonify({"message": "GitHub configuration saved successfully"})

@app.route('/api/github/sync', methods=['POST'])
def sync_to_github():
    """Sync problems to GitHub"""
    if "github" not in tracker.config:
        return jsonify({"error": "GitHub not configured"}), 400
    
    github_config = tracker.config["github"]
    
    try:
        # Generate README content
        readme_content = generate_readme(tracker.problems)
        
        # Create problems JSON for repo
        repo_data = {
            "last_updated": datetime.now().isoformat(),
            "problems": tracker.problems["problems"],
            "statistics": tracker.problems["stats"]
        }
        
        # Ensure repo exists
        ensure_github_repo(github_config)
        
        # Update files
        update_github_file(github_config, "README.md", readme_content, "Update README with latest problems")
        update_github_file(github_config, "problems.json", json.dumps(repo_data, indent=2), "Update problems data")
        
        return jsonify({"message": "Successfully synced to GitHub!"})
        
    except Exception as e:
        return jsonify({"error": f"Failed to sync to GitHub: {str(e)}"}), 500

@app.route('/api/export', methods=['GET'])
def export_data():
    """Export all data as JSON"""
    export_data = {
        "problems": tracker.problems["problems"],
        "export_date": datetime.now().isoformat(),
        "total_problems": len(tracker.problems["problems"])
    }
    
    return jsonify(export_data)

@app.route('/api/import', methods=['POST'])
def import_data():
    """Import data from JSON"""
    data = request.get_json()
    
    if not data or 'problems' not in data:
        return jsonify({"error": "Invalid data format"}), 400
    
    if not isinstance(data['problems'], list):
        return jsonify({"error": "Problems must be an array"}), 400
    
    # Add imported problems
    imported_count = 0
    for problem in data['problems']:
        # Validate problem structure
        required_fields = ['name', 'platform', 'difficulty', 'category']
        if all(field in problem for field in required_fields):
            problem['id'] = len(tracker.problems["problems"]) + 1
            tracker.problems["problems"].append(problem)
            imported_count += 1
    
    # Update stats
    tracker.problems["stats"]["total"] = len(tracker.problems["problems"])
    tracker.problems["stats"]["solved"] = len(tracker.problems["problems"])
    tracker.save_problems()
    
    return jsonify({
        "message": f"Successfully imported {imported_count} problems",
        "imported_count": imported_count
    })

def generate_readme(problems_data):
    """Generate README content for GitHub repo"""
    stats = problems_data["stats"]
    problems = problems_data["problems"]
    
    # Count by difficulty and category
    difficulty_count = {"easy": 0, "medium": 0, "hard": 0}
    category_count = {}
    platform_count = {}
    
    for p in problems:
        diff = p["difficulty"]
        cat = p["category"]
        plat = p["platform"]
        
        if diff in difficulty_count:
            difficulty_count[diff] += 1
        category_count[cat] = category_count.get(cat, 0) + 1
        platform_count[plat] = platform_count.get(plat, 0) + 1
    
    readme = f"""# 🚀 DSA Problem Tracker

## 📊 Statistics
- **Total Problems Solved:** {stats['solved']}
- **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 Problems by Difficulty
"""
    
    for diff, count in difficulty_count.items():
        emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(diff, "⚪")
        readme += f"- {emoji} {diff.title()}: {count}\n"
    
    readme += f"""
## 📚 Problems by Category
"""
    for cat, count in sorted(category_count.items()):
        readme += f"- {cat}: {count}\n"
    
    readme += f"""
## 🌐 Problems by Platform
"""
    for plat, count in sorted(platform_count.items()):
        readme += f"- {plat}: {count}\n"
    
    readme += f"""
## 📝 Recent Problems
| Problem | Platform | Difficulty | Category | Date |
|---------|----------|------------|----------|------|
"""
    
    # Show last 10 problems
    recent_problems = sorted(problems, key=lambda x: x["date_solved"], reverse=True)[:10]
    
    for p in recent_problems:
        date = datetime.fromisoformat(p["date_solved"]).strftime('%Y-%m-%d')
        diff_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(p["difficulty"], "⚪")
        readme += f"| {p['name']} | {p['platform']} | {diff_emoji} {p['difficulty'].title()} | {p['category']} | {date} |\n"
    
    readme += f"""
---
*Generated by DSA Tracker*
"""
    
    return readme

def ensure_github_repo(config):
    """Ensure GitHub repository exists"""
    headers = {
        "Authorization": f"token {config['token']}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Check if repo exists
    repo_url = f"https://api.github.com/repos/{config['username']}/{config['repo']}"
    response = requests.get(repo_url, headers=headers)
    
    if response.status_code == 404:
        # Create repository
        create_url = "https://api.github.com/user/repos"
        repo_data = {
            "name": config['repo'],
            "description": "My DSA problem tracking repository",
            "private": False,
            "auto_init": True
        }
        
        response = requests.post(create_url, headers=headers, json=repo_data)
        if response.status_code != 201:
            raise Exception(f"Failed to create repository: {response.text}")

def update_github_file(config, filename, content, message):
    """Update a file in GitHub repository"""
    headers = {
        "Authorization": f"token {config['token']}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Get current file (if exists) to get SHA
    file_url = f"https://api.github.com/repos/{config['username']}/{config['repo']}/contents/{filename}"
    response = requests.get(file_url, headers=headers)
    
    encoded_content = base64.b64encode(content.encode()).decode()
    
    data = {
        "message": message,
        "content": encoded_content
    }
    
    if response.status_code == 200:
        # File exists, need SHA for update
        data["sha"] = response.json()["sha"]
    
    response = requests.put(file_url, headers=headers, json=data)
    if response.status_code not in [200, 201]:
        raise Exception(f"Failed to update {filename}: {response.text}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)