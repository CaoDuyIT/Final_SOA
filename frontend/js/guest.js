// =======================
// 1. Global Variables
// =======================
let allRooms = [];
window.bookingCart = [];

// =======================
// 2. Modal Elements
// =======================
const bookingModal = document.getElementById('booking-modal');
const modalOverlay = document.getElementById('modal-overlay');
const paymentModal = document.getElementById('payment-modal');
const paymentOverlay = document.getElementById('payment-overlay');

// =======================
// 3. Helper Functions
// =======================
function openModal(modal, overlay) {
    modal.style.display = 'flex';
    overlay.style.display = 'flex';
    document.body.classList.add('modal-open');
}

function closeModal(modal, overlay) {
    modal.style.display = 'none';
    overlay.style.display = 'none';
    document.body.classList.remove('modal-open');
}

// =======================
// 4. Login / Logout
// =======================
const navLogin = document.querySelector('header nav ul li a[href="login.html"]');

function isTokenExpired(token) {
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.exp && payload.exp < Math.floor(Date.now() / 1000);
    } catch {
        return true;
    }
}

// --- Logout Modal Elements ---
const logoutModal = document.getElementById('logout-modal');
const logoutOverlay = document.getElementById('logout-overlay');
const logoutClose = document.getElementById('logout-close');
const logoutCancel = document.getElementById('logout-cancel');
const logoutConfirm = document.getElementById('logout-confirm');

// --- Open / Close Logout Modal ---
function openLogoutModal() { openModal(logoutModal, logoutOverlay); }
function closeLogoutModal() { closeModal(logoutModal, logoutOverlay); }

logoutClose.onclick = logoutCancel.onclick = closeLogoutModal;

// --- Click Confirm Logout ---
logoutConfirm.onclick = () => {
    sessionStorage.removeItem('access_token');
    closeLogoutModal();
    window.location.href = 'login.html'; // redirect sang login
};

// --- Update Login Status ---
function updateLoginStatus() {
    const token = sessionStorage.getItem('access_token');

    if (!token) {
        // Không có token → Login
        navLogin.textContent = 'Login';
        navLogin.href = 'login.html';
        navLogin.onclick = null;
        return;
    }

    // Kiểm tra token hết hạn
    if (isTokenExpired(token)) {
        sessionStorage.removeItem('access_token');
        window.location.href = 'login.html'; // redirect thẳng sang login
        return;
    }

    // Token hợp lệ → Log out (chỉ mở modal khi click)
    navLogin.textContent = 'Log out';
    navLogin.href = '#';
    navLogin.onclick = (e) => {
        e.preventDefault();
        openLogoutModal();
    };
}


// =======================
// 5. Render Rooms
// =======================
const roomListContainer = document.getElementById('room-list');

function renderRooms(rooms) {
    roomListContainer.innerHTML = '';
    if (rooms.length === 0) {
        roomListContainer.innerHTML = '<p>No rooms match your search criteria.</p>';
        return;
    }

    rooms.forEach(room => {
        const card = document.createElement('div');
        card.className = 'room-card';
        card.style.cursor = 'pointer';
        card.style.width = '200px';
        card.style.margin = '10px';
        card.style.border = '1px solid #ccc';
        card.style.borderRadius = '8px';
        card.style.overflow = 'hidden';
        card.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';

        const img = document.createElement('img');
        img.src = room.ImageUrl || 'https://via.placeholder.com/200x120?text=No+Image';
        img.style.width = '100%';
        img.style.height = '120px';
        img.style.objectFit = 'cover';
        card.appendChild(img);

        const info = document.createElement('div');
        info.style.padding = '10px';
        info.innerHTML = `<h4>${room.Name}</h4><p>$${room.Price.toLocaleString()} / night</p>`;
        card.appendChild(info);

        card.addEventListener('click', () => openRoomDetail(room));
        roomListContainer.appendChild(card);
    });
}

// =======================
// 6. Fetch Rooms
// =======================
async function loadRooms() {
    const token = sessionStorage.getItem('access_token');
    if (!token) {
        alert('Please log in.');
        window.location.href = 'login.html';
        return;
    }

    try {
        const res = await fetch('http://127.0.0.1:8000/rooms/get_all_type/', {
            headers: { Authorization: `Bearer ${token}` }
        });
        if (!res.ok) throw new Error('Failed to load rooms');
        allRooms = await res.json();
        renderRooms(allRooms);
    } catch (err) {
        console.error(err);
        roomListContainer.innerHTML = '<p>Failed to load rooms.</p>';
    }
}

// =======================
// 7. Search / Filter
// =======================
const searchForm = document.getElementById('search-form');
searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const checkIn = document.getElementById('check-in').value;
    const checkOut = document.getElementById('check-out').value;
    const guests = parseInt(document.getElementById('guests').value) || 0;
    const type = document.getElementById('room-type').value.toLowerCase();
    const maxPrice = parseFloat(document.getElementById('max-price').value) || Infinity;

    const filtered = allRooms.filter(r => 
        (guests === 0 || r.MaxPeople >= guests) &&
        (type === '' || r.Name.toLowerCase().includes(type)) &&
        r.Price <= maxPrice
    );

    renderRooms(filtered);
});

// =======================
// 8. Room Modal
// =======================
function openRoomDetail(room) {
    bookingModal.innerHTML = `
        <span id="modal-close-detail" style="cursor: pointer; position: absolute; top: 10px; right: 15px; font-size: 24px;">&times;</span>
        <div class="modal-body">
            <h2>${room.Name}</h2>
            <p>${room.Description}</p>
            <p>Price: $${room.Price.toLocaleString()} / night</p>
            <p>Beds: ${room.BedCount} | Max People: ${room.MaxPeople}</p>
            <p>Available: <span id="modal-available-qty">${room.Available}</span></p>
            <label>Quantity: <input type="number" id="room-qty" min="1" max="${room.Available}" value="1" style="width:60px"></label>
        </div>
        <div class="modal-footer">
            <button class="btn btn-primary" id="add-booking-btn">Add to Booking</button>
        </div>
    `;
    document.getElementById('modal-close-detail').onclick = () => closeModal(bookingModal, modalOverlay);

    document.getElementById('add-booking-btn').onclick = () => {
        const qty = parseInt(document.getElementById('room-qty').value);
        if (qty > room.Available) { alert('Not enough rooms'); return; }

        const existing = window.bookingCart.find(i => i.RoomId === room.Id);
        let totalQty = qty + (existing ? existing.Quantity : 0);
        if (totalQty > room.Available) {
            alert(`Exceeds available (${room.Available})`);
            return;
        }

        if (existing) existing.Quantity = totalQty;
        else window.bookingCart.push({...room, Quantity: qty});

        room.Available -= qty;
        document.getElementById('modal-available-qty').textContent = room.Available;

        alert(`${qty} room(s) added to booking`);
        updateCheckoutLink();
        closeModal(bookingModal, modalOverlay);
    };

    openModal(bookingModal, modalOverlay);
}

// =======================
// 9. Checkout / Payment
// =======================
function updateCheckoutLink() {
    let checkoutLink = document.getElementById('checkout-link');
    if (!checkoutLink) {
        const li = document.createElement('li');
        li.innerHTML = `<a href="#" id="checkout-link">Checkout (${window.bookingCart.length})</a>`;
        document.querySelector('nav ul').appendChild(li);
        checkoutLink = document.getElementById('checkout-link');
        checkoutLink.onclick = (e) => { e.preventDefault(); openPaymentModal(); };
    } else {
        checkoutLink.textContent = `Checkout (${window.bookingCart.length})`;
    }
}

function openPaymentModal() {
    if (window.bookingCart.length === 0) { alert('Cart empty'); return; }
    const total = window.bookingCart.reduce((sum,i)=>sum + i.Price*i.Quantity,0);
    document.getElementById('total-amount').textContent = `$${total.toLocaleString()}`;
    openModal(paymentModal, paymentOverlay);
}

paymentModal.querySelector('.close-btn').onclick = () => closeModal(paymentModal, paymentOverlay);
paymentOverlay.onclick = () => closeModal(paymentModal, paymentOverlay);

// =======================
// 10. Init
// =======================
document.addEventListener('DOMContentLoaded', () => {
    updateLoginStatus();
    loadRooms();
});
