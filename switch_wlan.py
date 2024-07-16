import os
import subprocess
import argparse

def install_packages():
    packages = [
        "hostapd",
        "dnsmasq",
        "iptables",
        "dhcpcd"
    ]
    subprocess.run(["sudo", "apt-get", "update"])
    subprocess.run(["sudo", "apt-get", "install", "-y"] + packages)

def configure_hostapd():
    hostapd_conf = """
interface=wlan0
driver=nl80211
ssid=MyRPiNetwork
hw_mode=g
channel=6
ieee80211n=1
wmm_enabled=1
ht_capab=[HT40][SHORT-GI-20][DSSS_CCK-40]
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=MySecurePass
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
    """
    with open("/etc/hostapd/hostapd.conf", "w") as f:
        f.write(hostapd_conf)

    with open("/etc/default/hostapd", "r") as f:
        default_hostapd = f.read()

    default_hostapd = default_hostapd.replace("#DAEMON_CONF=\"\"", "DAEMON_CONF=\"/etc/hostapd/hostapd.conf\"")

    with open("/etc/default/hostapd", "w") as f:
        f.write(default_hostapd)

def configure_dnsmasq():
    dnsmasq_conf = """
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
    """
    with open("/etc/dnsmasq.conf", "w") as f:
        f.write(dnsmasq_conf)

def configure_network_ap():
    dhcpcd_conf = """
interface wlan0
static ip_address=192.168.4.1/24
    """
    with open("/etc/dhcpcd.conf", "a") as f:
        f.write(dhcpcd_conf)

    subprocess.run(["sudo", "systemctl", "restart", "dhcpcd"])

def configure_network_client():
    dhcpcd_conf = """
# Normal client mode configuration
    """
    with open("/etc/dhcpcd.conf", "w") as f:
        f.write(dhcpcd_conf)

    subprocess.run(["sudo", "systemctl", "restart", "dhcpcd"])

def enable_ip_forwarding():
    with open("/etc/sysctl.conf", "r") as f:
        sysctl_conf = f.read()

    sysctl_conf = sysctl_conf.replace("#net.ipv4.ip_forward=1", "net.ipv4.ip_forward=1")

    with open("/etc/sysctl.conf", "w") as f:
        f.write(sysctl_conf)

    subprocess.run(["sudo", "sh", "-c", "echo 1 > /proc/sys/net/ipv4/ip_forward"])

def configure_nat():
    subprocess.run(["sudo", "iptables", "-t", "nat", "-A", "POSTROUTING", "-o", "eth0", "-j", "MASQUERADE"])
    subprocess.run(["sudo", "sh", "-c", "iptables-save > /etc/iptables.ipv4.nat"])

    with open("/etc/rc.local", "r") as f:
        rc_local = f.read()

    if "iptables-restore < /etc/iptables.ipv4.nat" not in rc_local:
        rc_local = rc_local.replace("exit 0", "iptables-restore < /etc/iptables.ipv4.nat\nexit 0")

    with open("/etc/rc.local", "w") as f:
        f.write(rc_local)

def start_services():
    subprocess.run(["sudo", "systemctl", "unmask", "hostapd"])
    subprocess.run(["sudo", "systemctl", "enable", "hostapd"])
    subprocess.run(["sudo", "systemctl", "start", "hostapd"])
    subprocess.run(["sudo", "systemctl", "start", "dnsmasq"])

def stop_services():
    subprocess.run(["sudo", "systemctl", "stop", "hostapd"])
    subprocess.run(["sudo", "systemctl", "stop", "dnsmasq"])

def switch_to_ap_mode():
    configure_hostapd()
    configure_dnsmasq()
    configure_network_ap()
    enable_ip_forwarding()
    configure_nat()
    start_services()

def switch_to_client_mode():
    stop_services()
    configure_network_client()

def main():
    parser = argparse.ArgumentParser(description='Switch between AP mode and client mode on Raspberry Pi.')
    parser.add_argument('mode', choices=['ap', 'client'], help='Mode to switch to: "ap" for Access Point mode, "client" for normal WiFi client mode.')

    args = parser.parse_args()

    install_packages()

    if args.mode == 'ap':
        switch_to_ap_mode()
        print("Switched to Access Point mode.")
    elif args.mode == 'client':
        switch_to_client_mode()
        print("Switched to client mode.")

if __name__ == "__main__":
    main()
