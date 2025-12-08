document.addEventListener('DOMContentLoaded', () => {
    // --- NAVIGATION HANDLING ---
    const navLinks = document.querySelectorAll('.sidebar-nav a');
    const contentBlocks = document.querySelectorAll('.main-content .content-block');

    const navMapping = {
        'nav-rooms': 'rooms-content',
        'nav-staff': 'staff-content'
    };

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = navMapping[link.id];
            if (!targetId) return;

            // Update active link
            navLinks.forEach(nav => nav.classList.remove('active'));
            link.classList.add('active');

            // Show/hide content blocks
            contentBlocks.forEach(block => {
                if (block.id === targetId) {
                    block.style.display = 'block';
                } else {
                    block.style.display = 'none';
                }
            });
        });
    });


    // --- MODAL HANDLING ---
    const openModal = (modal) => {
        modal.querySelector('.modal-overlay').style.display = 'flex';
    };
    const closeModal = (modal) => {
        modal.querySelector('.modal-overlay').style.display = 'none';
    };

    // Generic close behavior for all modals
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                closeModal(overlay.closest('.modal-container'));
            }
        });
    });
    document.querySelectorAll('.close-btn, .cancel-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            closeModal(e.target.closest('.modal-container'));
        });
    });


    // --- ROOM MANAGEMENT ---
    const roomModal = document.getElementById('room-modal');
    const deleteRoomModal = document.getElementById('delete-room-modal');
    const roomForm = document.getElementById('room-form');
    const roomModalTitle = document.getElementById('room-modal-title');

    // Open "Add Room" modal
    document.getElementById('add-room-btn').addEventListener('click', () => {
        roomModalTitle.textContent = 'Add New Room';
        roomForm.reset();
        openModal(roomModal);
    });

    // Open "Edit Room" modal
    document.querySelectorAll('.edit-room-btn').forEach(btn => {
        btn.addEventListener('click', e => {
            roomModalTitle.textContent = 'Edit Room';
            // Logic to populate form would go here
            openModal(roomModal);
        });
    });

    // Open "Delete Room" modal
    document.querySelectorAll('.delete-room-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            openModal(deleteRoomModal);
        });
    });


    // --- STAFF MANAGEMENT ---
    const staffModal = document.getElementById('staff-modal');
    const deleteStaffModal = document.getElementById('delete-staff-modal');
    const staffForm = document.getElementById('staff-form');
    const staffModalTitle = document.getElementById('staff-modal-title');

    // Open "Add Staff" modal
    document.getElementById('add-staff-btn').addEventListener('click', () => {
        staffModalTitle.textContent = 'Add New Staff';
        staffForm.reset();
        openModal(staffModal);
    });

    // Open "Edit Staff" modal
    document.querySelectorAll('.edit-staff-btn').forEach(btn => {
        btn.addEventListener('click', e => {
            staffModalTitle.textContent = 'Edit Staff';
            // Logic to populate form would go here
            openModal(staffModal);
        });
    });

    // Open "Delete Staff" modal
    document.querySelectorAll('.delete-staff-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            openModal(deleteStaffModal);
        });
    });
});
