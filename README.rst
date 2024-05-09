FlowPilot ~ PFC ~ Proxy Flow Control
========================================================

ProxyFlow Control
------------------------------

A net flow pilot in order to handle some proxy configuration automatically.

Usage ::

    ██████╗ ███████╗██╗      ██████╗ ██╗    ██╗ ██████╗
    ██╔══██╗██╔════╝██║     ██╔═══██╗██║    ██║██╔════╝
    ██████╔╝█████╗  ██║     ██║   ██║██║ █╗ ██║██║
    ██╔═══╝ ██╔══╝  ██║     ██║   ██║██║███╗██║██║
    ██║     ██║     ███████╗╚██████╔╝╚███╔███╔╝╚██████╗
    ╚═╝     ╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝  ╚═════╝

    Command line interface for Proxy Flow Controller with basic auto configurations.
    Version: 2.0.1                    By: BlackHaoke<Haoke98@outlook.com>
    Usage: pflow-cli [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      off      Set off and clear all proxy config.
      on       Run proxy flow controller.
      server   Server as the Agent service for the local device in same LAN...
      version  Version

* Install:

    Run ``pip install PFlowC -U`` on the shell.

* start a local flow control service:

    Run ``pflow-cli server`` on the shell.


* set on the proxy setting:

    Run ``pflow-cli on`` on the shell.

* set off the proxy setting:

    Run ``pflow-cli off`` on the shell.

* Ask for Help:

    Run ``pflow-cli --help`` on the shell.
