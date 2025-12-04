document.addEventListener('DOMContentLoaded', () => {
    const reviewModal = document.getElementById('review-modal');

    const openModal = (modal) => {
        modal.querySelector('.modal-overlay').style.display = 'flex';
    };
    const closeModal = (modal) => {
        modal.querySelector('.modal-overlay').style.display = 'none';
    };

    // Generic close behavior
    const overlay = reviewModal.querySelector('.modal-overlay');
    const closeBtn = reviewModal.querySelector('.close-btn');
    if (overlay) {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) closeModal(reviewModal);
        });
    }
    if (closeBtn) {
        closeBtn.addEventListener('click', () => closeModal(reviewModal));
    }

    // Open Review Modal
    document.querySelectorAll('.review-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            openModal(reviewModal);
        });
    });

    // Handle review submission
    document.getElementById('review-form').addEventListener('submit', (e) => {
        e.preventDefault();
        alert('Thank you for your review!');
        closeModal(reviewModal);
    });
});
