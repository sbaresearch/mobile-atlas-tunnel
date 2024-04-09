> [!CAUTION]
> **DEPRECATED**
> The tunnel server version in this repository is **out of date and deprecated**,
> and the implementation was merged into the [main repository](https://github.com/sbaresearch/mobile-atlas).

---

# MobileAtlas SIM Tunnel Server

The MobileAtlas SIM Tunnel Server relays the communication between a measurement probe's modem and a
SIM card hosted on a SIM provider. Additionally, it handles access management, logs relayed
communication, and provides information on managed SIM cards.

This repository contains:

* A Flask server for hosting the REST API.
* The tunnel server handling connections between probes and SIM providers.
* Client implementations for the probe- and the SIM provider sides.
