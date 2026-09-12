const registerForm =
    document.getElementById("registerForm");

const loginForm =
    document.getElementById("loginForm");

const logoutButton =
    document.getElementById("logoutButton");

const dashboardButton =
    document.getElementById("dashboardButton");


// -------------------------
// DASHBOARD BUTTON ON HOME
// -------------------------

if (dashboardButton) {

    dashboardButton.addEventListener(
        "click",
        function () {

            const accessToken =
                localStorage.getItem("access_token");


            const dashboardMessage =
                document.getElementById(
                    "dashboardMessage"
                );


            if (!accessToken) {

                dashboardMessage.textContent =
                    "Please login first.";

                return;
            }


            window.location.href =
                "/dashboard-page";

        }
    );

}


// -------------------------
// REFRESH ACCESS TOKEN
// -------------------------

async function refreshAccessToken() {

    const refreshToken =
        localStorage.getItem("refresh_token");


    if (!refreshToken) {

        return false;
    }


    const response = await fetch("/refresh", {

        method: "POST",

        headers: {
            "Authorization":
                `Bearer ${refreshToken}`
        }

    });


    const data =
        await response.json();


    if (!response.ok) {

        localStorage.removeItem(
            "access_token"
        );

        localStorage.removeItem(
            "refresh_token"
        );

        return false;
    }


    localStorage.setItem(
        "access_token",
        data.access_token
    );


    return true;
}


// -------------------------
// REGISTER
// -------------------------

if (registerForm) {

    const nameInput =
        document.getElementById("name");

    const emailInput =
        document.getElementById("email");

    const passwordInput =
        document.getElementById("password");

    const message =
        document.getElementById("message");


    registerForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const name =
                nameInput.value.trim();

            const email =
                emailInput.value.trim();

            const password =
                passwordInput.value;


            if (
                name === "" ||
                email === "" ||
                password === ""
            ) {

                message.textContent =
                    "Please fill in all fields.";

                return;
            }


            if (password.length < 8) {

                message.textContent =
                    "Password must be at least 8 characters.";

                return;
            }


            const response =
                await fetch("/register", {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        name: name,

                        email: email,

                        password: password

                    })

                });


            const data =
                await response.json();


            message.textContent =
                data.message;

        }
    );

}


// -------------------------
// LOGIN
// -------------------------

if (loginForm) {

    const emailInput =
        document.getElementById("email");

    const passwordInput =
        document.getElementById("password");

    const message =
        document.getElementById("message");


    loginForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const email =
                emailInput.value.trim();

            const password =
                passwordInput.value;


            if (
                email === "" ||
                password === ""
            ) {

                message.textContent =
                    "Please enter email and password.";

                return;
            }


            const response =
                await fetch("/login", {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        email: email,

                        password: password

                    })

                });


            const data =
                await response.json();


            if (response.ok) {

                localStorage.setItem(
                    "access_token",
                    data.access_token
                );

                localStorage.setItem(
                    "refresh_token",
                    data.refresh_token
                );

                window.location.href =
                    "/dashboard-page";

                return;
            }


            message.textContent =
                data.message;

        }
    );

}


// -------------------------
// DASHBOARD
// -------------------------

if (
    window.location.pathname ===
    "/dashboard-page"
) {

    const message =
        document.getElementById("message");

    const userId =
        document.getElementById("userId");


    async function loadDashboard() {

        let accessToken =
            localStorage.getItem(
                "access_token"
            );


        if (!accessToken) {

            message.textContent =
                "You are not logged in.";

            return;
        }


        let response =
            await fetch("/dashboard", {

                method: "GET",

                headers: {
                    "Authorization":
                        `Bearer ${accessToken}`
                }

            });


        let data =
            await response.json();


        // Access token expired

        if (
            data.code ===
            "access_token_expired"
        ) {

            message.textContent =
                "Access token expired. Refreshing...";


            const refreshed =
                await refreshAccessToken();


            if (!refreshed) {

                message.textContent =
                    "Your session has expired. Please login again.";

                return;
            }


            accessToken =
                localStorage.getItem(
                    "access_token"
                );


            response =
                await fetch("/dashboard", {

                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${accessToken}`
                    }

                });


            data =
                await response.json();

        }


        if (!response.ok) {

            message.textContent =
                data.message ||
                "Access denied.";

            return;
        }


        message.textContent =
            data.message;


        userId.textContent =
            `Your user ID is: ${data.user_id}`;

    }


    loadDashboard();

}


// -------------------------
// LOGOUT
// -------------------------

if (logoutButton) {

    logoutButton.addEventListener(
        "click",
        function () {

            localStorage.removeItem(
                "access_token"
            );

            localStorage.removeItem(
                "refresh_token"
            );


            window.location.href = "/";

        }
    );

}