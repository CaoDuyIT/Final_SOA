document.addEventListener('DOMContentLoaded', () => {
    // --- SAMPLE DATABASE ---
    const roomsData = [
        { id: 1, name: 'Standard Single Room', type: 'Single', beds: 1, area: 20, amenities: ['Wi-Fi', 'TV', 'AC'], price: 100, image: 'https://via.placeholder.com/400x250/1' },
        { id: 2, name: 'Deluxe Double Room', type: 'Double', beds: 1, area: 30, amenities: ['Wi-Fi', 'TV', 'AC', 'Mini-bar'], price: 180, image: 'https://via.placeholder.com/400x250/2' },
        { id: 3, name: 'Family Suite', type: 'Suite', beds: 2, area: 50, amenities: ['Wi-Fi', 'TV', 'AC', 'Kitchenette'], price: 250, image: 'https://via.placeholder.com/400x250/3' },
        { id: 4, name: 'Economy Twin Room', type: 'Double', beds: 2, area: 25, amenities: ['Wi-Fi', 'TV'], price: 120, image: 'https://via.placeholder.com/400x250/4' },
        { id: 5, name: 'Presidential Suite', type: 'Suite', beds: 3, area: 100, amenities: ['Wi-Fi', 'TV', 'AC', 'Kitchenette', 'Jacuzzi'], price: 480, image: 'https://via.placeholder.com/400x250/5' }
    ];

    // --- DOM ELEMENTS ---
    const roomListContainer = document.getElementById('room-list');
    const searchForm = document.getElementById('search-form');
    const bookingModal = document.getElementById('booking-modal');
    const paymentModal = document.getElementById('payment-modal');
    const priceDisplay = document.getElementById('price-display');
    const maxPriceInput = document.getElementById('max-price');

    // --- RENDER FUNCTIONS ---
    const renderRooms = (rooms) => {
        roomListContainer.innerHTML = ''; // Clear existing rooms
        if (rooms.length === 0) {
            roomListContainer.innerHTML = '<p>No rooms match your criteria.</p>';
            return;
        }
        rooms.forEach(room => {
            const roomCard = document.createElement('div');
            roomCard.className = 'room-card';
            roomCard.innerHTML = `
                <img src="${room.image}" alt="${room.name}">
                <div class="room-info">
                    <h3>${room.name}</h3>
                    <p>${room.beds} Bed(s) &middot; ${room.area}m²</p>
                    <div class="room-price">
                        <p>$${room.price} / night</p>
                        <button class="book-now-btn" data-room-id="${room.id}">Details</button>
                    </div>
                </div>
            `;
            roomListContainer.appendChild(roomCard);
        });
    };

    // --- MODAL HANDLING ---
    const openModal = (modal) => modal.querySelector('.modal-overlay').style.display = 'flex';
    const closeModal = (modal) => modal.querySelector('.modal-overlay').style.display = 'none';

    document.querySelectorAll('.modal-container').forEach(modal => {
        const overlay = modal.querySelector('.modal-overlay');
        const closeBtn = modal.querySelector('.close-btn');
        if (overlay) overlay.addEventListener('click', (e) => { if (e.target === overlay) closeModal(modal); });
        if (closeBtn) closeBtn.addEventListener('click', () => closeModal(modal));
    });

    // --- EVENT LISTENERS ---

    // Price Range Slider
    maxPriceInput.addEventListener('input', (e) => {
        priceDisplay.textContent = `$${e.target.value}`;
    });

    // Search and Filter
    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const guests = parseInt(document.getElementById('guests').value, 10) || 0;
        const roomType = document.getElementById('room-type').value;
        const maxPrice = parseInt(maxPriceInput.value, 10);

        const filteredRooms = roomsData.filter(room => {
            const guestMatch = !guests || room.beds >= guests;
            const typeMatch = !roomType || room.type === roomType;
            const priceMatch = room.price <= maxPrice;
            return guestMatch && typeMatch && priceMatch;
        });
        renderRooms(filteredRooms);
    });

    // Open Room Details Modal
    roomListContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('book-now-btn')) {
            const roomId = parseInt(e.target.getAttribute('data-room-id'), 10);
            const room = roomsData.find(r => r.id === roomId);
            const checkinDate = document.getElementById('check-in').value;
            const checkoutDate = document.getElementById('check-out').value;

            const modalBody = document.getElementById('booking-modal-body');
            modalBody.innerHTML = `
                <h3 style="font-size: 1.5rem; margin-top: 0;">${room.name}</h3>
                <p><strong>Price:</strong> $${room.price} / night</p>
                <p><strong>Area:</strong> ${room.area}m²</p>
                <p><strong>Beds:</strong> ${room.beds}</p>
                <p><strong>Amenities:</strong> ${room.amenities.join(', ')}</p>
                <hr>
                <p>Your selected dates:</p>
                <p><strong>Check-in:</strong> ${checkinDate || 'Not selected'}</p>
                <p><strong>Check-out:</strong> ${checkoutDate || 'Not selected'}</p>
            `;
            openModal(bookingModal);
        }
    });
    
    // Payment Flow
    document.getElementById('payment-btn').addEventListener('click', () => {
        closeModal(bookingModal);
        openModal(paymentModal);
    });

    document.getElementById('payment-form').addEventListener('submit', (e) => {
        e.preventDefault();
        alert('Payment successful! A confirmation email has been sent.');
        closeModal(paymentModal);
    });

    // --- INITIAL RENDER ---
    renderRooms(roomsData);
});
