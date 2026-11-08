"""K4 scratch execution: scrubbed environment, denied network, bounded process group.

All case/test execution uses this module. It never resolves credentials. Python and
packages are read from .venv when present, else the running interpreter; code and a
writable HOME live in a temporary directory.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_VENV = ROOT / ".venv/bin/python"
if hasattr(sys, "_k4_sandbox_mode"):
    PYTHON = Path(sys.executable)
else:
    PYTHON = _VENV if _VENV.exists() else Path(sys.executable)
_MODE = None
_VERIFIED = False
_SELF_TESTING = threading.local()
_PREFLIGHT_LOCK = threading.RLock()


@dataclass
class Result:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool
    seconds: float
    mode: str
    python: str
    cpu_seconds: int
    process_limit: int
    packages: dict = field(default_factory=dict)


def _environment(home):
    return {"PATH": f"{PYTHON.parent}:/usr/bin:/bin:/usr/sbin:/sbin",
            "HOME": str(home), "LANG": "C"}


def _env_command(environment, command):
    return ["/usr/bin/env", "-i", *[f"{k}={v}" for k, v in environment.items()], *command]


def _quick(command, home, timeout=4):
    try:
        return subprocess.run(_env_command(_environment(home), command), env={},
                              capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None


def mode():
    """Select the first usable isolation mechanism without downloading/startup."""
    global _MODE
    if hasattr(sys, "_k4_sandbox_mode"):
        return (sys._k4_sandbox_mode, ["Inherited the enclosing K4 sandbox."])
    if _MODE is not None:
        return _MODE
    notes = []
    with tempfile.TemporaryDirectory(prefix="k4-probe-") as tmp:
        home = Path(tmp)
        unshare = shutil.which("unshare")
        if platform.system() == "Linux" and unshare:
            probe = _quick([unshare, "-rn", "/bin/true"], home)
            if probe and probe.returncode == 0:
                _MODE = ("unshare", notes)
                return _MODE
        notes.append("Linux unshare unavailable or unusable.")
        seatbelt = shutil.which("sandbox-exec")
        if platform.system() == "Darwin" and seatbelt:
            probe = _quick([seatbelt, "-p", "(version 1)(allow default)(deny network*)", "/usr/bin/true"], home)
            if probe and probe.returncode == 0:
                _MODE = ("sandbox-exec", notes)
                return _MODE
        notes.append("macOS sandbox-exec unavailable or unusable; pytest-socket fallback has Python-only coverage.")
        # Last resort is explicit and fails closed if pytest-socket is absent.
        import importlib.util
        if importlib.util.find_spec("pytest_socket") is None:
            raise RuntimeError("No usable network isolation mechanism; install pytest-socket offline dependency.")
        _MODE = ("pytest-socket", notes)
        return _MODE


BOOTSTRAP = r'''
import importlib.metadata, json, os, platform, runpy, sys, tempfile
from pathlib import Path
# No inherited variables, and no bytecode/cache files in the source tree.
os.environ.clear()
os.environ.update({"PATH": sys.argv[1], "HOME": sys.argv[2], "LANG": "C"})
sys.dont_write_bytecode = True
root = Path.cwd()
scratch = root / 'tmp'
scratch.mkdir()
tempfile.tempdir = str(scratch)
sys._k4_sandbox_mode = sys.argv[3]
(root / '_k4_runtime.json').write_text(json.dumps({'python': platform.python_version(),
    'packages': {d.metadata['Name']: d.version for d in importlib.metadata.distributions()}}))
sys.path.insert(0, str(root))
def guard(event, args):
    if event in {"socket.connect", "socket.bind", "socket.getaddrinfo", "socket.sendto"}:
        raise PermissionError("K4 sandbox: network denied")
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        path = Path(os.path.abspath(os.fsdecode(args[0])))
        name = path.name
        if name.startswith(".env") or name in {".netrc", "credentials", "id_rsa", "id_ed25519"}:
            raise PermissionError("K4 sandbox: credential access denied")
        roots = [root, Path(sys.prefix), Path(sys.base_prefix), Path('/System'),
                 Path('/usr'), Path('/Library'), Path('/dev'), Path('/private/var/db')]
        # Also admit each root's resolved form. sys.prefix and sys.base_prefix can be
        # reported through a symlink -- a Homebrew interpreter reports
        # /opt/homebrew/opt/python@X but loads its stdlib from the Cellar path it
        # points at -- and without this the interpreter cannot read its own files.
        # These are the same directories, so nothing new is admitted.
        allowed = []
        for candidate in roots:
            allowed.append(candidate)
            try:
                allowed.append(candidate.resolve())
            except OSError:
                pass
        if not any(path == p or p in path.parents for p in allowed):
            raise PermissionError("K4 sandbox: file outside scratch/runtime denied")
        writing = (args[1] and any(c in args[1] for c in 'wax+')) or (
            isinstance(args[2], int) and args[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
        if writing and root != path and root not in path.parents and str(path) != '/dev/null':
            raise PermissionError("K4 sandbox: write outside scratch denied")
sys.addaudithook(guard)
if sys.argv[3] == "pytest-socket":
    import pytest_socket
    pytest_socket.disable_socket()
args = sys.argv[4:]
if args[0] == "-m":
    sys.argv = [args[1], *args[2:]]
    runpy.run_module(args[1], run_name="__main__", alter_sys=True)
else:
    sys.argv = args
    runpy.run_path(args[0], run_name="__main__")
'''


def _profile(workspace):
    home = Path.home()
    sensitive = [home / p for p in (".ssh", ".aws", ".azure", ".config/gcloud",
                 "Library/Keychains", ".netrc", ".git-credentials")]
    paths = " ".join(f"(subpath {json.dumps(str(p))})" for p in sensitive)
    # OS denies network, known credential paths/names and writes to the source tree.
    # The additional Python guard restricts opens to scratch/runtime. Full native
    # filesystem/process-namespace isolation is not claimed on macOS.
    return ("(version 1)(allow default)(deny network*)"
            "(deny file-read-data " + paths +
            r' (regex #"/[.]env") (regex #"/credentials")'
            r' (regex #"/id_rsa") (regex #"/id_ed25519")' + ")"
            f"(deny file-write* (subpath {json.dumps(str(ROOT))}))")


def run(arguments, files, *, timeout=20, cpu_seconds=15, process_limit=None, git_source=None):
    """Execute Python args against a fresh copy of explicit relative-path files."""
    if not _VERIFIED and not getattr(_SELF_TESTING, "active", False) and not hasattr(sys, "_k4_sandbox_mode"):
        with _PREFLIGHT_LOCK:
            if not _VERIFIED:
                self_test()
    chosen, _ = mode()
    with tempfile.TemporaryDirectory(prefix="k4-sandbox-") as tmp:
        container = Path(tmp).resolve()
        workspace = container / "work"
        if git_source is not None:
            clone_home = container / "git-home"
            clone_home.mkdir()
            cloned = _quick(["/usr/bin/git", "-c", "credential.helper=", "clone", "--quiet",
                            "--no-checkout", "--no-local", "--", str(Path(git_source).resolve()), str(workspace)],
                           clone_home, timeout=60)
            if cloned is None or cloned.returncode:
                raise RuntimeError("Local provenance clone failed before test execution")
        else:
            workspace.mkdir()
        home = workspace / "home"
        home.mkdir()
        if process_limit is None:
            counted = _quick(["/bin/ps", "-u", str(os.getuid()), "-o", "pid="], home)
            if counted is None or counted.returncode:
                raise RuntimeError("Cannot establish safe per-user process limit")
            process_limit = max(128, len(counted.stdout.splitlines()) + 64)
        hard_processes = resource.getrlimit(resource.RLIMIT_NPROC)[1]
        if hard_processes != resource.RLIM_INFINITY:
            process_limit = min(process_limit, hard_processes)
        for relative, body in files.items():
            relative = Path(relative)
            if relative.is_absolute() or ".." in relative.parts or relative.name.startswith(".env"):
                raise ValueError("Unsafe sandbox input path")
            target = workspace / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body if isinstance(body, bytes) else body.encode())
        bootstrap = workspace / "_k4_bootstrap.py"
        bootstrap.write_text(BOOTSTRAP)
        environment = _environment(home)
        command = [str(PYTHON), "-B", str(bootstrap), environment["PATH"],
                   str(home), chosen, *map(str, arguments)]
        inherited = hasattr(sys, "_k4_sandbox_mode")
        if chosen == "sandbox-exec" and not inherited:
            profile = workspace / "_sandbox.sb"
            profile.write_text(_profile(workspace))
            command = ["/usr/bin/sandbox-exec", "-f", str(profile), *command]
        elif chosen == "unshare" and not inherited:
            command = [shutil.which("unshare"), "-rn", *command]

        def limits():
            os.setsid()
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 1))
            hard = resource.getrlimit(resource.RLIMIT_NPROC)[1]
            cap = process_limit if hard == resource.RLIM_INFINITY else min(process_limit, hard)
            resource.setrlimit(resource.RLIMIT_NPROC, (cap, cap))
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

        started = time.monotonic()
        process = subprocess.Popen(_env_command(environment, command), cwd=workspace,
            env={}, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            preexec_fn=limits)
        timed_out = False
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
        receipt = workspace / "_k4_runtime.json"
        runtime = json.loads(receipt.read_text()) if receipt.exists() else {}
        actual_python = runtime.get("python", "UNVERIFIED")
        return Result(process.returncode, stdout, stderr, timed_out,
                      time.monotonic() - started, chosen, actual_python,
                      cpu_seconds, process_limit, runtime.get("packages", {}))


def documents_files(documents):
    """Split banner-delimited shown documents without executing any of their code."""
    import re
    result = {}
    for document in documents:
        current = None
        for line in document.splitlines(keepends=True):
            match = re.fullmatch(r"# ---- (.+) ----\n?", line)
            if match:
                current = match.group(1)
                if current in result:
                    raise ValueError(f"Duplicate shown file: {current}")
                result[current] = ""
            elif current is None:
                raise ValueError("Missing file boundary")
            else:
                result[current] += line
    return result


def run_suite(documents, target="tests", **kwargs):
    return run(["-m", "pytest", "-q", "-p", "no:cacheprovider", target],
               documents_files(documents), **kwargs)

# Which error a blocked connection raises depends on the backend, so the child probe
# ships as its own file rather than a string nested three deep.
_CHILD_NETWORK_CHILD = """\
import errno, socket, sys

TARGET = ("127.0.0.1", 9)

# sandbox-exec and LSM denials surface as EPERM or EACCES. A fresh network namespace
# leaves loopback down instead, and connecting to 127.0.0.1 gives ENETUNREACH. Both
# are denials. ECONNREFUSED is deliberately not in this set: it means the stack routed
# the connection and nothing happened to be listening, so the child was NOT isolated.
# Loopback is the discriminating test for both backends: an unisolated machine always
# reaches it, so ECONNREFUSED here proves isolation failed, and a fresh network
# namespace leaves loopback down so the attempt cannot be refused at all. An external
# address would be weaker, since an unisolated host often cannot route to one either.
DENIED = {errno.EPERM, errno.EACCES, errno.ENETUNREACH, errno.EHOSTUNREACH,
          errno.EAFNOSUPPORT}

try:
    socket.create_connection(TARGET, timeout=0.1).close()
except OSError as error:
    if error.errno in DENIED:
        print("OS_NETWORK_DENIED", errno.errorcode.get(error.errno, error.errno))
        sys.exit(9)
    print("OS_NETWORK_REACHED", errno.errorcode.get(error.errno, error.errno))
    sys.exit(8)
print("OS_NETWORK_CONNECTED")
sys.exit(7)
"""

_CHILD_NETWORK_PROBE = """\
import subprocess, sys

result = subprocess.run([sys.executable, "child_probe.py"], capture_output=True, text=True)
print(result.stdout)
assert result.returncode == 9 and "OS_NETWORK_DENIED" in result.stdout, (
    result.stdout + result.stderr
)
"""


def _self_test_checks():
    checks = {}
    for name, code, timeout, extra in [
        ("network", "import socket; socket.create_connection(('192.0.2.1',443),timeout=.1)", 5, {}),
        ("environment", "import os; print(os.environ['K4_SANDBOX_SECRET_PROBE'])", 5, {}),
        ("infinite_loop", "while True: pass", 2, {}),
        ("normal", "import os; assert set(os.environ)=={'PATH','HOME','LANG'}; print('OK')", 5, {}),
        ("child_network", _CHILD_NETWORK_PROBE, 5,
         {"child_probe.py": _CHILD_NETWORK_CHILD}),
    ]:
        result = run(["probe.py"], {"probe.py": code + "\n", **extra},
                     timeout=timeout, cpu_seconds=2)
        if name in {"normal", "child_network"}:
            passed = result.returncode == 0
        elif name == "network":
            passed = result.returncode != 0 and "PermissionError: K4 sandbox: network denied" in result.stderr
        elif name == "environment":
            passed = result.returncode != 0 and "KeyError: 'K4_SANDBOX_SECRET_PROBE'" in result.stderr
        else:
            passed = result.returncode < 0 and result.seconds >= 1
        checks[name] = {"passed": passed, **asdict(result)}
    if mode()[0] == "sandbox-exec":
        with tempfile.TemporaryDirectory(prefix="k4-canary-") as tmp:
            canary = Path(tmp) / "credentials_k4_synthetic_canary.txt"
            canary.write_text("SYNTHETIC K4 control; contains no credential.\n")
            code = ("import os,subprocess\n"
                    f"os.symlink({str(canary)!r}, 'probe_link')\n"
                    f"paths=[{str(canary)!r}, 'probe_link']\n"
                    "for path in paths:\n"
                    " r=subprocess.run(['/bin/cat',path],capture_output=True,text=True)\n"
                    " assert r.returncode != 0 and not r.stdout and 'Operation not permitted' in r.stderr, r\n"
                    "print('NATIVE_CANARY_DENIED')\n")
            result = run(["probe.py"], {"probe.py": code}, timeout=5)
            checks["native_file_and_symlink_canary"] = {"passed": result.returncode == 0, **asdict(result)}
    if not all(x["passed"] for x in checks.values()):
        raise RuntimeError(json.dumps(checks, indent=2))
    return {"mode": mode()[0], "selection_notes": mode()[1], "checks": checks,
            "limits": {"memory": "No RLIMIT_AS memory cap on macOS.",
                       "processes": "RLIMIT_NPROC current-user baseline +64 (clamped to OS hard limit); per-user, not a process namespace. Timeout kills process group.",
                       "cpu": "RLIMIT_CPU per child; wall timeout kills the process group.",
                       "fallback": "Python audit guard also denies sockets; pytest-socket is last resort only."}}


def self_test():
    global _VERIFIED
    with _PREFLIGHT_LOCK:
        _SELF_TESTING.active = True
        try:
            result = _self_test_checks()
        except BaseException:
            _VERIFIED = False
            raise
        finally:
            _SELF_TESTING.active = False
        _VERIFIED = True
        return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2))


if __name__ == "__main__":
    main()
