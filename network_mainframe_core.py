import asyncio
import json
import numpy as np

# Global Mainframe Registry tracking hardware anomaly counters
MALFUNCTIONING_NODE_REGISTRY = {}
CRITICAL_MALFUNCTION_CEILING = 3 # Blacklist node after 3 active breaches

class MainframeNetworkProtocol(asyncio.DatagramProtocol):
    def __init__(self, safety_guard_instance):
        super().__init__()
        self.safety_guard = safety_guard_instance
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        print("Sovereign Mainframe Network Layer: Asynchronous socket port opened successfully.")

    def datagram_received(self, data, addr):
        """Asynchronously intercepts raw sensor packets directly off the network buffer."""
        try:
            # Decode the incoming UDP network string byte array
            payload_str = data.decode('utf-8')
            packet = json.loads(payload_str)
            
            # Instantly forward packet to the integrated safety and diagnostic engine
            asyncio.create_task(self.safety_guard.audit_incoming_packet(packet, addr))
            
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(f"⚠️  Network Intercept Warning: Dropping malformed packet string from {addr}")


class MainframeSafetyDiagnosticGuard:
    def __init__(self):
        # Maximum hard limit for frequency (300 GHz cutoff to avoid ionizing spectrums)
        self.HARD_FREQ_CUTOFF_HZ = 300e9
        # Maximum allowed physical power density (FCC ceiling for public safety)
        self.MAX_SAFE_POWER_DENSITY = 10.0 

    async def audit_incoming_packet(self, packet, addr):
        """
        Processes node metrics, verifies environmental compliance, 
        and flags corrupted or un-throttled edge node hardware.
        """
        node_id = packet.get("node_id", f"UNKNOWN_NODE_{addr[0]}")
        
        # Check if the node is already fully blacklisted
        if MALFUNCTIONING_NODE_REGISTRY.get(node_id, 0) >= CRITICAL_MALFUNCTION_CEILING:
            print(f"⛔ CRITICAL SHIELD DROPPED: Rejecting stream from blacklisted defective node [{node_id}] at {addr}")
            return

        freq = float(packet.get("frequency_hz", 0))
        power = float(packet.get("output_power_watts", 0))
        gain = float(packet.get("antenna_gain", 1))
        contains_biology = bool(packet.get("assert_contains_biology", False))

        # --- DEFECT VERIFICATION RULES ---
        is_defective = False
        fault_reason = ""

        # Rule 1: Structural Frequency Deviation (Hardware trying to sweep into ionizing bands)
        if freq >= self.HARD_FREQ_CUTOFF_HZ:
            is_defective = True
            fault_reason = f"Ionization frequency violation detected: Tracing {freq / 1e9:.2f} GHz spectrum pulse."

        # Rule 2: Active Power Limit Breach near Biological Indicators
        # Assuming proxy 1-meter minimum safety margin test for incoming unshielded signals
        calculated_density = (power * gain) / (4.0 * np.pi * (1.0 ** 2))
        if contains_biology and (calculated_density > self.MAX_SAFE_POWER_DENSITY):
            is_defective = True
            fault_reason = f"Unsafe power density output ({calculated_density:.2f} W/m²) mapped adjacent to biological matrix."

        # --- DEFECT ENFORCEMENT STATE MACHINE ---
        if is_defective:
            # Increment anomaly fault score inside global mainframe memory registers
            MALFUNCTIONING_NODE_REGISTRY[node_id] = MALFUNCTIONING_NODE_REGISTRY.get(node_id, 0) + 1
            fault_count = MALFUNCTIONING_NODE_REGISTRY[node_id]
            
            print(f"🚨 ANOMALY ALERT: Node [{node_id}] flagged as defective. Reason: {fault_reason}")
            print(f"-> Node Anomaly Score: {fault_count}/{CRITICAL_MALFUNCTION_CEILING}")
            
            if fault_count >= CRITICAL_MALFUNCTION_CEILING:
                print(f"❌ BROADCAST OVERRIDE IMMINENT: Node [{node_id}] blacklisted. Isolation command issued to grid network.")
            return

        # --- VALIDATED SAFE PATHWAY ---
        # If passed, decrement anomaly score slightly to reward sustained hardware calibration stability
        if node_id in MALFUNCTIONING_NODE_REGISTRY and MALFUNCTIONING_NODE_REGISTRY[node_id] > 0:
            MALFUNCTIONING_NODE_REGISTRY[node_id] -= 1
            
        print(f"✔ Telemetry Verified Safe: Node [{node_id}] from {addr}. Forwarding metrics to Univac-IX pipeline.")


async def main():
    # Instantiate the monitoring engine core
    safety_guard = MainframeSafetyDiagnosticGuard()
    
    # Initialize asynchronous loop network listener on local port 9999
    loop = asyncio.get_running_loop()
    print("Initializing Multi-Client Asynchronous Network Infrastructure...")
    
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: MainframeNetworkProtocol(safety_guard),
        local_addr=('0.0.0.0', 9999)
    )

    # Keep listener open perpetually
    try:
        await asyncio.sleep(3600)  # Runs server for 1 hour
    finally:
        transport.close()

if __name__ == "__main__":
    # Start the asynchronous runtime daemon on the mainframe
    asyncio.run(main())
