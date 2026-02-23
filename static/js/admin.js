let complaintsTable;

document.addEventListener('DOMContentLoaded', function() {
    loadComplaints();
});

function loadComplaints() {
    fetch('/api/admin/complaints')
        .then(response => response.json())
        .then(complaints => {
            updateStatistics(complaints);
            
            if (complaintsTable) {
                complaintsTable.destroy();
            }
            
            const tbody = document.querySelector('#complaintsTable tbody');
            tbody.innerHTML = '';
            
            complaints.forEach(c => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${c.id}</td>
                    <td>${c.username}</td>
                    <td>${c.title}</td>
                    <td>${c.category}</td>
                    <td><span class="badge bg-${getSentimentColor(c.sentiment)}">${c.sentiment}</span></td>
                    <td><span class="badge bg-${getPriorityColor(c.priority)}">${c.priority}</span></td>
                    <td><span class="badge bg-${getStatusColor(c.status)}">${c.status}</span></td>
                    <td>${c.assigned_to || 'Unassigned'}</td>
                    <td>${new Date(c.created_at).toLocaleDateString()}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editComplaint(${c.id})">Edit</button>
                    </td>
                `;
            });
            
            complaintsTable = new DataTable('#complaintsTable');
        });
}

function updateStatistics(complaints) {
    document.getElementById('totalComplaints').textContent = complaints.length;
    document.getElementById('criticalCount').textContent = 
        complaints.filter(c => c.priority === 'Critical').length;
    document.getElementById('pendingCount').textContent = 
        complaints.filter(c => c.status === 'Pending').length;
    document.getElementById('resolvedCount').textContent = 
        complaints.filter(c => c.status === 'Resolved').length;
}

function getSentimentColor(sentiment) {
    return {
        'Positive': 'success',
        'Neutral': 'secondary',
        'Negative': 'danger'
    }[sentiment] || 'secondary';
}

function getPriorityColor(priority) {
    return {
        'Critical': 'danger',
        'High': 'warning',
        'Medium': 'primary',
        'Low': 'success'
    }[priority] || 'secondary';
}

function getStatusColor(status) {
    return {
        'Pending': 'warning',
        'In Progress': 'info',
        'Resolved': 'success',
        'Closed': 'secondary'
    }[status] || 'secondary';
}

function editComplaint(id) {
    document.getElementById('editComplaintId').value = id;
    new bootstrap.Modal(document.getElementById('editModal')).show();
}

function updateComplaint() {
    const id = document.getElementById('editComplaintId').value;
    const status = document.getElementById('editStatus').value;
    const assigned_to = document.getElementById('editAssignedTo').value;
    
    fetch(`/api/admin/complaint/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status, assigned_to })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
            loadComplaints();
        }
    });
}

function logout() {
    fetch('/api/logout')
        .then(() => window.location.href = '/');
}