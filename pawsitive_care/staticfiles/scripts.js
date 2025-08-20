(function () {
    const nav = document.querySelector('.app-navbar');
    const bar = document.getElementById('scrollProgress');

    function onScroll() {
        const doc = document.documentElement;
        const y = doc.scrollTop || document.body.scrollTop;
        const h = doc.scrollHeight - doc.clientHeight;
        const pct = h ? (y / h) * 100 : 0;

        bar.style.width = pct + '%';
        if (y > 8) nav.classList.add('nav-scrolled');
        else nav.classList.remove('nav-scrolled');
    }

    window.addEventListener('scroll', onScroll, {
        passive: true
    });
    document.addEventListener('DOMContentLoaded', onScroll);
})();
