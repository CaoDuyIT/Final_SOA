const API_BASE_URL = 'http://127.0.0.1:8080';

document.addEventListener('DOMContentLoaded', () => {
    fetchRoomsToClean();
});

async function fetchRoomsToClean() {
    try {
        const response = await fetch(`${API_BASE_URL}/housekeeping/rooms-to-clean`);
        if (!response.ok) {
            throw new Error('Failed to fetch rooms');
        }
        const rooms = await response.json();
        renderRoomsTable(rooms);
    } catch (error) {
        console.error('Error:', error);
        alert('Không thể tải danh sách phòng cần dọn.');
    }
}

function renderRoomsTable(rooms) {
    const tableBody = document.querySelector('#rooms-to-clean-table tbody');
    tableBody.innerHTML = '';

    if (rooms.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="4" style="text-align:center;">Không có phòng nào cần dọn</td></tr>';
        return;
    }

    rooms.forEach(room => {
        const row = document.createElement('tr');
        let actionButton = '';
        if (room.Status === 'Need Clean') {
            actionButton = `<button class="btn edit-btn" onclick="updateRoomStatus('${room.RoomNumber}', 'Cleaning')">Start Cleaning</button>`;
        } else if (room.Status === 'Cleaning') {
             actionButton = `<button class="btn action-btn" onclick="updateRoomStatus('${room.RoomNumber}', 'Wait Check Clean')">Done</button>`;
        } else if (room.Status === 'Wait Check Clean') {
             actionButton = `<button class="btn" disabled style="background-color: #6c757d; cursor: not-allowed;">Waiting for Check</button>`;
        } else if (room.Status === 'Available') {
             actionButton = `<button class="btn" disabled style="background-color: #28a745; cursor: not-allowed;">Available</button>`;
        } else {
            actionButton = `<span class="status-badge">${room.Status}</span>`;
        }

        row.innerHTML = `
            <td>${room.RoomNumber}</td>
            <td>${room.RoomType}</td>
            <td class="status">${room.Status}</td>
            <td class="actions">
                ${actionButton}
            </td>
        `;
        tableBody.appendChild(row);
    });
}

async function updateRoomStatus(roomNumber, newStatus) {
    try {
        const response = await fetch(`${API_BASE_URL}/housekeeping/rooms/${roomNumber}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: newStatus })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to update status');
        }

        const result = await response.json();
        alert(result.message);
        
        // Refresh the list
        fetchRoomsToClean();

    } catch (error) {
        console.error('Error:', error);
        alert(`Lỗi: ${error.message}`);
    }
}

