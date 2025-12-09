const API_BASE_URL = "http://127.0.0.1:8080";

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
    const passwordGroup = document.getElementById('password-group');

    // Get main action buttons
    const addUserBtn = document.getElementById('add-user-btn');
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
    const cancelDeleteBtn = document.getElementById('cancel-delete-btn');

    let currentDeleteId = null;

    // --- API Functions ---

    async function fetchRoles() {
        try {
            const response = await fetch(`${API_BASE_URL}/roles/`);
            const data = await response.json();
            const roleSelect = document.getElementById('role');
            roleSelect.innerHTML = '';
            data.roles.forEach(role => {
                const option = document.createElement('option');
                option.value = role.RoleID;
                option.textContent = role.Name;
                roleSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error fetching roles:', error);
        }
    }

    async function fetchUsers() {
        try {
            const response = await fetch(`${API_BASE_URL}/users/`);
            const data = await response.json();
            const tbody = document.getElementById('user-table-body');
            tbody.innerHTML = '';

            data.users.forEach(user => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${user.CustomerID}</td>
                    <td>${user.UserName}</td>
                    <td>${user.FullName}</td>
                    <td>${user.Email}</td>
                    <td>${user.PhoneNumber || ''}</td>
                    <td>${user.RoleName}</td>
                    <td class="actions">
                        <button class="edit-btn" data-id="${user.CustomerID}" data-role="${user.RoleID}">Edit</button>
                        <button class="delete-btn" data-id="${user.CustomerID}">Delete</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });

            // Re-attach event listeners
            attachActionListeners();
        } catch (error) {
            console.error('Error fetching users:', error);
        }
    }

    async function createUser(userData) {
        try {
            const response = await fetch(`${API_BASE_URL}/users/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData)
            });
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Failed to create user');
            }
            alert('User created successfully');
            closeModal(userModal);
            fetchUsers();
        } catch (error) {
            alert(error.message);
        }
    }

    async function updateUser(userId, userData) {
        try {
            const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData)
            });
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Failed to update user');
            }
            alert('User updated successfully');
            closeModal(userModal);
            fetchUsers();
        } catch (error) {
            alert(error.message);
        }
    }

    async function deleteUser(userId) {
        try {
            const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
                method: 'DELETE'
            });
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Failed to delete user');
            }
            alert('User deleted successfully');
            closeModal(deleteModal);
            fetchUsers();
        } catch (error) {
            alert(error.message);
        }
    }

    // --- UI Functions ---

    const openModal = (modal) => {
        modal.querySelector('.modal-overlay').style.display = 'flex';
    };

    const closeModal = (modal) => {
        modal.querySelector('.modal-overlay').style.display = 'none';
    };

    function attachActionListeners() {
        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const row = e.target.closest('tr');
                const id = btn.dataset.id;
                const roleId = btn.dataset.role;
                
                document.getElementById('user-id').value = id;
                document.getElementById('username').value = row.cells[1].textContent;
                document.getElementById('fullname').value = row.cells[2].textContent;
                document.getElementById('email').value = row.cells[3].textContent;
                document.getElementById('phonenumber').value = row.cells[4].textContent;
                document.getElementById('role').value = roleId;

                modalTitle.textContent = 'Edit User';
                passwordGroup.style.display = 'none'; // Hide password on edit
                document.getElementById('password').removeAttribute('required');
                
                openModal(userModal);
            });
        });

        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                currentDeleteId = btn.dataset.id;
                openModal(deleteModal);
            });
        });
    }

    // --- Event Listeners ---

    addUserBtn.addEventListener('click', () => {
        modalTitle.textContent = 'Add New User';
        userForm.reset();
        document.getElementById('user-id').value = '';
        passwordGroup.style.display = 'block'; // Show password on add
        document.getElementById('password').setAttribute('required', 'true');
        openModal(userModal);
    });

    userForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const id = document.getElementById('user-id').value;
        
        const userData = {
            username: document.getElementById('username').value,
            fullname: document.getElementById('fullname').value,
            email: document.getElementById('email').value,
            phonenumber: document.getElementById('phonenumber').value,
            role_id: parseInt(document.getElementById('role').value)
        };

        if (id) {
            // Update
            updateUser(id, userData);
        } else {
            // Create
            userData.hashed_password = document.getElementById('password').value;
            createUser(userData);
        }
    });

    confirmDeleteBtn.addEventListener('click', () => {
        if (currentDeleteId) {
            deleteUser(currentDeleteId);
        }
    });

    cancelDeleteBtn.addEventListener('click', () => closeModal(deleteModal));
    userModalCloseBtn.addEventListener('click', () => closeModal(userModal));
    deleteModalCloseBtn.addEventListener('click', () => closeModal(deleteModal));

    userModalOverlay.addEventListener('click', (e) => {
        if (e.target === userModalOverlay) closeModal(userModal);
    });
    deleteModalOverlay.addEventListener('click', (e) => {
        if (e.target === deleteModalOverlay) closeModal(deleteModal);
    });

    // Initial Load
    fetchRoles();
    fetchUsers();
});

        // Here you would typically send a request to the server to delete the user
        console.log('User deleted');
        closeModal(deleteModal);
        // You might want to remove the row from the table here
    ;

    document.getElementById('cancel-delete-btn').addEventListener('click', () => {
        closeModal(deleteModal);
    });
;
