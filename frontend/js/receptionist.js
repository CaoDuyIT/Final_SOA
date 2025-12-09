const API_BASE_URL = "http://127.0.0.1:8080";

document.addEventListener("DOMContentLoaded", () => {
    const searchForm = document.getElementById("search-booking-form");
    const searchInput = document.getElementById("search-input");
    const resetBtn = document.getElementById("reset-search-btn");
    const searchResultsContainer = document.getElementById("search-results");

    // Navigation
    const navCheckinCheckout = document.getElementById("nav-checkin-checkout");
    // const navBookings = document.getElementById("nav-bookings");
    // const navReport = document.getElementById("nav-report");
    
    const contentCheckinCheckout = document.getElementById("checkin-checkout-content");
    // const contentBookings = document.getElementById("bookings-content");
    // const contentReport = document.getElementById("report-content");

    function showContent(contentId) {
        // [contentCheckinCheckout, contentBookings, contentReport].forEach(el => el.style.display = "none");
        contentCheckinCheckout.style.display = "block";
        
        // Update active nav
        // [navCheckinCheckout, navBookings, navReport].forEach(el => el.classList.remove("active"));
        if(contentId === "checkin-checkout-content") navCheckinCheckout.classList.add("active");
        // if(contentId === "bookings-content") navBookings.classList.add("active");
        // if(contentId === "report-content") navReport.classList.add("active");
    }

    navCheckinCheckout.addEventListener("click", (e) => { e.preventDefault(); showContent("checkin-checkout-content"); });
    // navBookings.addEventListener("click", (e) => { e.preventDefault(); showContent("bookings-content"); });
    // navReport.addEventListener("click", (e) => { e.preventDefault(); showContent("report-content"); });

    // Load all bookings initially
    loadBookings();

    // Reset Handler
    resetBtn.addEventListener("click", () => {
        searchInput.value = "";
        loadBookings();
    });

    // Search Handler
    searchForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const query = searchInput.value.trim();
        loadBookings(query);
    });

    async function loadBookings(query = "") {
        try {
            let url = `${API_BASE_URL}/receptionist/bookings/search`;
            if (query) {
                url += `?query=${encodeURIComponent(query)}`;
            }
            
            const response = await fetch(url);
            if (!response.ok) throw new Error("Failed to fetch bookings");
            
            const bookings = await response.json();
            displaySearchResults(bookings);
        } catch (error) {
            console.error(error);
            searchResultsContainer.innerHTML = `<p class="error">Error loading bookings: ${error.message}</p>`;
        }
    }

    function displaySearchResults(bookings) {
        if (bookings.length === 0) {
            searchResultsContainer.innerHTML = "<p>No bookings found.</p>";
            return;
        }

        let html = `
            <table class="results-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Customer</th>
                        <th>Phone</th>
                        <th>Rooms</th>
                        <th>Check-in</th>
                        <th>Check-out</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
        `;

        bookings.forEach(booking => {
            let actionBtn = "";
            // Logic for buttons based on status
            // Cycle: Booked/Confirmed/Paid -> Check-in -> Occupied -> Check-out -> Maintenance (Need Clean) -> Available (Check-in)
            
            const status = booking.BookingStatus;
            const roomStatus = booking.RoomStatuses || ""; // e.g. "Need Clean, Available"

            if (['Booked', 'Confirmed', 'Paid'].includes(status)) {
                actionBtn = `<button class="btn-checkin" onclick="handleCheckIn(${booking.TransactionID})">Check In</button>`;
            } else if (['Occupied', 'CheckedIn'].includes(status)) {
                actionBtn = `<button class="btn-checkout" onclick="handleCheckOut(${booking.TransactionID})">Check Out</button>`;
            } else if (status === 'Maintenance') {
                // If Maintenance, check room status
                if (roomStatus.includes('Need Clean') || roomStatus.includes('Cleaning') || roomStatus.includes('Wait Check Clean')) {
                    actionBtn = `<button class="btn-waiting" disabled style="background-color: #ffc107; cursor: not-allowed;">Need to clean</button>`;
                } else if (roomStatus.includes('Available')) {
                    // Room is clean/available, allow Check-in (new cycle)
                    actionBtn = `<button class="btn-checkin" onclick="handleCheckIn(${booking.TransactionID})">Check In</button>`;
                } else {
                     // Fallback
                     actionBtn = `<button class="btn-waiting" disabled style="background-color: #ffc107; cursor: not-allowed;">Cleaning...</button>`;
                }
            } else if (status === 'Completed') {
                 actionBtn = `<span class="status-badge completed">Completed</span>`;
            } else {
                actionBtn = `<span class="status-badge ${status.toLowerCase()}">${status}</span>`;
            }

            html += `
                <tr>
                    <td>${booking.TransactionID}</td>
                    <td>${booking.CustomerName}</td>
                    <td>${booking.PhoneNumber}</td>
                    <td>${booking.RoomNumbers || 'N/A'}</td>
                    <td>${new Date(booking.CheckIn).toLocaleDateString()}</td>
                    <td>${new Date(booking.CheckOut).toLocaleDateString()}</td>
                    <td>${booking.BookingStatus}</td>
                    <td>${actionBtn}</td>
                </tr>
            `;
        });

        html += `</tbody></table>`;
        searchResultsContainer.innerHTML = html;
    }

    // Expose functions to global scope for onclick handlers
    window.handleCheckIn = async (transactionId) => {
        // if (!confirm(`Confirm Check-in for Booking #${transactionId}?`)) return;
        
        try {
            const response = await fetch(`${API_BASE_URL}/receptionist/bookings/${transactionId}/check-in`, {
                method: "POST"
            });
            const result = await response.json();
            
            if (!response.ok) throw new Error(result.detail || "Check-in failed");
            
            // alert("Check-in successful!");
            // Refresh list
            const query = searchInput.value.trim();
            loadBookings(query);
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    };

    window.handleCheckOut = async (transactionId) => {
        // if (!confirm(`Confirm Check-out for Booking #${transactionId}?`)) return;
        
        try {
            const response = await fetch(`${API_BASE_URL}/receptionist/bookings/${transactionId}/check-out`, {
                method: "POST"
            });
            const result = await response.json();
            
            if (!response.ok) throw new Error(result.detail || "Check-out failed");
            
            // alert("Check-out successful!");
            // Refresh list
            const query = searchInput.value.trim();
            loadBookings(query);
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    };
});
