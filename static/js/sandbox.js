/* Coding Sandbox: drafts, timer, real execution, tests, hints and history. */
(function () {
    'use strict';

    var DATA = window.RP_SANDBOX;
    if (!DATA) return;

    var HINTS = window.RP_HINTS || [];
    var LANGUAGES = ['python', 'javascript', 'java', 'c++'];
    var SUPPORTED = ['python', 'javascript'];
    var LABELS = { python: 'Python', javascript: 'JavaScript', java: 'Java', 'c++': 'C++' };
    var EXTENSIONS = { python: 'py', javascript: 'js', java: 'java', 'c++': 'cpp' };

    var DRAFT_PREFIX = 'recruitpro-draft:' + DATA.slug + ':';
    var LANG_KEY = 'recruitpro-lang:' + DATA.slug;
    var TIMER_KEY = 'recruitpro-timer:' + DATA.slug;
    var FONT_KEY = 'recruitpro-font';

    function $(id) { return document.getElementById(id); }
    function getStore(key) { try { return window.localStorage.getItem(key); } catch (e) { return null; } }
    function setStore(key, value) { try { window.localStorage.setItem(key, value); } catch (e) {} }
    function removeStore(key) { try { window.localStorage.removeItem(key); } catch (e) {} }

    var codeEl = $('sandbox-code');
    var linesEl = $('sandbox-lines');
    var editorEl = document.querySelector('.sandbox-editor');
    var scrollerEl = document.querySelector('.sandbox-editor .code-content');
    var langEl = $('sandbox-lang');
    var outEl = $('sandbox-output');
    var runBtn = $('sandbox-run');
    var submitBtn = $('sandbox-submit');
    var resetBtn = $('sandbox-reset');
    var hintBtn = $('hint-btn');
    var hintList = $('hint-list');
    var solutionBtn = $('solution-btn');
    var historyEl = $('sandbox-history');
    var historyAll = $('history-all');
    var timerEl = $('sandbox-timer');
    var attemptsEl = $('sandbox-attempts');
    var bestEl = $('sandbox-best');
    var problemSelect = $('problem-select');

    if (!codeEl || !langEl) return;

    var currentLang = 'python';
    var bestScore = DATA.best || 0;
    var busy = false;

    function labelFor(lang) { return LABELS[lang] || lang; }
    function isSupported(lang) { return SUPPORTED.indexOf(lang) !== -1; }
    function starterFor(lang) {
        var starters = DATA.starters || {};
        return typeof starters[lang] === 'string' ? starters[lang] : '';
    }
    function draftKey(lang) { return DRAFT_PREFIX + lang; }

    function getCode() {
        return (codeEl.innerText || '').replace(/\u00a0/g, ' ').replace(/\r\n/g, '\n');
    }

    function updateLines() {
        var count = getCode().split('\n').length;
        var frag = document.createDocumentFragment();
        for (var i = 1; i <= count; i++) {
            var span = document.createElement('span');
            span.textContent = String(i);
            frag.appendChild(span);
        }
        linesEl.innerHTML = '';
        linesEl.appendChild(frag);
    }

    function saveDraft() {
        setStore(draftKey(currentLang), getCode());
    }

    function setOutput(text) {
        outEl.textContent = text;
    }

    updateLines();
    if (scrollerEl) {
        scrollerEl.addEventListener('scroll', function () {
            linesEl.scrollTop = scrollerEl.scrollTop;
        });
    }

    /* ---------- initial code: pending cross-problem load > draft > starter ---------- */
    var savedLang = getStore(LANG_KEY);
    if (savedLang && LANGUAGES.indexOf(savedLang) !== -1) currentLang = savedLang;

    var pending = null;
    var pendingRaw = getStore('recruitpro-load:' + DATA.slug);
    if (pendingRaw) {
        try { pending = JSON.parse(pendingRaw); } catch (e) { pending = null; }
        removeStore('recruitpro-load:' + DATA.slug);
    }
    if (pending && pending.language && LANGUAGES.indexOf(pending.language) !== -1) {
        currentLang = pending.language;
    }
    langEl.value = currentLang;

    var initialCode = (pending && typeof pending.code === 'string')
        ? pending.code : getStore(draftKey(currentLang));
    if ((initialCode === null || initialCode === undefined) && !pending
            && DATA.slug === 'two-sum' && currentLang === 'python') {
        initialCode = getStore('recruitpro-sandbox-draft');
    }
    if (initialCode === null || initialCode === undefined) initialCode = starterFor(currentLang);

    codeEl.textContent = initialCode;
    updateLines();
    saveDraft();

    /* ---------- font size ---------- */
    var fontSize = parseInt(getStore(FONT_KEY) || '13', 10);
    if (isNaN(fontSize) || fontSize < 11 || fontSize > 20) fontSize = 13;
    function applyFont() {
        if (editorEl) editorEl.style.fontSize = fontSize + 'px';
        setStore(FONT_KEY, String(fontSize));
    }
    applyFont();
    $('font-up').addEventListener('click', function () {
        if (fontSize < 20) { fontSize += 1; applyFont(); }
    });
    $('font-down').addEventListener('click', function () {
        if (fontSize > 11) { fontSize -= 1; applyFont(); }
    });

    /* ---------- timer ---------- */
    var limitSeconds = (DATA.time_limit_minutes || 30) * 60;
    var timerStart = parseInt(getStore(TIMER_KEY) || '0', 10);
    if (!timerStart || isNaN(timerStart)) {
        timerStart = Date.now();
        setStore(TIMER_KEY, String(timerStart));
    }
    function secondsLeft() {
        return Math.max(0, limitSeconds - Math.floor((Date.now() - timerStart) / 1000));
    }
    function formatTime(total) {
        var minutes = Math.floor(total / 60);
        var seconds = total % 60;
        return (minutes < 10 ? '0' : '') + minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
    }
    function paintTimer() {
        if (!timerEl) return;
        var left = secondsLeft();
        timerEl.textContent = formatTime(left);
        if (left <= 300) timerEl.classList.add('text-danger');
        else timerEl.classList.remove('text-danger');
    }
    setInterval(paintTimer, 1000);
    paintTimer();
    $('timer-reset').addEventListener('click', function () {
        timerStart = Date.now();
        setStore(TIMER_KEY, String(timerStart));
        paintTimer();
        setOutput('Practice timer reset to ' + formatTime(limitSeconds) + '.');
    });
    function elapsedSeconds() {
        return Math.min(limitSeconds, Math.max(0, Math.floor((Date.now() - timerStart) / 1000)));
    }

    /* ---------- editor behaviour ---------- */
    function insertText(text) {
        codeEl.focus();
        if (document.execCommand) {
            document.execCommand('insertText', false, text);
        } else {
            var sel = window.getSelection();
            if (sel && sel.rangeCount) {
                var range = sel.getRangeAt(0);
                range.deleteContents();
                range.insertNode(document.createTextNode(text));
                range.collapse(false);
            }
        }
        updateLines();
        saveDraft();
    }

    codeEl.addEventListener('input', function () {
        updateLines();
        saveDraft();
    });

    codeEl.addEventListener('keydown', function (event) {
        if (event.key === 'Tab') {
            event.preventDefault();
            insertText('    ');
        } else if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            event.preventDefault();
            execute('run');
        }
    });

    codeEl.addEventListener('paste', function (event) {
        var clipboard = event.clipboardData || window.clipboardData;
        if (!clipboard) return;
        event.preventDefault();
        insertText(clipboard.getData('text'));
    });

    document.addEventListener('keydown', function (event) {
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter'
                && document.activeElement !== codeEl) {
            event.preventDefault();
            execute('run');
        }
    });

    document.getElementById('copy-code').addEventListener('click', function () {
        var text = getCode();
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(function () {
                setOutput('Code copied to the clipboard.');
            }, function () { fallbackCopy(text); });
        } else {
            fallbackCopy(text);
        }
    });

    function fallbackCopy(text) {
        var area = document.createElement('textarea');
        area.value = text;
        area.style.position = 'fixed';
        area.style.opacity = '0';
        document.body.appendChild(area);
        area.select();
        try {
            document.execCommand('copy');
            setOutput('Code copied to the clipboard.');
        } catch (e) {
            setOutput('Could not copy the code.');
        }
        document.body.removeChild(area);
    }

    document.getElementById('download-code').addEventListener('click', function () {
        var blob = new Blob([getCode()], { type: 'text/plain;charset=utf-8' });
        var link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = DATA.slug + '.' + (EXTENSIONS[currentLang] || 'txt');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        setTimeout(function () { URL.revokeObjectURL(link.href); }, 1000);
    });

    /* ---------- language switching ---------- */
    langEl.addEventListener('change', function () {
        saveDraft();
        var next = langEl.value;
        if (LANGUAGES.indexOf(next) === -1) next = 'python';
        currentLang = next;
        setStore(LANG_KEY, currentLang);
        var draft = getStore(draftKey(currentLang));
        codeEl.textContent = (draft === null || draft === undefined) ? starterFor(currentLang) : draft;
        updateLines();
        saveDraft();
        if (isSupported(currentLang)) {
            setOutput('Switched to ' + labelFor(currentLang) + '. Press Run to execute your code.');
        } else {
            setOutput(labelFor(currentLang) + ' cannot run in this local demo. Python and JavaScript are supported.');
        }
    });

    if (!isSupported(currentLang)) {
        setOutput(labelFor(currentLang) + ' cannot run in this local demo. Python and JavaScript are supported.');
    }

    /* ---------- problem switching ---------- */
    if (problemSelect) {
        problemSelect.addEventListener('change', function () {
            saveDraft();
            window.location.href = window.location.pathname + '?problem=' + encodeURIComponent(problemSelect.value);
        });
    }

    /* ---------- tests ---------- */
    function resetTests() {
        var rows = document.querySelectorAll('#test-cases .test-result');
        for (var i = 0; i < rows.length; i++) {
            var row = rows[i];
            row.classList.remove('pass', 'fail');
            var icon = row.querySelector('i');
            if (icon) icon.className = 'bi bi-circle text-secondary';
            var badge = row.querySelector('.result-badge');
            if (badge) {
                badge.className = 'result-badge pending';
                badge.textContent = 'PENDING';
            }
            var got = row.querySelector('.test-got');
            if (got) {
                got.classList.add('d-none');
                got.textContent = '';
            }
        }
        var scoreEl = $('test-score');
        if (scoreEl) scoreEl.textContent = '--';
    }

    function updateTests(results) {
        for (var i = 0; i < results.length; i++) {
            var row = $('test-row-' + i);
            if (!row) continue;
            var item = results[i] || { ok: false, got: '' };
            row.classList.remove('pass', 'fail');
            row.classList.add(item.ok ? 'pass' : 'fail');
            var icon = row.querySelector('i');
            if (icon) icon.className = item.ok ? 'bi bi-check-circle-fill' : 'bi bi-x-circle-fill';
            var badge = row.querySelector('.result-badge');
            if (badge) {
                badge.className = 'result-badge ' + (item.ok ? 'pass' : 'fail');
                badge.textContent = item.ok ? 'PASS' : 'FAIL';
            }
            var got = row.querySelector('.test-got');
            if (got) {
                got.classList.remove('d-none');
                got.classList.remove('text-danger');
                got.classList.add(item.ok ? 'text-success' : 'text-danger');
                got.textContent = 'Got: ' + (item.got === undefined ? '' : item.got);
            }
        }
    }

    /* ---------- execute / submit ---------- */
    function setBusy(state) {
        busy = state;
        runBtn.disabled = state;
        submitBtn.disabled = state;
        runBtn.innerHTML = state
            ? '<span class="spinner-border spinner-border-sm"></span> Running...'
            : '<i class="bi bi-play-fill"></i> Run Code';
        submitBtn.innerHTML = state
            ? '<span class="spinner-border spinner-border-sm"></span> Checking...'
            : '<i class="bi bi-send-fill"></i> Submit';
    }

    function execute(mode) {
        if (busy) return;
        if (!isSupported(currentLang)) {
            setOutput(labelFor(currentLang) + ' cannot run in this local demo. Switch to Python or JavaScript.');
            return;
        }
        if (!getCode().trim()) {
            setOutput('Write some code before running it.');
            return;
        }

        saveDraft();
        setBusy(true);
        if (mode === 'submit') resetTests();
        setOutput(mode === 'submit' ? 'Running all test cases...' : 'Running your code...');

        fetch('/api/sandbox/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                code: getCode(),
                language: currentLang,
                mode: mode,
                problem_id: DATA.id,
                duration_seconds: elapsedSeconds()
            })
        }).then(function (response) {
            return response.json().then(function (body) {
                return { ok: response.ok, body: body || {} };
            });
        }).then(function (result) {
            var body = result.body;
            if (!result.ok) {
                if (body.results) updateTests(body.results);
                setOutput(body.output || 'Request failed.');
                return;
            }

            if (mode === 'submit') {
                if (body.results) updateTests(body.results);
                var summary = 'Score: ' + body.score + '% (' + body.passed + '/' + body.total + ' passed)';
                var output = body.success
                    ? 'All test cases passed!\n' + summary
                    : 'Some test cases failed.\n' + summary;
                if (body.output) output += '\n\nProgram output:\n' + body.output;
                setOutput(output);
                var scoreEl = $('test-score');
                if (scoreEl) scoreEl.textContent = body.score + '%';

                if (body.attempts !== undefined && attemptsEl) {
                    attemptsEl.textContent = 'Attempts: ' + body.attempts;
                }
                if (body.score !== undefined && body.score > bestScore) {
                    bestScore = body.score;
                    if (bestEl) bestEl.textContent = 'Best: ' + bestScore + '%';
                }
                if (body.attempts !== undefined && body.attempts >= 2) {
                    unlockSolution();
                }
            } else {
                setOutput(body.status === 'success'
                    ? 'Output:\n' + (body.output || '(no output)')
                    : 'Error:\n' + (body.output || 'Code could not run.'));
            }
            loadHistory();
        }).catch(function () {
            setOutput('Server error - your draft is still saved in this browser.');
        }).then(function () {
            setBusy(false);
        });
    }

    runBtn.addEventListener('click', function () { execute('run'); });
    submitBtn.addEventListener('click', function () { execute('submit'); });

    resetBtn.addEventListener('click', function () {
        codeEl.textContent = starterFor(currentLang);
        updateLines();
        saveDraft();
        resetTests();
        setOutput('Code reset to the starter for ' + labelFor(currentLang) + '.');
    });

    /* ---------- hints ---------- */
    var hintIndex = 0;
    function paintHintButton() {
        if (!hintBtn) return;
        if (!HINTS.length) {
            hintBtn.disabled = true;
            hintBtn.textContent = 'No hints for this problem';
            return;
        }
        if (hintIndex >= HINTS.length) {
            hintBtn.disabled = true;
            hintBtn.innerHTML = '<i class="bi bi-check2-circle"></i> All hints shown';
            return;
        }
        hintBtn.disabled = false;
        hintBtn.innerHTML = '<i class="bi bi-lightbulb"></i> Show hint ('
            + (HINTS.length - hintIndex) + ' left)';
    }
    if (hintBtn) {
        hintBtn.addEventListener('click', function () {
            if (hintIndex >= HINTS.length) return;
            var box = document.createElement('div');
            box.className = 'alert alert-info py-2 px-3 small mb-2';
            box.textContent = 'Hint ' + (hintIndex + 1) + ': ' + HINTS[hintIndex];
            hintList.appendChild(box);
            hintIndex += 1;
            paintHintButton();
        });
    }
    paintHintButton();

    /* ---------- reference solution ---------- */
    function unlockSolution() {
        if (!solutionBtn) return;
        solutionBtn.disabled = false;
        solutionBtn.innerHTML = '<i class="bi bi-unlock"></i> Reveal reference solution';
    }

    if (solutionBtn) {
        solutionBtn.addEventListener('click', function () {
            fetch('/api/sandbox/solution/' + DATA.id + '?language=' + encodeURIComponent(currentLang))
                .then(function (response) {
                    return response.json().then(function (body) {
                        return { ok: response.ok, body: body || {} };
                    });
                }).then(function (result) {
                    if (!result.ok) {
                        setOutput(result.body.error || 'The reference solution is locked.');
                        return;
                    }
                    var solution = result.body.code || '';
                    if (!solution) {
                        setOutput('No reference solution is available for this language.');
                        return;
                    }
                    setStore(draftKey(currentLang) + ':backup', getCode());
                    if (result.body.language && result.body.language !== currentLang) {
                        currentLang = result.body.language;
                        langEl.value = currentLang;
                    }
                    codeEl.textContent = solution;
                    updateLines();
                    saveDraft();
                    setOutput('Reference solution loaded. Your previous code was backed up in this browser.');
                }).catch(function () {
                    setOutput('Could not load the reference solution.');
                });
        });
    }

    /* ---------- history ---------- */
    function historyItem(item) {
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'list-group-item list-group-item-action';

        var top = document.createElement('div');
        top.className = 'd-flex justify-content-between align-items-center gap-2';
        var title = document.createElement('span');
        title.className = 'fw-semibold';
        title.textContent = '#' + item.id + ' - ' + item.problem_title;
        var badge = document.createElement('span');
        if (item.is_submission) {
            badge.className = 'badge-custom ' + (item.score === 100 ? 'badge-completed' : 'badge-rejected');
            badge.textContent = item.score + '%';
        } else {
            badge.className = 'badge-custom badge-interview';
            badge.textContent = 'RUN';
        }
        top.appendChild(title);
        top.appendChild(badge);

        var meta = document.createElement('div');
        meta.className = 'text-secondary small mt-1';
        meta.textContent = item.language + ' - ' + item.created_at
            + (item.is_submission ? ' - ' + item.passed + '/' + item.total + ' tests' : '');

        var preview = document.createElement('div');
        preview.className = 'text-secondary small mt-1';
        preview.style.overflow = 'hidden';
        preview.style.textOverflow = 'ellipsis';
        preview.style.whiteSpace = 'nowrap';
        preview.textContent = item.code_preview;

        button.appendChild(top);
        button.appendChild(meta);
        button.appendChild(preview);
        button.addEventListener('click', function () { loadExecution(item.id); });
        return button;
    }

    function loadHistory() {
        if (!historyEl) return;
        var url = '/api/sandbox/history';
        if (!(historyAll && historyAll.checked)) {
            url += '?problem_id=' + encodeURIComponent(DATA.id);
        }
        fetch(url).then(function (response) { return response.json(); }).then(function (items) {
            historyEl.innerHTML = '';
            if (!items || !items.length) {
                var empty = document.createElement('div');
                empty.className = 'list-group-item text-secondary';
                empty.textContent = historyAll && historyAll.checked
                    ? 'No saved runs yet.' : 'No runs for this problem yet.';
                historyEl.appendChild(empty);
                return;
            }
            for (var i = 0; i < items.length; i++) {
                historyEl.appendChild(historyItem(items[i]));
            }
        }).catch(function () {
            historyEl.innerHTML = '<div class="list-group-item text-secondary">Could not load history.</div>';
        });
    }

    if (historyAll) historyAll.addEventListener('change', loadHistory);

    function loadExecution(id) {
        fetch('/api/sandbox/load/' + id).then(function (response) {
            return response.json();
        }).then(function (data) {
            if (!data || data.error) {
                setOutput((data && data.error) || 'Could not load that run.');
                return;
            }
            if (data.problem_slug && data.problem_id !== DATA.id) {
                setStore('recruitpro-load:' + data.problem_slug, JSON.stringify({
                    code: data.code,
                    language: data.language
                }));
                window.location.href = window.location.pathname + '?problem='
                    + encodeURIComponent(data.problem_slug);
                return;
            }
            if (data.language && LANGUAGES.indexOf(data.language) !== -1) {
                currentLang = data.language;
                langEl.value = currentLang;
                setStore(LANG_KEY, currentLang);
            }
            codeEl.textContent = data.code || '';
            updateLines();
            saveDraft();
            if (data.details && data.details.length) updateTests(data.details);
            else resetTests();

            var message = 'Loaded run #' + id + ' (' + (data.problem_title || DATA.title)
                + ', ' + labelFor(data.language || currentLang) + ').';
            if (data.is_submission) {
                message += '\nScore: ' + data.score + '% (' + data.passed + '/' + data.total + ' passed)';
            }
            if (data.output) message += '\n\n' + data.output;
            setOutput(message);
        }).catch(function () {
            setOutput('Could not load that run.');
        });
    }

    loadHistory();
})();
