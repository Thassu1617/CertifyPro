document.addEventListener("DOMContentLoaded", () => {
    animateCounters();
    setupFadeIn();
    autoDismissAlerts();
    setupMobileMenu();
});

function animateCounters() {
    document.querySelectorAll(".stat-number[data-target]").forEach(el => {
        const target = parseInt(el.dataset.target);
        if (!target || isNaN(target)) return;
        let current = 0;
        const step = Math.ceil(target / 60);
        const interval = setInterval(() => {
            current += step;
            if (current >= target) {
                current = target;
                clearInterval(interval);
            }
            el.textContent = current;
        }, 25);
    });
}

function setupFadeIn() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll(".fade-in").forEach(el => {
        el.style.opacity = "0";
        el.style.transform = "translateY(20px)";
        el.style.transition = "opacity 0.6s ease, transform 0.6s ease";
        observer.observe(el);
    });
}

document.addEventListener("animationstart", (e) => {
    if (e.target.classList.contains("fade-in")) {
        e.target.style.opacity = "1";
        e.target.style.transform = "translateY(0)";
    }
});

function autoDismissAlerts() {
    document.querySelectorAll(".alert").forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-20px)";
            alert.style.transition = "opacity 0.4s ease, transform 0.4s ease";
            setTimeout(() => alert.remove(), 400);
        }, 5000);
    });
}

function setupMobileMenu() {
    document.querySelector(".nav-toggle")?.addEventListener("click", () => {
        document.querySelector(".nav-links")?.classList.toggle("active");
    });
}

document.addEventListener("click", (e) => {
    const nav = document.querySelector(".nav-links");
    const toggle = document.querySelector(".nav-toggle");
    if (nav?.classList.contains("active") && !nav.contains(e.target) && !toggle?.contains(e.target)) {
        nav.classList.remove("active");
    }
});

function computeInternalTotal() {
    const att = parseFloat(document.getElementById("attendance")?.value) || 0;
    const asn = parseFloat(document.getElementById("assignments")?.value) || 0;
    const quiz = parseFloat(document.getElementById("quiz_scores")?.value) || 0;
    const total = att + asn + quiz;
    const el = document.getElementById("internalTotal");
    if (el) el.textContent = total.toFixed(1) + " / 300";
}
document.querySelectorAll("#attendance, #assignments, #quiz_scores").forEach(el => {
    el?.addEventListener("input", computeInternalTotal);
});
