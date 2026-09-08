---
name: Bug report
about: Something in the Violet Pool Controller integration does not work
title: ''
labels: bug
assignees: ''

---

## What happens

<!-- What went wrong? One or two sentences. -->

## What you expected instead

<!-- What should have happened? -->

## Steps to reproduce

1.
2.
3.

## Versions

| | |
|---|---|
| Home Assistant version | <!-- Settings → About, e.g. 2026.9.1 --> |
| Integration version | <!-- Settings → Devices & Services → Violet Pool Controller, or manifest.json --> |
| Controller firmware | <!-- The controller's own web UI, or the `firmware` field in the diagnostics download --> |
| Installed via | <!-- HACS / manual copy --> |

## Diagnostics

Please attach the diagnostics download — it is the single most useful thing
you can add, and passwords and usernames are redacted automatically.

**Settings → Devices & Services → Violet Pool Controller → the three-dot menu
on the device → Download diagnostics**, then drag the JSON file into this
issue.

<!-- If you cannot attach it, say so and we will work without it. -->

## Logs

Enable debug logging, reproduce the problem, then paste the relevant lines.

Either use **Settings → Devices & Services → Violet Pool Controller → Enable
debug logging**, or add this to `configuration.yaml` and restart:

```yaml
logger:
  logs:
    custom_components.violet_pool_controller: debug
```

<details>
<summary>Log output</summary>

```text
paste here
```

</details>

## Affected entities or services

<!-- Entity ids (e.g. switch.violet_pool_controller_pump) or service names
     (e.g. violet_pool_controller.control_pump), if the problem is specific
     to one of them. -->

## Anything else

<!-- Screenshots, automation YAML, network setup (SSL on/off?), how many
     controllers you run, anything you already tried. -->
