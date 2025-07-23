// Global variables
let allProblems = [];

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
    loadProblems();
    
    // Setup form submission
    document.getElementById('addProblemForm').addEventListener('submit', addProblem);
});

// Tab switching functionality
function showTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(tab => tab.classList.remove('active'));
    
    // Remove active class from all nav tabs
    const navTabs = document.querySelectorAll('.nav-tab');
    navTabs.forEach(tab => tab.classList.remove('active'));
    
    // Show selected tab content
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked nav tab
    event.target.classList.add('active');
    
    // Load specific tab data
    if (tabName === 'dashboard') {
        loadDashboard();
    } else if (tabName === 'problems') {
        loadProblems();
    }
}

// Load dashboard statistics
async function loadDashboard() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        // Update stat cards
        document.getElementById('totalProblems').textContent = stats.total;
        document.getElementById('easyProblems').textContent = stats.difficulty.easy || 0;
        document.getElementById('mediumProblems').textContent = stats.difficulty.medium || 0;
        document.getElementById('hardProblems').textContent = stats.difficulty.hard || 0;
        
        // Update category stats
        updateCategoryStats(stats.categories);
        
        // Update platform stats
        updatePlatformStats(stats.platforms);
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showMessage('Error loading dashboard data', 'error');
    }
}

// Update category statistics display
function updateCategoryStats(categories) {
    const categoryStats = document.getElementById('categoryStats');
    categoryStats.innerHTML = '';
    
    Object.entries(categories).forEach(([category, count]) => {
        const statItem = document.createElement('div');
        statItem.className = 'stat-item';
        statItem.innerHTML = `
            <span class="stat-name">${category}</span>
            <span class="stat-count">${count}</span>
        `;
        categoryStats.appendChild(statItem);
    });
}

// Update platform statistics display
function updatePlatformStats(platforms) {
    const platformStats = document.getElementById('platformStats');
    platformStats.innerHTML = '';
    
    Object.entries(platforms).forEach(([platform, count]) => {
        const statItem = document.createElement('div');
        statItem.className = 'stat-item';
        statItem.innerHTML = `
            <span class="stat-name">${platform}</span>
            <span class="stat-count">${count}</span>
        `;
        platformStats.appendChild(statItem);
    });
}

// Load all problems
async function loadProblems() {
    try {
        const response = await fetch('/api/problems');
        const data = await response.json();
        allProblems = data.problems;
        displayProblems(allProblems);
    } catch (error) {
        console.error('Error loading problems:', error);
        showMessage('Error loading problems', 'error');
    }
}

// Display problems in the list
function displayProblems(problems) {
    const problemsList = document.getElementById('problemsList');
    
    if (problems.length === 0) {
        problemsList.innerHTML = `
            <div class="empty-state">
                <h3>No problems found</h3>
                <p>Start by adding your first solved problem!</p>
            </div>
        `;
        return;
    }
    
    problemsList.innerHTML = problems.map(problem => `
        <div class="problem-item">
            <div class="problem-header">
                <h4 class="problem-name">${problem.name}</h4>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <span class="problem-platform">${problem.platform}</span>
                    <button class="delete-btn" onclick="deleteProblem(${problem.id})">Delete</button>
                </div>
            </div>
            <div class="problem-details">
                <span class="difficulty-badge difficulty-${problem.difficulty}">${problem.difficulty.toUpperCase()}</span>
                <span class="problem-category">${problem.category}</span>
                <span class="problem-date">${formatDate(problem.date_solved)}</span>
            </div>
            ${problem.notes ? `<div class="problem-notes">"${problem.notes}"</div>` : ''}
        </div>
    `).join('');
}

// Add new problem
async function addProblem(event) {
    event.preventDefault();
    
    const formData = {
        name: document.getElementById('problemName').value,
        platform: document.getElementById('platform').value,
        difficulty: document.getElementById('difficulty').value,
        category: document.getElementById('category').value,
        notes: document.getElementById('notes').value
    };
    
    try {
        const response = await fetch('/api/problems', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage('Problem added successfully!', 'success');
            document.getElementById('addProblemForm').reset();
            loadProblems();
            loadDashboard();
        } else {
            showMessage(result.error || 'Error adding problem', 'error');
        }
    } catch (error) {
        console.error('Error adding problem:', error);
        showMessage('Error adding problem', 'error');
    }
}

// Delete problem
async function deleteProblem(problemId) {
    if (!confirm('Are you sure you want to delete this problem?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/problems/${problemId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage('Problem deleted successfully!', 'success');
            loadProblems();
            loadDashboard();
        } else {
            showMessage(result.error || 'Error deleting problem', 'error');
        }
    } catch (error) {
        console.error('Error deleting problem:', error);
        showMessage('Error deleting problem', 'error');
    }
}

// Filter problems
function filterProblems() {
    const search = document.getElementById('searchInput').value.toLowerCase();
    const difficulty = document.getElementById('difficultyFilter').value;
    const platform = document.getElementById('platformFilter').value;
    const category = document.getElementById('categoryFilter').value;
    
    let filtered = allProblems.filter(problem => {
        const matchesSearch = problem.name.toLowerCase().includes(search) ||
                            problem.category.toLowerCase().includes(search) ||
                            problem.platform.toLowerCase().includes(search);
        
        const matchesDifficulty = !difficulty || problem.difficulty === difficulty;
        const matchesPlatform = !platform || problem.platform === platform;
        const matchesCategory = !category || problem.category === category;
        
        return matchesSearch && matchesDifficulty && matchesPlatform && matchesCategory;
    });
    
    displayProblems(filtered);
}

// GitHub setup
async function setupGithub() {
    const username = document.getElementById('githubUsername').value;
    const token = document.getElementById('githubToken').value;
    const repo = document.getElementById('githubRepo').value;
    
    if (!username || !token || !repo) {
        showMessage('Please fill in all GitHub fields', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/github/setup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, token, repo })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage('GitHub configuration saved successfully!', 'success');
        } else {
            showMessage(result.error || 'Error setting up GitHub', 'error');
        }
    } catch (error) {
        console.error('Error setting up GitHub:', error);
        showMessage('Error setting up GitHub', 'error');
    }
}

// Sync to GitHub
async function syncToGithub() {
    try {
        showMessage('Syncing to GitHub...', 'success');
        
        const response = await fetch('/api/github/sync', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage('Successfully synced to GitHub!', 'success');
        } else {
            showMessage(result.error || 'Error syncing to GitHub', 'error');
        }
    } catch (error) {
        console.error('Error syncing to GitHub:', error);
        showMessage('Error syncing to GitHub', 'error');
    }
}

// Export data
async function exportData() {
    try {
        const response = await fetch('/api/export');
        const data = await response.json();
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `dsa-problems-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showMessage('Data exported successfully!', 'success');
    } catch (error) {
        console.error('Error exporting data:', error);
        showMessage('Error exporting data', 'error');
    }
}

// Import data
async function importData() {
    const fileInput = document.getElementById('importFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showMessage('Please select a file to import', 'error');
        return;
    }
    
    try {
        const text = await file.text();
        const data = JSON.parse(text);
        
        const response = await fetch('/api/import', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage(result.message, 'success');
            loadProblems();
            loadDashboard();
            fileInput.value = '';
        } else {
            showMessage(result.error || 'Error importing data', 'error');
        }
    } catch (error) {
        console.error('Error importing data:', error);
        showMessage('Error importing data. Please check file format.', 'error');
    }
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

function showMessage(message, type) {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    // Insert at top of container
    const container = document.querySelector('.container');
    container.insertBefore(messageDiv, container.firstChild);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}