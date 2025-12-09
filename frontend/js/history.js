document.addEventListener("DOMContentLoaded", async () => {
    const token = sessionStorage.getItem("access_token");

    if (!token) {
        alert("You must login first!");
        window.location.href = "login.html";
        return;
    }

    await loadBookingHistory(token);

    // ===== REVIEW FORM =====
    const reviewForm = document.getElementById("review-form");
    if (reviewForm) {
        reviewForm.addEventListener("submit", submitReview);
    }

    // ===== ISSUE FORM =====
    const issueForm = document.getElementById("issue-form");
    if (issueForm) {
        issueForm.addEventListener("submit", submitIssue);
    }
});

// ========================= GLOBAL STATE =========================
let currentTransactionID = null;
let currentRoomID = null;

let currentIssueTransactionID = null;
let currentIssueRoomID = null;

// ========================= LOAD BOOKING HISTORY =========================
async function loadBookingHistory(token) {
    try {
        const res = await fetch("http://127.0.0.1:8000/booking/booking-history", {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        });

        const data = await res.json();
        console.log("Booking History:", data);

        if (!Array.isArray(data)) {
            console.error("Dữ liệu booking không hợp lệ:", data);
            return;
        }

        const tbody = document.querySelector("tbody");
        if (!tbody) return;
        tbody.innerHTML = "";

        data.forEach(bk => {
            const tr = document.createElement("tr");

            tr.innerHTML = `
                <td>${formatDate(bk.checkIn)}</td>
                <td>${bk.roomType} (Room ${bk.roomNumber})</td>
                <td>${bk.status}</td>
                <td class="actions"></td>
            `;

            const actionsTd = tr.querySelector(".actions");

            if (bk.status && bk.status.toLowerCase() === "paid") {
                // REVIEW BUTTON
                const btnReview = document.createElement("button");
                btnReview.className = "review-btn";
                btnReview.textContent = "Leave a Review";
                btnReview.onclick = () => openReviewModal(bk);

                // REPORT BUTTON
                const btnReport = document.createElement("button");
                btnReport.className = "report-btn";
                btnReport.textContent = "Report Issue";
                btnReport.onclick = () => openIssueModal(bk);

                actionsTd.appendChild(btnReview);
                actionsTd.appendChild(btnReport);
            }

            tbody.appendChild(tr);
        });

    } catch (error) {
        console.error("Error:", error);
        alert("Failed to load booking history");
    }
}

// ========================= FORMAT DATE =========================
function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString("vi-VN");
}

// ========================= REVIEW MODAL =========================
const reviewOverlay = document.getElementById("review-overlay");
const reviewModal = document.getElementById("review-modal");
const closeReviewBtn = reviewModal ? reviewModal.querySelector(".close-btn") : null;

function openReviewModal(bk) {
    currentTransactionID = bk.id;
    currentRoomID = bk.RoomID;

    if (!reviewOverlay || !reviewModal) return;

    reviewOverlay.style.display = "block";
    reviewModal.style.display = "block";
    document.body.classList.add("modal-open");
}

function closeReviewModal() {
    if (!reviewOverlay || !reviewModal) return;

    reviewOverlay.style.display = "none";
    reviewModal.style.display = "none";
    document.body.classList.remove("modal-open");
}

if (reviewOverlay) reviewOverlay.onclick = closeReviewModal;
if (closeReviewBtn) closeReviewBtn.onclick = closeReviewModal;

async function submitReview(e) {
    e.preventDefault();

    const token = sessionStorage.getItem("access_token");
    const rating = Number(document.getElementById("rating").value);
    const comment = document.getElementById("review-text").value;

    if (!currentTransactionID || !currentRoomID) {
        alert("Missing booking info!");
        return;
    }

    const bodyData = {
        transaction_id: currentTransactionID,
        room_id: currentRoomID,
        rating: rating,
        comment: comment
    };

    try {
        const res = await fetch("http://127.0.0.1:8000/review/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(bodyData)
        });

        const result = await res.json();

        if (!res.ok) {
            alert(result.detail || "Review failed!");
            return;
        }

        alert("Review submitted successfully!");
        closeReviewModal();
        document.getElementById("review-text").value = ""; // reset textarea
        document.getElementById("rating").value = 0; // reset rating input
    } catch (err) {
        console.error(err);
        alert("Error submitting review");
    }
}


// ========================= ISSUE MODAL =========================
const issueOverlay = document.getElementById("issue-overlay");
const issueModal = document.getElementById("issue-modal");
const closeIssueBtn = document.getElementById("close-issue");

function openIssueModal(bk) {
    currentIssueTransactionID = bk.id;
    currentIssueRoomID = bk.RoomID;

    if (!issueOverlay || !issueModal) return;

    issueOverlay.style.display = "block";
    issueModal.style.display = "block";
}

function closeIssueModal() {
    if (!issueOverlay || !issueModal) return;

    issueOverlay.style.display = "none";
    issueModal.style.display = "none";
}

if (issueOverlay) issueOverlay.onclick = closeIssueModal;
if (closeIssueBtn) closeIssueBtn.onclick = closeIssueModal;

async function submitIssue(e) {
    e.preventDefault();

    const token = sessionStorage.getItem("access_token");
    const description = document.getElementById("issue-text").value;

    if (!currentIssueTransactionID || !currentIssueRoomID) {
        alert("Missing booking info!");
        return;
    }

    const bodyData = {
        transaction_id: currentIssueTransactionID,
        room_id: currentIssueRoomID,
        description: description
    };

    try {
        const res = await fetch("http://127.0.0.1:8000/incident/report", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(bodyData)
        });

        const result = await res.json();

        if (!res.ok) {
            return alert(result.detail || "Failed to report issue");
        }

        alert("Issue reported successfully!");
        closeIssueModal();
        document.getElementById("issue-text").value = ""; // reset textarea
    } catch (err) {
        console.error(err);
        alert("Error sending report");
    }
}


// ========================= STAR RATING =========================
const starElements = document.querySelectorAll(".star");
const ratingInput = document.getElementById("rating");

starElements.forEach(star => {
    star.addEventListener("mouseover", () => {
        const value = star.dataset.value;
        starElements.forEach(s => s.classList.toggle("hovered", s.dataset.value <= value));
    });
    star.addEventListener("mouseout", () => {
        starElements.forEach(s => s.classList.remove("hovered"));
    });
    star.addEventListener("click", () => {
        const value = star.dataset.value;
        ratingInput.value = value;
        starElements.forEach(s => s.classList.toggle("selected", s.dataset.value <= value));
    });
});

// ========================= SHOW ISSUE TEXTAREA =========================
const reportCheck = document.getElementById("report-check");
if (reportCheck) {
    reportCheck.addEventListener("change", function() {
        const issueBox = document.getElementById("issue-box");
        issueBox.style.display = this.checked ? "block" : "none";
    });
}
