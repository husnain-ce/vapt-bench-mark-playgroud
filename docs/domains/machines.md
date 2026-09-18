# Machine targets (VulnHub VMs)

**6 boot2root VMs**: Chronos, DoubleTrouble, EvilBox, Hacksudo,
Metasploitable 2, Momentum.

These are full **VulnHub virtual machines**, distributed as OVA/zip images and
run in **VirtualBox** — not containers. `bench` lists them
(`./bench list --all`) but does not host them.

## Setup (per VM)

Each `Machines/<name>/` directory has a README with the exact download URL,
file size, and md5/sha1 checksums. General flow:

1. Install [VirtualBox](https://www.virtualbox.org/).
2. Download the OVA (or zip) from the URL in that VM's README, and **verify the
   checksum** before importing.
3. **File → Import Appliance**, select the `.ova`.
4. **Networking: Host-Only or NAT, never Bridged.** These VMs are deliberately
   vulnerable; keep them off any real network.
5. Boot, then find the VM's DHCP-assigned IP with `arp-scan` / `netdiscover`
   on the virtual network, or from VirtualBox's DHCP lease list.

## ⚠️ Metasploitable 2

Metasploitable 2 is widely known to be dangerous if exposed — real instances
have been compromised in the wild within minutes. Only ever run it Host-Only or
NAT, never on infrastructure reachable from the internet. See
[`docs/SECURITY.md`](../SECURITY.md).
