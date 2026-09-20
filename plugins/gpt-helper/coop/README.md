# Optional Coop setup for GPT Helper

[Русский](README.ru.md)

This optional helper downloads and configures upstream **Coop v0.6.0**. Installing the GPT Helper
plugin does **not** install Coop or create a VM. This is not a VM image, a copy of your existing
environment, a mobile runtime, or an automatic permission grant.

## Requirements and scope

- Linux **x86_64**, Python **3.10+**, working accessible `/dev/kvm`, and sudo access for Coop setup.
- Windows: **PowerShell 7**, an existing WSL **2** Linux x86_64 distribution, Python 3.10+ inside it,
  and working nested KVM. The wrapper defaults to `Ubuntu-24.04` and its default Linux user;
  it does not force root. WSL compatibility depends on your host and kernel, not merely WSL being installed.
- No native Windows, macOS, ARM, or phone support in this helper. It does not install WSL, enable
  virtualization, edit Windows execution policy, or fix KVM permissions automatically.
- Commands that change state require `--confirm`. For an agent, this flag **does not replace explicit
  task-scoped user permission** for installation, VM operations, file transfer, or guest execution.

## Get the files

Download the entire [GPT Helper ZIP](https://github.com/FFriends/GPT-Helper/archive/refs/heads/main.zip)
and extract it, or clone the repository. Keep this folder's files together, then enter
`plugins/gpt-helper/coop` inside the extracted/cloned repository. Optional clone command:

```sh
git clone https://github.com/FFriends/GPT-Helper.git
cd GPT-Helper/plugins/gpt-helper/coop
```

## Linux / inside WSL

Run as the intended Linux user. Review each operation before confirming it:

```sh
python3 -I coop_helper.py install --confirm
python3 -I coop_helper.py check
python3 -I coop_helper.py setup --confirm
```

`install` fetches the official pinned archive, verifies its SHA-256, and installs `coop`, `coop-proxy`,
the upstream license, and a restricted configuration. It does not create or start a VM.
`check` checks local files, CLI flags, selected prerequisites, and the KVM API; it does not test VM boot
or networking. Stop on a failure; do not run the project on the host instead.

**`setup` makes host changes:** Coop may request sudo, install missing host packages, download
Firecracker and a kernel, mount filesystems, and build a rootfs using chroot. Its guest image includes
Docker, GitHub CLI, Claude Code, and Codex. No agent session is launched by this helper; the image is
not “agent-free.” Downloads use the network. Review upstream prompts; required setup work is not
covered merely by permission to install the GPT Helper plugin.

Prepare a **separate, reviewed project copy** with only approved files. Replace the path below with
its absolute Linux path (on WSL, a specific `/mnt/c/...` project directory is also possible):

```sh
python3 -I coop_helper.py up --name sample-task --project /absolute/path/to/reviewed-project --confirm
python3 -I coop_helper.py exec --confirm --name sample-task -- uname -a
python3 -I coop_helper.py status
python3 -I coop_helper.py stop --name sample-task --confirm
```

`up` requires a **fresh name**, creates a copy-based VM, excludes `.git`, skips agent credential/config
injection and devcontainer processing, then checks guest reachability. It refuses existing names;
there is no restart command. `exec` runs only the supplied command inside the VM. `status` lists local
instance metadata, **not live health**. `stop` preserves the VM disk.

## Windows / PowerShell 7

From this same folder, use the wrapper instead of `python3 -I coop_helper.py`:

```powershell
.\Coop.ps1 -CoopArguments @('install', '--confirm')
.\Coop.ps1 -CoopArguments @('check')
.\Coop.ps1 -CoopArguments @('setup', '--confirm')
.\Coop.ps1 -CoopArguments @('up', '--name', 'sample-task', '--project', '/absolute/path/to/reviewed-project', '--confirm')
.\Coop.ps1 -CoopArguments @('exec', '--confirm', '--name', 'sample-task', '--', 'uname', '-a')
.\Coop.ps1 -CoopArguments @('status')
.\Coop.ps1 -CoopArguments @('stop', '--name', 'sample-task', '--confirm')
```

Optionally add `-Distribution 'YourDistro'` and `-LinuxUser 'youruser'` consistently to every call.
The wrapper can start the selected WSL distribution; that distribution hosts Coop and is **not** the
Coop guest VM. If PowerShell blocks the script, inspect your policy; this helper does not bypass it.

## Safety, storage, and limits

- State lives under the selected Linux user's `~/.local/share/gpt-helper-coop/v0.6.0/`, with separate
  config, binaries, data, Firecracker, and kernel paths. Existing `~/.coop` is not reused.
- Existing installation roots are refused, not overwritten. A partial install or failed VM operation
  may leave files/resources for inspection; failures do not trigger deletion or host fallback.
- Each Coop invocation receives a restricted environment; GitHub forwarding, agent config copying,
  extra forwarded variables, and background update checks are disabled. Altered config is refused.
- Project checks reject several obvious secret paths and symlinks, but are **not an exhaustive secret
  scanner**. Review every copied file yourself. A VM is not a guarantee of zero risk or blocked network access.
- No automatic pull, update, restart, or uninstall. Review guest changes before manually returning
  only relevant files; preserve unrelated host edits. Do not publish VM disks, keys, or local state.
- Validation during development covered offline checks only; **live installation and VM execution
  were not tested for this package**. The pinned CLI does not pin all later upstream setup downloads.

To rerun offline tests with Python 3.11+ from this folder: `python3 -m unittest -v test_coop_helper`.
The tests replace network, subprocess and KVM operations with fixtures; they do not install Coop.
GPT Helper's helper code is MIT-licensed; downloaded Coop remains under its upstream Apache-2.0 license.

Archive: `coop-v0.6.0-x86_64-unknown-linux-musl.tar.gz`; SHA-256:
`fced8803bfe655a9614cae3338b03cbfaf46eff959c31d15a34f0ad87ca67700`.
Sources: [release](https://github.com/trailofbits/coop/releases/tag/v0.6.0),
[checksums](https://github.com/trailofbits/coop/releases/download/v0.6.0/SHA256SUMS),
[commands](https://github.com/trailofbits/coop/blob/v0.6.0/docs/commands.md),
[configuration](https://github.com/trailofbits/coop/blob/v0.6.0/docs/configuration.md),
[Linux prerequisites](https://github.com/trailofbits/coop/blob/v0.6.0/docs/backends.md),
[WSL settings](https://learn.microsoft.com/en-us/windows/wsl/wsl-config#main-wsl-settings).
