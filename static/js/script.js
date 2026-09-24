(function () {
    'use strict';
    var sidebar = document.getElementById('sidebar');
    var overlay = document.getElementById('sidebarOverlay');
    var toggleBtn = document.getElementById('sidebarToggle');

    function openSidebar() { sidebar.classList.add('open'); overlay.classList.add('show'); document.body.style.overflow = 'hidden'; }
    function closeSidebar() { sidebar.classList.remove('open'); overlay.classList.remove('show'); document.body.style.overflow = ''; }

    if (toggleBtn) {
        toggleBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            sidebar.classList.contains('open') ? closeSidebar() : openSidebar();
        });
    }
    if (overlay) overlay.addEventListener('click', closeSidebar);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && sidebar.classList.contains('open')) closeSidebar(); });

    var darkToggle = document.getElementById('darkModeToggle');
    var html = document.documentElement;
    function setTheme(theme) {
        html.setAttribute('data-bs-theme', theme);
        localStorage.setItem('recruitpro-theme', theme);
        if (darkToggle) darkToggle.innerHTML = theme === 'dark' ? '<i class="bi bi-sun-fill"></i>' : '<i class="bi bi-moon-fill"></i>';
    }
    if (darkToggle) {
        var savedTheme = localStorage.getItem('recruitpro-theme') || 'light';
        setTheme(savedTheme);
        darkToggle.addEventListener('click', function () {
            setTheme(html.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark');
        });
    }

    var globalSearch = document.getElementById('globalSearch');
    if (globalSearch) {
        globalSearch.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                var query = this.value.trim();
                if (query) window.location.href = '/candidates?search=' + encodeURIComponent(query);
            }
        });
    }

    var dropdownTriggers = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    document.addEventListener('click', function () {
        document.querySelectorAll('.dropdown-menu.show').forEach(function (m) { m.classList.remove('show'); });
    });
    dropdownTriggers.forEach(function (trigger) {
        trigger.addEventListener('click', function (e) {
            e.preventDefault(); e.stopPropagation();
            var menu = this.nextElementSibling;
            if (menu && menu.classList.contains('dropdown-menu')) {
                document.querySelectorAll('.dropdown-menu.show').forEach(function (m) { m.classList.remove('show'); });
                if (!menu.classList.contains('show')) menu.classList.add('show');
            }
        });
    });

    var selectFilters = document.querySelectorAll('.filter-select');
    selectFilters.forEach(function (s) {
        s.addEventListener('change', function () { if (this.form) this.form.submit(); });
    });

    var tooltipTriggers = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggers.length && typeof bootstrap !== 'undefined') {
        tooltipTriggers.forEach(function (el) { new bootstrap.Tooltip(el); });
    }
})();