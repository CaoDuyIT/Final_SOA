// --- DOM ELEMENTS ---
const roomListContainer = document.getElementById('room-list');
const searchForm = document.getElementById('search-form');
const bookingModal = document.getElementById('booking-modal');
const paymentModal = document.getElementById('payment-modal');
const priceDisplay = document.getElementById('price-display');
const priceSelect = document.getElementById('max-price');

// --- RENDER FUNCTIONS ---
document.addEventListener('DOMContentLoaded', async () => {
    const roomListContainer = document.getElementById('room-list');

    async function loadRoomTypes() {
        const accessToken = sessionStorage.getItem("access_token"); // Lấy token đã sửa
    
        if (!accessToken) {
            alert("Please log in to view room types.");
            window.location.href = "login.html"; // Chuyển hướng đến trang đăng nhập
            return;
        }

        try {
            const headers = {
                "Authorization": `Bearer ${accessToken}`, // Sử dụng token đã lấy
                "Content-Type": "application/json"
            };
            const response = await fetch('http://127.0.0.1:8000/rooms/get_all_type/',
                {
                    method: "GET",
                    headers: headers
                });
            if (!response.ok) {
                const err = await response.json();
                alert(err.detail);
                return;
            }

            const roomTypes = await response.json();
            roomListContainer.innerHTML = ''; 

            roomTypes.forEach(room => {
                const roomCard = document.createElement('div');
                roomCard.className = 'room-card';
                roomCard.style.border = '1px solid #ccc';
                roomCard.style.padding = '15px';
                roomCard.style.marginBottom = '15px';
                roomCard.style.borderRadius = '8px';
                roomCard.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';

                roomCard.innerHTML = `
                    <h3>${room.Name}</h3>
                    <p>${room.Description}</p>
                    <p>Price: ${room.Price.toLocaleString()} / night</p>
                    <p>Max People: ${room.MaxPeople}, Beds: ${room.BedCount}</p>
                `;
                roomListContainer.appendChild(roomCard);
            });

        } catch (err) {
            console.error(err);
            roomListContainer.innerHTML = '<p>Failed to load room types.</p>';
        }
    }

    loadRoomTypes();
});



