"""Offline regression tests: no real download, installation, Coop or VM calls."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import types
import unittest
from unittest.mock import patch, Mock

spec = importlib.util.spec_from_file_location("coop_helper", Path(__file__).with_name("coop_helper.py"))
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


def archive_bytes(entries=None):
    entries = entries or [(name, tarfile.REGTYPE) for name in ("coop", "coop-proxy", "LICENSE")]
    output = io.BytesIO()
    prefix = helper.ARCHIVE.removesuffix(".tar.gz") + "/"
    with tarfile.open(fileobj=output, mode="w:gz") as archive:
        for name, kind in entries:
            entry = tarfile.TarInfo(prefix + name)
            entry.type = kind
            entry.linkname = "../../outside"
            content = ("fixture " + name).encode()
            entry.size = len(content) if kind == tarfile.REGTYPE else 0
            archive.addfile(entry, io.BytesIO(content) if entry.size else None)
    return output.getvalue()


class HelperTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "installation"

    def invoke(self, args, runner=None):
        with contextlib.ExitStack() as stack:
            for name in ("require_platform", "require_kvm", "verify_installation", "check_capabilities"):
                stack.enter_context(patch.object(helper, name))
            stack.enter_context(patch.object(helper, "install_root", return_value=self.root))
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
            call = stack.enter_context(patch.object(helper, "run_coop", side_effect=runner or (lambda *a, **k: "")))
            result = helper.main(args)
            return result, call

    def test_confirmation_blocks_mutations_before_platform_network_or_execution(self):
        for args in (["install"], ["setup"], ["up", "--name", "task", "--project", "unused"],
                     ["exec", "--name", "task", "--", "echo"], ["stop", "--name", "task"]):
            with self.subTest(args=args), patch.object(helper, "require_platform") as host, \
                    patch.object(helper, "download_archive") as network, patch.object(helper, "run_coop") as run, \
                    contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(helper.main(args), 1)
                host.assert_not_called()
                network.assert_not_called()
                run.assert_not_called()

    def test_unsupported_native_windows(self):
        with patch.object(helper.platform, "system", return_value="Windows"):
            with self.assertRaises(helper.SetupError):
                helper.require_platform()

    def test_checksum_failure_writes_nothing(self):
        response = Mock()
        response.geturl.return_value = helper.DOWNLOAD_URL
        response.read.return_value = b"not the release"
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        opener = Mock()
        opener.open.return_value = response
        with patch.object(helper.urllib.request, "build_opener", return_value=opener):
            with self.assertRaisesRegex(helper.SetupError, "SHA-256 mismatch"):
                helper.install(self.root)
        self.assertFalse(self.root.exists())

    def test_real_archive_layout_and_license(self):
        files = helper.release_binaries(archive_bytes())
        self.assertEqual(set(files), {"coop", "coop-proxy", "LICENSE"})
        with patch.object(helper, "download_archive", return_value=archive_bytes()):
            helper.install(self.root)
        self.assertEqual((self.root / "LICENSE").read_bytes(), b"fixture LICENSE")
        helper.verify_installation(self.root)

    def test_expected_binary_cannot_be_link_duplicate_or_traversal(self):
        for entries in (
            [("coop", tarfile.SYMTYPE), ("coop-proxy", tarfile.REGTYPE), ("LICENSE", tarfile.REGTYPE)],
            [("coop", tarfile.REGTYPE), ("coop", tarfile.REGTYPE), ("coop-proxy", tarfile.REGTYPE), ("LICENSE", tarfile.REGTYPE)],
            [("../coop", tarfile.REGTYPE), ("coop-proxy", tarfile.REGTYPE), ("LICENSE", tarfile.REGTYPE)],
        ):
            with self.subTest(entries=entries), self.assertRaises(helper.SetupError):
                helper.release_binaries(archive_bytes(entries))

    def test_existing_installation_not_overwritten(self):
        self.root.mkdir()
        sentinel = self.root / "user-file"
        sentinel.write_text("keep")
        with patch.object(helper, "download_archive") as download, self.assertRaises(helper.SetupError):
            helper.install(self.root)
        download.assert_not_called()
        self.assertEqual(sentinel.read_text(), "keep")

    def test_tampered_config_and_binary_refused(self):
        with patch.object(helper, "download_archive", return_value=archive_bytes()):
            helper.install(self.root)
        config = self.root / "config.toml"
        config.write_text(helper.config_text(self.root) + '\n[proxy]\n', encoding="utf-8")
        with self.assertRaises(helper.SetupError):
            helper.verify_installation(self.root)
        config.write_text(helper.config_text(self.root), encoding="utf-8")
        (self.root / "bin/coop").write_bytes(b"changed")
        with self.assertRaises(helper.SetupError):
            helper.verify_installation(self.root)

    def test_config_paths_and_disabled_forwarding(self):
        import tomllib
        config = tomllib.loads(helper.config_text(self.root))
        self.assertEqual(config["data_dir"], str(self.root / "data"))
        self.assertEqual(config["firecracker_bin"], str(self.root / "data/firecracker"))
        self.assertEqual(config["vm"]["kernel_path"], str(self.root / "data/vmlinux"))
        self.assertEqual(config["github"], "off")
        self.assertFalse(config["setup"]["prompt_for_pat"])
        for name in ("claude", "codex"):
            self.assertFalse(config[name]["config_dir"])
            self.assertEqual(config[name]["env_forward"], [])
        self.assertEqual(config["updates"]["mode"], "off")

    def test_environment_drops_secrets_and_search_path_overrides(self):
        account = types.SimpleNamespace(pw_dir="/home/example", pw_name="example")
        pwd = types.SimpleNamespace(getpwuid=lambda uid: account)
        with patch.dict(sys.modules, {"pwd": pwd}), patch.object(os, "getuid", return_value=1000, create=True), \
                patch.dict(os.environ, {"OPENAI_API_KEY": "secret", "GITHUB_TOKEN": "secret", "SSH_AUTH_SOCK": "secret", "PYTHONPATH": "secret"}):
            environment = helper.clean_environment(self.root)
        self.assertEqual(set(environment), {"HOME", "USER", "LOGNAME", "PATH", "LANG"})
        self.assertEqual(environment["HOME"], "/home/example")
        self.assertNotIn("secret", environment.values())

    def test_subprocess_uses_clean_env_no_shell_and_private_cwd(self):
        environment = {"PATH": "safe"}
        with patch.object(helper, "clean_environment", return_value=environment), patch.object(helper.subprocess, "run") as run:
            run.return_value.stdout = "ok"
            self.assertEqual(helper.run_coop(self.root, ["list", "--json"], capture=True), "ok")
        kwargs = run.call_args.kwargs
        self.assertIs(kwargs["env"], environment)
        self.assertEqual(kwargs["cwd"], str(self.root))
        self.assertNotIn("shell", kwargs)
        self.assertTrue(kwargs["check"])

    def test_project_secret_and_home_refused(self):
        project = self.base / "project"
        project.mkdir()
        with patch.object(helper, "host_home", return_value=project), self.assertRaises(helper.SetupError):
            helper.project_path(str(project), self.root)
        (project / ".env").write_text("SECRET=value")
        with patch.object(helper, "host_home", return_value=self.base / "home"), self.assertRaises(helper.SetupError):
            helper.project_path(str(project), self.root)

    def test_top_level_symlink_refused(self):
        with patch.object(Path, "is_symlink", return_value=True), self.assertRaises(helper.SetupError):
            helper.project_path("unused", self.root)

    def test_up_uses_restricted_flags_and_probes_guest(self):
        with patch.object(helper, "project_path", return_value=self.base / "project"):
            code, run = self.invoke(["up", "--confirm", "--name", "task", "--project", "chosen"],
                                    lambda root, args, **kwargs: "[]" if args[0] == "list" else "")
        self.assertEqual(code, 0)
        up = run.call_args_list[1].args[1]
        for flag in ("--new-instance", "--copy", "--no-agents", "--no-prompt", "--no-devcontainer", "--exclude-git"):
            self.assertIn(flag, up)
        self.assertEqual(run.call_args_list[2].args[1], ["exec", "task", "--", "/usr/bin/true"])

    def test_up_refuses_existing_name(self):
        with patch.object(helper, "project_path", return_value=self.base / "project"):
            code, run = self.invoke(["up", "--confirm", "--name", "task", "--project", "chosen"],
                                    lambda *a, **k: '[{"name":"task"}]')
        self.assertEqual(code, 1)
        self.assertEqual(run.call_count, 1)

    def test_exec_failed_readiness_never_runs_requested_command(self):
        def fail(*args, **kwargs):
            raise subprocess.CalledProcessError(9, "fixture")
        code, run = self.invoke(["exec", "--confirm", "--name", "task", "--", "make", "test"], fail)
        self.assertEqual(code, 9)
        self.assertEqual(run.call_count, 1)
        self.assertEqual(run.call_args.args[1], ["exec", "task", "--", "/usr/bin/true"])

    def test_missing_safety_flag_fails_closed(self):
        with patch.object(helper, "run_coop", return_value="--copy"), self.assertRaises(helper.SetupError):
            helper.check_capabilities(self.root)


if __name__ == "__main__":
    unittest.main()
