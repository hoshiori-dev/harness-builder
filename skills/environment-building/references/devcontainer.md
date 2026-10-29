# Dev Container

Read when a dev container configuration exists or the session runs in a
container, and when writing one the user chose as the base.

## Reading an existing one

Settle from the files, never by asking: `.devcontainer/devcontainer.json`
(or `.devcontainer.json`), any `dockerComposeFile` it names, and the
Dockerfile. Reach comes from:

- `mounts`, `workspaceMount`, and `runArgs` (`-v`, `--mount`,
  `--privileged`, `--cap-add`, `--network`);
- `forwardPorts` and compose `ports`, `network_mode`, `volumes`;
- `containerEnv` and `remoteEnv` (token variables, names only);
- features that add Docker access (`docker-outside-of-docker` mounts the
  host socket; `docker-in-docker` runs the container `--privileged`; both
  are host privilege leaks);
- `remoteUser` and whether it has `sudo`.

Inside a running container, `/proc/self/mountinfo` shows what is actually
mounted, which can differ from the file when the container predates an
edit. Report the difference.

An existing container is adopted as is. Changes to it come only from cuts
the user made in the audit or thick-grade enforcement the user confirmed.

## Writing one the user chose

Write the smallest configuration the choice requires: an image or the
project's existing Dockerfile, a non-root `remoteUser`, the tools the
project's recipes need, and no host credential mount. Shape:

```jsonc
{
  "name": "<project>",
  "image": "mcr.microsoft.com/devcontainers/base:<tag>",
  "features": {},
  "remoteUser": "vscode"
}
```

Pin the image tag and feature versions. Add thick-grade mounts and the
firewall only as the confirmed control-plane proposal states. Anything
beyond that (language toolchains, editor extensions, services) is
contributor setup, not this layer: list it as a suggestion and leave it.
