# Changing WiFi networks with the robot: scoping note

Version 1 · 2026-11-06

## Need
The robot is moved between sites and its Raspberry Pi only knows the home WiFi network. The Pi must learn other networks, and the operator must be able to detect when the PC and the robot are not on the same network.

## Options

| Option | Principle | Simplicity | Security | Remark |
|---|---|---|---|---|
| A. PC script (`picrawler-robot/tools/wifi/wifi_check.py`) | Compares the PC WiFi and the Pi WiFi (SSH + `nmcli`) and prints the command to add a network | Very simple | Good: read-only, no stored password | Works only if the Pi is already reachable |
| B. Local web page | Small form on the PC | Medium | Risk of handling passwords in an application | Not needed at this stage |
| C. Fallback access point on the Pi | If no known WiFi is found, the Pi creates its own network | Medium, to be tested | Good, and the only safety net if the network is lost | To be prepared in advance |
| D. Phone hotspot | The phone shares its mobile connection, PC and Pi both join it | Very simple | Good | Most reliable network when travelling, added to the Pi beforehand |

## Recommendation
1. Before leaving, add the phone hotspot (option D) and, if known, the WiFi of the destination to the Pi. Check with the script (option A).
2. Use the script A at the start of each session to detect a network mismatch.
3. Add option C later as a safety net.
4. A window (widget) is built on top of script A with the same logic. It lives in `picrawler-robot`.

## Risks and mitigations
- **Locking oneself out of the robot**: never delete the previous network and never run a command that switches network during the SSH session. `nmcli connection add` stores a network without switching to it. Keep a fallback access (network cable, screen and keyboard, or access point C).
- **WiFi passwords**: never in the repository and never in a chat. Typed live on the Pi (`read -s`) or sent through the standard input of SSH.
- **Captive portal or client isolation** (hotel, school, public WiFi): the Pi cannot validate a portal in a browser, and such networks often prevent the PC and the Pi from reaching each other. Prefer the phone hotspot.
- **IP address**: it changes between networks. Use the name `picrawler.local` or the list of devices connected to the hotspot.
- **Any change on the Pi** is made with an operator present who can take control back if something goes wrong.

## Status (2026-11-06)
- Read access: the window `wifi_widget.py` was tested on the real robot from a Windows PC.
- The phone hotspot profile was added and verified manually with `nmcli`: the Pi obtained an address on it.
- The add button of the window and `picrawler_ssh.py` have not been tested on the real robot yet.
