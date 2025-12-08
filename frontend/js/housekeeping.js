document.addEventListener('DOMContentLoaded', () => {
    const roomTableBody = document.querySelector('#rooms-to-clean-table tbody');

    roomTableBody.addEventListener('click', (e) => {
        if (e.target.tagName === 'BUTTON') {
            const button = e.target;
            const row = button.closest('tr');
            const statusCell = row.querySelector('.status');
            const currentStatus = statusCell.textContent.trim();

            let nextStatus = '';
            let nextButtonText = '';
            let nextButtonClass = '';

            switch (currentStatus) {
                case 'Needs Cleaning':
                    nextStatus = 'In Progress';
                    nextButtonText = 'Mark as Available';
                    nextButtonClass = 'action-btn';
                    break;
                case 'In Progress':
                    nextStatus = 'Available';
                    nextButtonText = 'Mark as Needs Cleaning';
                    nextButtonClass = 'delete-btn'; // Using delete style for "resetting"
                    break;
                case 'Available':
                    nextStatus = 'Needs Cleaning';
                    nextButtonText = 'Mark as In Progress';
                    nextButtonClass = 'edit-btn';
                    break;
            }

            // Update the UI
            statusCell.textContent = nextStatus;
            button.textContent = nextButtonText;
            button.className = `btn ${nextButtonClass}`; // Use a generic 'btn' class + specific one
        }
    });
});
