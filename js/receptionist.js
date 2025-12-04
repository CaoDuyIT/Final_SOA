document.addEventListener('DOMContentLoaded', () => {
    // --- SAMPLE DATABASE ---
    let bookingsData = [
        { id: 'BK-12345', guestName: 'John Doe', phone: '555-1111', roomNumber: '101', status: 'Confirmed' },
        { id: 'BK-67890', guestName: 'Jane Smith', phone: '555-2222', roomNumber: '205', status: 'Occupied' },
        { id: 'BK-ABCDE', guestName: 'Peter Jones', phone: '555-3333', roomNumber: '102', status: 'Confirmed' },
        { id: 'BK-FGHIJ', guestName: 'Alice Williams', phone: '555-4444', roomNumber: '301', status: 'Checked-out' }
    ];

    // --- DOM ELEMENTS ---
    const navLinks = document.querySelectorAll('.sidebar-nav a');
    const contentBlocks = document.querySelectorAll('.main-content .content-block');
    const searchForm = document.getElementById('search-booking-form');
    const searchInput = document.getElementById('search-input');
    const searchResultsContainer = document.getElementById('search-results');
    const allBookingsTableBody = document.querySelector('#all-bookings-table tbody');
    const reportIssueForm = document.getElementById('report-issue-form');

    // --- NAVIGATION ---
    const navMapping = {
        'nav-checkin-checkout': 'checkin-checkout-content',
        'nav-bookings': 'bookings-content',
        'nav-report': 'report-content'
    };

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = navMapping[link.id];
            if (!targetId) return;

            navLinks.forEach(nav => nav.classList.remove('active'));
            link.classList.add('active');

            contentBlocks.forEach(block => {
                block.style.display = (block.id === targetId) ? 'block' : 'none';
            });
            
            if (targetId === 'bookings-content') {
                renderAllBookings();
            }
        });
    });

    // --- RENDER FUNCTIONS ---
    const renderAllBookings = () => {
        allBookingsTableBody.innerHTML = '';
        bookingsData.forEach(booking => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${booking.id}</td>
                <td>${booking.guestName}</td>
                <td>${booking.roomNumber}</td>
                <td>${booking.status}</td>
            `;
            allBookingsTableBody.appendChild(row);
        });
    };

    const renderSearchResult = (booking) => {
        let actionButton = '';
        if (booking.status === 'Confirmed') {
            actionButton = `<button class="btn action-btn checkin-btn" data-id="${booking.id}">Check-in</button>`;
        } else if (booking.status === 'Occupied') {
            actionButton = `<button class="btn edit-btn checkout-btn" data-id="${booking.id}">Check-out</button>`;
        }

        searchResultsContainer.innerHTML = `
            <div class="result-card">
                <h4>${booking.guestName}</h4>
                <p><strong>Booking ID:</strong> ${booking.id}</p>
                <p><strong>Room:</strong> ${booking.roomNumber}</p>
                <p><strong>Status:</strong> <span class="status">${booking.status}</span></p>
                <div class="actions">${actionButton}</div>
            </div>
        `;
    };

    // --- EVENT LISTENERS & LOGIC ---

    // Search
    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const query = searchInput.value.toLowerCase().trim();
        const result = bookingsData.find(b => 
            b.id.toLowerCase() === query || 
            b.guestName.toLowerCase().includes(query) ||
            b.phone.includes(query)
        );

        if (result) {
            renderSearchResult(result);
        } else {
            searchResultsContainer.innerHTML = '<p>No booking found.</p>';
        }
    });

    // Check-in / Check-out
    searchResultsContainer.addEventListener('click', (e) => {
        const bookingId = e.target.dataset.id;
        if (!bookingId) return;

        const booking = bookingsData.find(b => b.id === bookingId);
        if (!booking) return;

        if (e.target.classList.contains('checkin-btn')) {
            booking.status = 'Occupied';
            alert(`Guest ${booking.guestName} checked into room ${booking.roomNumber}.`);
        } else if (e.target.classList.contains('checkout-btn')) {
            booking.status = 'Needs Cleaning';
            alert(`Guest ${booking.guestName} checked out of room ${booking.roomNumber}. Room status set to "Needs Cleaning".`);
        }
        
        renderSearchResult(booking); // Re-render the card to update status and button
    });

    // Report Issue
    reportIssueForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const room = document.getElementById('issue-room-number').value;
        const desc = document.getElementById('issue-description').value;
        alert(`Issue reported for room ${room}: "${desc}". The manager has been notified.`);
        reportIssueForm.reset();
    });

    // Initial Render
    renderAllBookings();
});
