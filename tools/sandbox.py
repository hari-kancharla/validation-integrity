"""Scratch execution for case and test code: scrubbed environment, denied network,
bounded process group, scratch-only filesystem.

All case and test execution goes through this module. It never resolves credentials.
Python and packages are read from .venv when present, else the running interpreter;
code and a writable HOME live in a temporary directory.

What this is, and is not. It exists so that running the study's own twins leaves no
trace outside a scratch directory, reaches no network, and reads no credential -- so
that an execution receipt means something. It is not a boundary against hostile code.
The Python audit guard covers `open` and a list of filesystem calls, which is defence
in depth and nothing more: it cannot see a ctypes call into libc, a child process that
does not carry the hook, or a race between its own path resolution and the kernel's.

What stops those is the operating system, and only on macOS. The sandbox-exec profile
denies the network, named credential paths, and writes to the source tree. On Linux the
backend is `unshare -rn`, which creates a network namespace and nothing else: there is
no mount namespace, so a child sees the whole host filesystem, and `-r` maps the
invoking user to root inside the namespace, which grants capabilities over that user's
own files. The Python guard is therefore the only filesystem barrier on Linux, and it
is not one. Treat the Linux backend as network isolation plus hygiene. Real filesystem
confinement there needs `unshare -m` with bind mounts, or bubblewrap, and is not
implemented.
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
# Kept in step with the bootstrap guard's own set, so a case that the guard would
# refuse at open time is refused at submission instead, identically on every backend.
_CREDENTIAL_INPUT_NAMES = {".netrc", "credentials", "id_rsa", "id_ed25519"}

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
    """Select the first usable isolation mechanism, starting nothing."""
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
        if platform.system() == "Linux":
            notes.append("Linux unshare unavailable or unusable.")
        seatbelt = shutil.which("sandbox-exec")
        if platform.system() == "Darwin" and seatbelt:
            probe = _quick([seatbelt, "-p", "(version 1)(allow default)(deny network*)", "/usr/bin/true"], home)
            if probe and probe.returncode == 0:
                _MODE = ("sandbox-exec", notes)
                return _MODE
        notes.append("macOS sandbox-exec unavailable or unusable.")
        # There is no safe fallback. A Python audit hook is installed per interpreter
        # and is not inherited, so it cannot confine a child process, and the child
        # preflight could never pass on such a mode. Fail closed instead of selecting
        # a backend that only looks like isolation.
        raise RuntimeError(
            "No OS-level isolation available: this needs Linux with unshare, or macOS "
            "with sandbox-exec. A Python-level guard does not confine child processes, "
            "so there is no fallback. " + " ".join(notes))


BOOTSTRAP = r'''
import importlib.metadata, json, os, platform, runpy, sys, tempfile
from pathlib import Path
# No inherited variables, and no bytecode/cache files in the source tree.
os.environ.clear()
os.environ.update({"PATH": sys.argv[1], "HOME": sys.argv[2], "LANG": "C"})
sys.dont_write_bytecode = True
root = Path.cwd().resolve()
scratch = root / 'tmp'
scratch.mkdir()
tempfile.tempdir = str(scratch)
sys._k4_sandbox_mode = sys.argv[3]
# Written outside the workspace, before the guard is installed. Inside it, the case
# could rewrite its own provenance and run() would read the forgery back.
Path(sys.argv[4]).write_text(json.dumps({'python': platform.python_version(),
    'packages': {d.metadata['Name']: d.version for d in importlib.metadata.distributions()}}))
sys.path.insert(0, str(root))
_ALLOWED = None
_CREDENTIAL_NAMES = {".netrc", "credentials", "id_rsa", "id_ed25519"}
_WRITE_DEVICES = {"/dev/null", "/dev/zero", "/dev/stdout", "/dev/stderr", "/dev/tty"}


def allowed_roots():
    """Readable roots, computed once. Each root's resolved form is admitted too.

    sys.prefix and sys.base_prefix can be reported through a symlink: a Homebrew
    interpreter reports /opt/homebrew/opt/python@X while loading its stdlib from the
    Cellar path that points at, and without the resolved form it cannot read its own
    files. Those are the same directories, so nothing new is admitted. /System/Library
    rather than /System, because /System/Volumes/Data is a firmlink alias for the whole
    data volume that realpath does not collapse.
    """
    global _ALLOWED
    if _ALLOWED is None:
        out = []
        for candidate in [root, Path(sys.prefix), Path(sys.base_prefix),
                          Path('/System/Library'), Path('/usr'), Path('/Library'),
                          Path('/dev'), Path('/private/var/db')]:
            out.append(candidate)
            try:
                out.append(candidate.resolve())
            except (OSError, ValueError):
                pass
        _ALLOWED = tuple(out)
    return _ALLOWED


def _real(value):
    """Absolute and symlink-resolved, failing closed rather than falling back."""
    try:
        return Path(os.path.realpath(Path(os.path.abspath(os.fsdecode(value)))))
    except (OSError, ValueError):
        raise PermissionError("K4 sandbox: unresolvable path denied")


def _reject_credentials(*names):
    for name in names:
        if name.startswith(".env") or name in _CREDENTIAL_NAMES:
            raise PermissionError("K4 sandbox: credential access denied")


def guard(event, args):
    if event in {"socket.connect", "socket.bind", "socket.getaddrinfo", "socket.sendto"}:
        raise PermissionError("K4 sandbox: network denied")
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        # Enforce on the real target, not the name in the call: a symlink made inside
        # scratch otherwise defeats both checks, since its own name hides the target's
        # and its own path is lexically inside the allowed root.
        lexical = Path(os.path.abspath(os.fsdecode(args[0])))
        path = _real(args[0])
        _reject_credentials(lexical.name, path.name)
        if not any(path == p or p in path.parents for p in allowed_roots()):
            raise PermissionError("K4 sandbox: file outside scratch/runtime denied")
        writing = (args[1] and any(c in args[1] for c in 'wax+')) or (
            isinstance(args[2], int) and args[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
        # Compared on the lexical name: /dev/stdout resolves to a tty or /dev/fd/N,
        # so the resolved form never matches the device list.
        if (writing and root != path and root not in path.parents
                and str(lexical) not in _WRITE_DEVICES
                and str(path) not in _WRITE_DEVICES):
            raise PermissionError("K4 sandbox: write outside scratch denied")


# Guarding `open` alone leaves the rest of the filesystem API unchecked, and two of
# those calls defeat the open guard outright. os.link brings an outside file into
# scratch as a hard link, which has no target for realpath to follow -- it is the same
# inode under a second name -- and os.rename, os.truncate and os.remove write to and
# destroy paths outside scratch without ever opening them.
_WRITE_EVENTS = {"os.link": (0, 1), "os.rename": (0, 1), "os.replace": (0, 1),
                 "os.symlink": (1,), "os.remove": (0,), "os.unlink": (0,),
                 "os.rmdir": (0,), "os.mkdir": (0,), "os.truncate": (0,),
                 "os.chmod": (0,), "os.chown": (0,), "os.utime": (0,)}
# Reads are held to the readable roots rather than to scratch: package imports scan
# sys.path, so restricting enumeration to scratch breaks importing anything at all.
_READ_EVENTS = {"os.listdir": (0,), "os.scandir": (0,), "os.chdir": (0,)}


def guard_fs(event, args):
    write = _WRITE_EVENTS.get(event)
    indexes = write if write is not None else _READ_EVENTS.get(event)
    if indexes is None:
        return
    for index in indexes:
        if index >= len(args) or not isinstance(args[index], (str, bytes, os.PathLike)):
            continue
        target = _real(args[index])
        if write is not None:
            _reject_credentials(Path(os.path.abspath(os.fsdecode(args[index]))).name,
                                target.name)
            if root != target and root not in target.parents:
                raise PermissionError("K4 sandbox: " + event + " outside scratch denied")
        elif not any(target == p or p in target.parents for p in allowed_roots()):
            raise PermissionError("K4 sandbox: " + event + " outside scratch/runtime denied")


sys.addaudithook(guard)
sys.addaudithook(guard_fs)
args = sys.argv[5:]
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
    # The OS denies the network, known credential paths and names, and writes to the
    # source tree. The Python guard is defence in depth over a handful of audit events,
    # not a boundary: it cannot see a ctypes call, a child process without the hook, or
    # a path/fd race, so anything this profile does not name is reachable. Full native
    # filesystem or process-namespace isolation is not claimed.
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
            if (relative.is_absolute() or ".." in relative.parts
                    or any(part.startswith(".env") or part in _CREDENTIAL_INPUT_NAMES
                           for part in relative.parts)
                    or relative.name in {"_k4_bootstrap.py", "_k4_runtime.json",
                                         "_sandbox.sb"}):
                raise ValueError("Unsafe sandbox input path")
            target = workspace / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body if isinstance(body, bytes) else body.encode())
        bootstrap = workspace / "_k4_bootstrap.py"
        bootstrap.write_text(BOOTSTRAP)
        environment = _environment(home)
        receipt = container / "_k4_runtime.json"
        command = [str(PYTHON), "-B", str(bootstrap), environment["PATH"],
                   str(home), chosen, str(receipt), *map(str, arguments)]
        inherited = hasattr(sys, "_k4_sandbox_mode")
        if chosen == "sandbox-exec" and not inherited:
            profile = workspace / "_sandbox.sb"
            profile.write_text(_profile(workspace))
            command = ["/usr/bin/sandbox-exec", "-f", str(profile), *command]
        elif chosen == "unshare" and not inherited:
            command = [shutil.which("unshare"), "-rn", *command]

        def limits():
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 1))
            hard = resource.getrlimit(resource.RLIMIT_NPROC)[1]
            cap = process_limit if hard == resource.RLIM_INFINITY else min(process_limit, hard)
            resource.setrlimit(resource.RLIMIT_NPROC, (cap, cap))
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
            resource.setrlimit(resource.RLIMIT_FSIZE, (1 << 30, 1 << 30))

        started = time.monotonic()
        process = subprocess.Popen(_env_command(environment, command), cwd=workspace,
            env={}, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            start_new_session=True, preexec_fn=limits)
        timed_out = False
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            try:
                # killpg reaches the process group only. A child that called setsid()
                # has left it and still holds the inherited pipes, so an unbounded
                # second communicate() waits for a process the timeout did not kill.
                stdout, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                for stream in (process.stdout, process.stderr):
                    if stream is not None:
                        stream.close()
                process.wait()
                stdout, stderr = "", "K4 sandbox: a detached child held the output pipes open"
        runtime = json.loads(receipt.read_text()) if receipt.exists() else {}
        recorded_python = runtime.get("python", "UNRECORDED")
        return Result(process.returncode, stdout, stderr, timed_out,
                      time.monotonic() - started, chosen, recorded_python,
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

# A sandbox-exec denial surfaces as EPERM or EACCES. A fresh network namespace
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
    # The filesystem checks need a target the case did not create, so the parent makes
    # one outside scratch and each probe is handed its real path.
    with tempfile.TemporaryDirectory(prefix="k4-outside-") as outside:
        host = Path(outside) / "host_canary.txt"
        host.write_text("K4 SYNTHETIC control; contains no credential.\n")
        secret = Path(outside) / ".env-canary"
        secret.write_text("K4 SYNTHETIC control; contains no credential.\n")
        victim = Path(outside) / "write_target.txt"
        victim.write_text("untouched\n")

        # Proving the scrub needs the variable to actually exist in the parent first;
        # asserting a KeyError for a name nothing ever sets passes on any build.
        os.environ["K4_SANDBOX_SECRET_PROBE"] = "present-in-parent"
        try:
            for name, code, timeout, extra in [
                ("network", "import socket; socket.create_connection(('192.0.2.1',443),timeout=.1)", 5, {}),
                ("environment", "import os; print(os.environ['K4_SANDBOX_SECRET_PROBE'])", 5, {}),
                ("infinite_loop", "while True: pass", 2, {}),
                ("normal", "import os; assert set(os.environ)=={'PATH','HOME','LANG'}; print('OK')", 5, {}),
                ("child_network", _CHILD_NETWORK_PROBE, 5,
                 {"child_probe.py": _CHILD_NETWORK_CHILD}),
                ("read_outside_scratch", f"open({str(host)!r}).read()", 5, {}),
                ("write_outside_scratch",
                 "import os, sys\n"
                 "open(os.path.join(sys.prefix, 'k4_write_probe.tmp'), 'w').write('PWNED')",
                 5, {}),
                ("write_unreadable_path", f"open({str(victim)!r}, 'w').write('PWNED')", 5, {}),
                ("credential_name", f"open({str(secret)!r}).read()", 5, {}),
                ("symlink_escape",
                 f"import os\nos.symlink({str(host)!r}, 'alias')\nopen('alias').read()", 5, {}),
                ("hardlink_escape",
                 f"import os\nos.link({str(host)!r}, 'alias')\nopen('alias').read()", 5, {}),
                ("rename_outside_scratch",
                 f"import os\nopen('p','w').write('PWNED')\nos.rename('p', {str(victim)!r})", 5, {}),
            ]:
                result = run(["probe.py"], {"probe.py": code + "\n", **extra},
                             timeout=timeout, cpu_seconds=2)
                if name in {"normal", "child_network"}:
                    passed = result.returncode == 0
                elif name == "network":
                    passed = result.returncode != 0 and "K4 sandbox: network denied" in result.stderr
                elif name == "environment":
                    passed = (result.returncode != 0
                              and "KeyError: 'K4_SANDBOX_SECRET_PROBE'" in result.stderr)
                elif name == "write_unreadable_path":
                    passed = (result.returncode != 0
                              and "K4 sandbox: file outside scratch/runtime denied" in result.stderr
                              and victim.read_text() == "untouched\n")
                elif name in {"read_outside_scratch", "symlink_escape"}:
                    passed = (result.returncode != 0
                              and "K4 sandbox: file outside scratch/runtime denied" in result.stderr)
                elif name == "write_outside_scratch":
                    # A readable root that is not scratch: the interpreter's own tree.
                    # Denial is the assertion -- a permitted write would exit 0.
                    passed = (result.returncode != 0
                              and "K4 sandbox: write outside scratch denied" in result.stderr)
                elif name == "credential_name":
                    passed = (result.returncode != 0
                              and "K4 sandbox: credential access denied" in result.stderr)
                elif name == "hardlink_escape":
                    passed = (result.returncode != 0
                              and "K4 sandbox: os.link outside scratch denied" in result.stderr)
                elif name == "rename_outside_scratch":
                    passed = (result.returncode != 0
                              and "K4 sandbox: os.rename outside scratch denied" in result.stderr
                              and victim.read_text() == "untouched\n")
                else:
                    passed = result.returncode < 0 and result.seconds >= 1
                checks[name] = {"passed": passed, **asdict(result)}
        finally:
            os.environ.pop("K4_SANDBOX_SECRET_PROBE", None)
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
            "limits": {"memory": "No RLIMIT_AS address-space cap on either backend; RLIMIT_FSIZE is 1 GiB.",
                       "processes": "RLIMIT_NPROC current-user baseline +64 (clamped to OS hard limit); per-user, not a process namespace. Timeout kills process group.",
                       "cpu": "RLIMIT_CPU per child; wall timeout kills the process group.",
                       "fallback": "The Python audit guard denies sockets in-process as well; there is no\n"
                                   "non-OS fallback, since a hook does not reach child processes."}}


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
