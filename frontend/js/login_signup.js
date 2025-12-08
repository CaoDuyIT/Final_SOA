//=================== FUNCTION LOGIN ===================
const loginForm = document.getElementById("login-form");
if (loginForm) {
    loginForm.addEventListener("submit", login);
}

async function login(event) {
    event.preventDefault();

    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    try {
        const response = await fetch("http://127.0.0.1:8000/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            const err = await response.json();
            alert(err.detail);
            return;
        }

        const data = await response.json();
        sessionStorage.setItem("access_token", data.access_token);

        window.location.href = "index.html";
    } catch (error) {
        console.error("Error:", error);
        alert("Cannot connect to server.");
    }
}


//=================== FUNCTION SIGN UP ===================
const signupForm = document.getElementById("signup-form");
if (signupForm) {
    signupForm.addEventListener("submit", signup);
}

async function signup(event) {
    event.preventDefault();

    const username = document.getElementById("signup-username").value;
    const fullname = document.getElementById("signup-fullname").value;
    const email = document.getElementById("signup-email").value;
    const phone = document.getElementById("signup-phone").value;
    const password = document.getElementById("signup-password").value;
    const password_checker = document.getElementById("signup-password-checker").value;

    if (password !== password_checker) {
        alert("Password does not match");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/users/add-customer/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username: username,
                fullname: fullname,
                email: email,
                phonenumber: phone,
                hashed_password: password
            })
        });

        if (!response.ok) {
            const err = await response.json();
            alert(err.detail);
            return;
        }

        alert("Signup successful!");
        window.location.href = "login.html";

    } catch (error) {
        console.error("Error:", error);
        alert("Cannot connect to server.");
    }
}
