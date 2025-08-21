const scrollBar = document.getElementById("scrollProgress");
const navbar = document.querySelector(".app-navbar");

function updateProgress() {
    // place bar just under the navbar
    scrollBar.style.top = navbar.offsetHeight + "px";

    // calculate scroll %
    let scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
    let scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    let scrolled = (scrollTop / scrollHeight) * 100;

    scrollBar.style.width = scrolled + "%";
}

window.addEventListener("scroll", updateProgress);
window.addEventListener("resize", updateProgress);
window.addEventListener("load", updateProgress);
