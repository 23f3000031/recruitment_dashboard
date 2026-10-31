"""Local code execution helpers for the Coding Sandbox.

Runs user code in a separate process with a hard time limit. This is a local
practice runner for a demo project, not a hardened multi-tenant sandbox.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

MAX_OUTPUT = 12000
MAX_CODE_LENGTH = 50000
DEFAULT_TIMEOUT = 5
RUNNABLE_LANGUAGES = ('python', 'javascript')

_RESULT_MARKER = '__RESULT__'


def _creation_flags():
    return subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0


def _run_file(filename, content, build_command, timeout):
    folder = tempfile.mkdtemp(prefix='recruitpro_sbx_')
    path = os.path.join(folder, filename)
    try:
        with open(path, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(content)
        try:
            proc = subprocess.run(
                build_command(path),
                cwd=folder,
                capture_output=True,
                text=True,
                errors='replace',
                timeout=timeout,
                creationflags=_creation_flags(),
            )
        except subprocess.TimeoutExpired:
            return 'timeout', 'Time limit exceeded (%ss). Check for infinite loops.' % timeout
        except FileNotFoundError as exc:
            return 'error', 'Runtime not found: %s' % exc
        except OSError as exc:
            return 'error', 'Could not start the runtime: %s' % exc

        output = proc.stdout or ''
        if proc.stderr:
            output = (output + '\n' if output else '') + proc.stderr
        output = output[:MAX_OUTPUT]
        status = 'success' if proc.returncode == 0 else 'error'
        return status, output
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def _python_command(path):
    return [sys.executable, '-I', '-B', path]


def _node_command(path):
    return [shutil.which('node') or 'node', path]


def run_source(language, source, timeout=DEFAULT_TIMEOUT):
    """Run a code snippet and return (status, output)."""
    if language == 'python':
        return _run_file('main.py', source, _python_command, timeout)
    if language == 'javascript':
        if not shutil.which('node'):
            return 'error', 'Node.js is not installed on this machine.'
        return _run_file('main.js', source, _node_command, timeout)
    return 'error', 'Only Python and JavaScript can be executed in this local demo.'


def _python_harness(cases, function_name):
    payload = json.dumps(cases)
    return (
        '\n\n# ---- RecruitPro test harness ----\n'
        'import json as __rp_json\n'
        '__rp_cases = __rp_json.loads(%s)\n'
        '__rp_results = []\n'
        'for __rp_case in __rp_cases:\n'
        "    __rp_args = __rp_case.get('args', [])\n"
        "    __rp_expected = __rp_case.get('expected')\n"
        '    try:\n'
        '        __rp_got = %s(*__rp_args)\n'
        '        if isinstance(__rp_got, list) and isinstance(__rp_expected, list):\n'
        '            try:\n'
        '                __rp_ok = sorted(__rp_got) == sorted(__rp_expected)\n'
        '            except TypeError:\n'
        '                __rp_ok = __rp_got == __rp_expected\n'
        '        else:\n'
        '            __rp_ok = __rp_got == __rp_expected\n'
        "        __rp_results.append({'ok': bool(__rp_ok), 'got': repr(__rp_got)[:300]})\n"
        '    except Exception as __rp_err:\n'
        '        __rp_results.append({\'ok\': False, \'got\': (type(__rp_err).__name__ + \': \' + str(__rp_err))[:300]})\n'
        "print('__RESULT__' + __rp_json.dumps(__rp_results))\n"
    ) % (json.dumps(payload), function_name)


def _js_harness(cases, function_name):
    payload = json.dumps(json.dumps(cases))
    return (
        '\n\n// ---- RecruitPro test harness ----\n'
        'const __rpCases = JSON.parse(%s);\n'
        'const __rpResults = [];\n'
        'for (const __rpCase of __rpCases) {\n'
        '    try {\n'
        '        const __rpGot = %s(...__rpCase.args);\n'
        '        let __rpOk;\n'
        '        if (Array.isArray(__rpGot) && Array.isArray(__rpCase.expected)) {\n'
        '            __rpOk = JSON.stringify([...__rpGot].sort()) === JSON.stringify([...__rpCase.expected].sort());\n'
        '        } else {\n'
        '            __rpOk = JSON.stringify(__rpGot) === JSON.stringify(__rpCase.expected);\n'
        '        }\n'
        '        __rpResults.push({ ok: __rpOk, got: JSON.stringify(__rpGot) });\n'
        '    } catch (e) {\n'
        '        __rpResults.push({ ok: false, got: String(e).slice(0, 300) });\n'
        '    }\n'
        '}\n'
        "console.log('__RESULT__' + JSON.stringify(__rpResults));\n"
    ) % (payload, function_name)


def _parse_results(output):
    for line in reversed((output or '').splitlines()):
        if line.startswith(_RESULT_MARKER):
            try:
                parsed = json.loads(line[len(_RESULT_MARKER):])
                if isinstance(parsed, list):
                    cleaned = []
                    for item in parsed:
                        cleaned.append({
                            'ok': bool(item.get('ok')),
                            'got': str(item.get('got', ''))[:300],
                        })
                    return cleaned
            except (ValueError, TypeError):
                return None
    return None


def run_test_cases(language, source, cases, function_name, function_name_js,
                   timeout=DEFAULT_TIMEOUT):
    """Run every test case against the submitted code.

    Returns (status, results, raw_output). results is a list of
    {'ok': bool, 'got': str} in the same order as cases.
    """
    cases = cases or []
    if not cases:
        return 'error', [], 'No test cases configured for this problem.'
    if language == 'python':
        harness = _python_harness(cases, function_name)
        status, output = run_source(language, source + harness, timeout)
    elif language == 'javascript':
        if not shutil.which('node'):
            return 'error', [], 'Node.js is not installed on this machine.'
        harness = _js_harness(cases, function_name_js or function_name)
        status, output = run_source(language, source + harness, timeout)
    else:
        return 'error', [], 'Only Python and JavaScript can be executed in this local demo.'

    results = _parse_results(output)
    if results is None or len(results) != len(cases):
        message = output.strip().splitlines()[-1][:300] if output.strip() else 'No result produced.'
        results = [{'ok': False, 'got': 'Test harness could not run: ' + message} for _ in cases]
        status = 'error'
    clean_output = '\n'.join(
        line for line in (output or '').splitlines()
        if not line.startswith(_RESULT_MARKER))
    return status, results, clean_output[:MAX_OUTPUT]
