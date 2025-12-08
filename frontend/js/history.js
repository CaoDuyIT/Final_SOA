document.addEventListener("DOMContentLoaded", async () => {
    const token = sessionStorage.getItem("access_token");

    if (!token) {
        alert("You must login first!");
        window.location.href = "login.html";
        return;
    }

    loadBookingHistory(token);
});

// ========================= LOAD BOOKING HISTORY =============================

async function loadBookingHistory(token) {
    try {
        const res = await fetch("http://127.0.0.1:8000/booking/booking-history", {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        });

        const data = await res.json();
        console.log("Booking History:", data);

        const tbody = document.querySelector("tbody");
        tbody.innerHTML = "";

        data.forEach(bk => {
            const tr = document.createElement("tr");

            tr.innerHTML = `
                <td>${formatDate(bk.bookingDate)}</td>
                <td>${bk.roomType} (Room ${bk.roomNumber})</td>
                <td>${bk.status}</td>
                <td class="actions"></td>
            `;

            const actionsTd = tr.querySelector(".actions");

            // CHỈ HIỆN NÚT REVIEW KHI STATUS = PAID
            if (bk.status.toLowerCase() === "paid") {
                // Nút Review
                const btnReview = document.createElement("button");
                btnReview.className = "review-btn";
                btnReview.textContent = "Leave a Review";
                btnReview.onclick = () => openReviewModal(bk);

                // Nút Report Issue
                const btnReport = document.createElement("button");
                btnReport.className = "report-btn";
                btnReport.textContent = "Report Issue";
                btnReport.onclick = () => openIssueModal(bk);

                actionsTd.appendChild(btnReview);
                actionsTd.appendChild(btnReport);
            }


            tbody.appendChild(tr);
        });
    }
    catch (error) {
        console.error("Error:", error);
        alert("Failed to load booking history");
    }
}

// ========================= FORMAT DATE =============================

function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString("vi-VN");
}

// ========================= MODAL HANDLING ===========================

const reviewModal = document.getElementById("review-modal");
const closeBtn = document.querySelector(".close-btn");

let currentTransactionID = null;

function openReviewModal(bk) {
    currentTransactionID = bk.id;

    document.getElementById("review-overlay").style.display = "block";
    document.getElementById("review-modal").style.display = "block";

    document.body.classList.add("modal-open");
}




function closeReviewModal() {
    document.getElementById("review-overlay").style.display = "none";
    document.getElementById("review-modal").style.display = "none";

    document.body.classList.remove("modal-open");
}

document.querySelector("#review-overlay").onclick = closeReviewModal;
document.querySelector("#review-modal .close-btn").onclick = closeReviewModal;


// ========================= SUBMIT REVIEW =============================

document.getElementById("review-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const token = sessionStorage.getItem("access_token");
    const rating = Number(document.getElementById("rating").value);
    const text = document.getElementById("review-text").value;

    if (!currentTransactionID) {
        alert("Error: Missing booking information!");
        return;
    }

    const bodyData = {
        transaction_id: currentTransactionID,
        rating: rating,
        comment: text
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

    } catch (error) {
        console.error("Error:", error);
        alert("Error submitting review");
    }
});

const starElements = document.querySelectorAll(".star");
const ratingInput = document.getElementById("rating");

// Hover effect
starElements.forEach(star => {
    star.addEventListener("mouseover", () => {
        const value = star.dataset.value;
        starElements.forEach(s => {
            s.classList.toggle("hovered", s.dataset.value <= value);
        });
    });

    star.addEventListener("mouseout", () => {
        starElements.forEach(s => s.classList.remove("hovered"));
    });
});

// Click to select
starElements.forEach(star => {
    star.addEventListener("click", () => {
        const value = star.dataset.value;
        ratingInput.value = value;

        starElements.forEach(s => {
            s.classList.toggle("selected", s.dataset.value <= value);
        });
    });
});

document.getElementById("report-check").addEventListener("change", function () {
    const issueBox = document.getElementById("issue-box");
    issueBox.style.display = this.checked ? "block" : "none";
});

// ============ REPORT ISSUE ==================
let currentIssueTransactionID = null;
let currentIssueRoomID = null;

function openIssueModal(bk) {
    currentIssueTransactionID = bk.id;
    currentIssueRoomID = bk.RoomID;

    document.getElementById("issue-overlay").style.display = "block";
    document.getElementById("issue-modal").style.display = "block";
}

function closeIssueModal() {
    document.getElementById("issue-overlay").style.display = "none";
    document.getElementById("issue-modal").style.display = "none";
}

document.getElementById("issue-overlay").onclick = closeIssueModal;
document.getElementById("close-issue").onclick = closeIssueModal;

document.getElementById("issue-form").addEventListener("submit", async (e) => {
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
        const res = await fetch("http://127.0.0.1:8000/incident/report_incident", {
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

    } catch (err) {
        console.error(err);
        alert("Error sending report");
    }
});
