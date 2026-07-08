FlowPilot ~ PFC ~ Proxy Flow Control
========================================================

A smart proxy router that automatically routes domestic traffic directly
and foreign traffic through an upstream proxy — all decided by GeoIP at
the TCP CONNECT level. Pure Python asyncio, no mitmproxy dependency.

Usage
-----

::

    ██████╗ ███████╗██╗      ██████╗ ██╗    ██╗ ██████╗
    ██╔══██╗██╔════╝██║     ██╔═══██╗██║    ██║██╔════╝
    ██████╔╝█████╗  ██║     ██║   ██║██║ █╗ ██║██║
    ██╔═══╝ ██╔══╝  ██║     ██║   ██║██║███╗██║██║
    ██║     ██║     ███████╗╚██████╔╝╚███╔███╔╝╚██████╗
    ╚═╝     ╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝  ╚═════╝

    Usage: pflow-cli [OPTIONS] COMMAND [ARGS]...

    Commands:
      server    Start the smart proxy router (GeoIP-based)
      on        Set macOS system proxy + shell env + git proxy
      off       Clear all proxy settings
      version   Show version

Install
-------

``pip install PFlowC -U``

Configure
---------

Create ``~/.PFlowC/config.json``::

    {
      "port": 7891,
      "upstream": {"host": "192.168.76.145", "port": "7890"},
      "bypass_domains": ["127.0.0.1", "192.168.0.0/16", "172.16.0.0/16", "10.0.0.0/8"]
    }

Run
---

Start the router::

    pflow-cli server

Set system proxy::

    pflow-cli on

Clear all proxy settings::

    pflow-cli off

How It Works
------------

A lightweight async CONNECT proxy listens on the configured port. For
each connection:

- GeoIP lookup determines if the target is domestic (China) or foreign.
- **Domestic**: TCP connects directly with zero latency overhead.
- **Foreign**: TCP connects to the upstream proxy, sends CONNECT, relays.
- Results are cached in memory for instant repeat lookups.

Release
-------

Push a ``v*`` tag to trigger GitHub Actions → PyPI + GitHub Release::

    git tag v3.0.0 && git push origin v3.0.0

License
-------

MIT · Copyright Sadam·Sadik
