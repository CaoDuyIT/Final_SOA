document.addEventListener('DOMContentLoaded', () => {
    // Get modals
    const userModal = document.getElementById('user-modal');
    const deleteModal = document.getElementById('delete-modal');

    // Get modal overlays
    const userModalOverlay = userModal.querySelector('.modal-overlay');
    const deleteModalOverlay = deleteModal.querySelector('.modal-overlay');

    // Get close buttons
    const userModalCloseBtn = userModal.querySelector('.close-btn');
    const deleteModalCloseBtn = deleteModal.querySelector('.close-btn');

    // Get form and modal title
    const modalTitle = document.getElementById('modal-title');
    const userForm = document.getElementById('user-form');

    // Get main action buttons
    const addUserBtn = document.getElementById('add-user-btn');

    // Get table action buttons
    const editBtns = document.querySelectorAll('.edit-btn');
    const deleteBtns = document.querySelectorAll('.delete-btn');

    // Function to open a modal
    const openModal = (modal) => {
        modal.querySelector('.modal-overlay').style.display = 'flex';
    };

    // Function to close a modal
    const closeModal = (modal) => {
        modal.querySelector('.modal-overlay').style.display = 'none';
    };

    // --- Event Listeners ---

    // Open "Add User" modal
    addUserBtn.addEventListener('click', () => {
        modalTitle.textContent = 'Add New User';
        userForm.reset(); // Clear form fields
        openModal(userModal);
    });

    // Open "Edit User" modal for each edit button
    editBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            modalTitle.textContent = 'Edit User';

            // Get data from the table row
            const row = e.target.closest('tr');
            const name = row.cells[0].textContent;
            const email = row.cells[1].textContent;
            const role = row.cells[2].textContent;

            // Populate the form
            document.getElementById('name').value = name;
            document.getElementById('email').value = email;
            document.getElementById('role').value = role;

            openModal(userModal);
        });
    });

    // Open "Delete" confirmation modal
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            openModal(deleteModal);
        });
    });

    // Close modals via close buttons
    userModalCloseBtn.addEventListener('click', () => closeModal(userModal));
    deleteModalCloseBtn.addEventListener('click', () => closeModal(deleteModal));

    // Close modals by clicking on the overlay
    userModalOverlay.addEventListener('click', (e) => {
        if (e.target === userModalOverlay) {
            closeModal(userModal);
        }
    });
    deleteModalOverlay.addEventListener('click', (e) => {
        if (e.target === deleteModalOverlay) {
            closeModal(deleteModal);
        }
    });

    // Handle form submission (for both add and edit)
    userForm.addEventListener('submit', (e) => {
        e.preventDefault();
        // Here you would typically send the data to a server
        console.log('Form submitted');
        console.log('Name:', document.getElementById('name').value);
        console.log('Email:', document.getElementById('email').value);
        console.log('Role:', document.getElementById('role').value);
        closeModal(userModal);
        // You might want to refresh the table data here
    });

    // Handle delete confirmation
    document.getElementById('confirm-delete-btn').addEventListener('click', () => {
        // Here you would typically send a request to the server to delete the user
        console.log('User deleted');
        closeModal(deleteModal);
        // You might want to remove the row from the table here
    });

    document.getElementById('cancel-delete-btn').addEventListener('click', () => {
        closeModal(deleteModal);
    });
});
