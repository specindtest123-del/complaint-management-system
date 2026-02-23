// Check login status on page load
document.addEventListener('DOMContentLoaded', function() {
    checkLoginStatus();
    
    // Login form handler
    document.getElementById('loginForm').addEventListener('submit', function(e) {
        e.preventDefault();
        login();
    });
    
    // Register form handler
    document.getElementById('registerForm').addEventListener('submit', function(e) {
        e.preventDefault();
        register();
    });
    
    // Complaint form handler
    document.getElementById('newComplaintForm').addEventListener('submit', function(e) {
        e.preventDefault();
        submitComplaint();
    });
});

function checkLoginStatus() {
    // You can implement session check here
}

function login() {
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.is_admin) {
                window.location.href = '/admin';
            } else {
                document.getElementById('complaintForm').style.display = 'block';
                document.querySelector('.card:first-child').style.display = 'none';
            }
        } else {
            showMessage('danger', data.message);
        }
    });
}

function register() {
    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    
    fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('success', 'Registration successful! Please login.');
            // Switch to login tab
            document.getElementById('login-tab').click();
        } else {
            showMessage('danger', data.message);
        }
    });
}

function submitComplaint() {
    const title = document.getElementById('complaintTitle').value;
    const category = document.getElementById('complaintCategory').value;
    const description = document.getElementById('complaintDescription').value;
    
    fetch('/api/complaints', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, category, description })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('success', 
                `Complaint submitted successfully! ID: ${data.complaint_id}<br>
                Sentiment: ${data.sentiment}<br>
                Priority: ${data.priority}`);
            document.getElementById('newComplaintForm').reset();
        } else {
            showMessage('danger', 'Failed to submit complaint');
        }
    });
}

function showMessage(type, text) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `<div class="alert alert-${type}">${text}</div>`;
    setTimeout(() => resultDiv.innerHTML = '', 5000);
}

function logout() {
    fetch('/api/logout')
        .then(() => window.location.href = '/');
}