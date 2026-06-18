import hmac
import hashlib
import json
import time

# Simulation Mainframe Registry of authorized devices and their private keys
# In product, this database is managed securely on your mainframe infrastructure
SOCIETAL_KEY_REGISTRY = {
    "TESLA_MODEL_Y_098A": b"secure_mainframe_secret_key_abc123!!",
    "MOBILE_NODE_IPHONE_77": b"aviation_knowledge_app_key_xyz987$$",
    "UNIVAC_MAINFRAME_RELO": b"vintage_hardware_restored_key_5544##"
}

class SovereignCryptoAuthEngine:
    @staticmethod
    def generate_signed_packet(node_id, secret_key, operational_data_dict):
        """
        [CLIENT SIDE] Runs on the smartphone app or smart car array.
        Packages data parameters, injects a timestamp, and appends a secure signature.
        """
        # 1. Inject temporal synchronization parameters to prevent replay exploits
        packet_payload = operational_data_dict.copy()
        packet_payload["node_id"] = node_id
        packet_payload["timestamp"] = time.time()  # High-precision UNIX epoch string
        
        # 2. Serialize payload data cleanly to create an immutable string base
        # Sorting keys guarantees identical string generation on both client and server
        serialized_payload = json.dumps(packet_payload, sort_keys=True)
        
        # 3. Compute HMAC-SHA256 signature
        signature = hmac.new(
            key=secret_key,
            msg=serialized_payload.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # 4. Wrap everything into the final network datagram payload transmission
        network_packet = {
            "payload": packet_payload,
            "signature": signature
        }
        return json.dumps(network_packet)

    @staticmethod
    def verify_incoming_packet(raw_network_json, allowed_skew_seconds=5.0):
        """
        [MAINFRAME SIDE] Processes incoming network data streams instantly.
        Validates timestamp alignment, pulls the key, and signs to match.
        """
        try:
            # Parse network envelope packing structure
            envelope = json.loads(raw_network_json)
            payload = envelope.get("payload")
            client_signature = envelope.get("signature")
            
            if not payload or not client_signature:
                return False, "Malformed packet envelope structure."

            node_id = payload.get("node_id")
            packet_time = float(payload.get("timestamp", 0))
            
            # A. REPLAY ATTACK MITIGATION: Verify temporal bounding window alignment
            current_time = time.time()
            if abs(current_time - packet_time) > allowed_skew_seconds:
                return False, f"Packet rejected. Time delta skew too high ({abs(current_time - packet_time):.2f}s delay)."
                
            # B. AUTHENTICATION SEARCH: Resolve trusted key for claiming hardware node identity
            if node_id not in SOCIETAL_KEY_REGISTRY:
                return False, f"Unauthorized access denied. Device ID [{node_id}] not found in database registry."
                
            secret_key = SOCIETAL_KEY_REGISTRY[node_id]
            
            # C. INTEGRITY VERIFICATION: Regenerate matching string and signature
            serialized_payload = json.dumps(payload, sort_keys=True)
            computed_signature = hmac.new(
                key=secret_key,
                msg=serialized_payload.encode('utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()
            
            # Use constant-time comparison hmac.compare_digest to prevent timing-attack exploits
            if hmac.compare_digest(computed_signature, client_signature):
                return True, f"Authentication Success. Payload verified for [{node_id}]."
            else:
                return False, "Tampering detected. Payload signature mismatch."
                
        except Exception as e:
            return False, f"Cryptographic parsing crash error: {str(e)}"

# --- ACTIVE CRYPTOGRAPHIC LOOP PROOF CONSOLE ---
if __name__ == "__main__":
    print("Initializing Cryptographic Packet Signing Core...")
    auth_engine = SovereignCryptoAuthEngine()
    
    # Raw sensor data compiled by the mobile app/sensor arrays before transport
    sample_telemetry = {
        "frequency_hz": 24.12e9,
        "output_power_watts": 1.5,
        "antenna_gain": 4.0,
        "assert_contains_biology": False
    }
    
    # -------------------------------------------------------------
    # SCENARIO 1: Valid client maps and signs its transmission telemetry
    # -------------------------------------------------------------
    print("\n[Scenario 1: Authenticated Node Transmitting Data]")
    client_id = "TESLA_MODEL_Y_098A"
    client_private_key = SOCIETAL_KEY_REGISTRY[client_id]
    
    valid_network_datagram = auth_engine.generate_signed_packet(
        node_id=client_id, secret_key=client_private_key, operational_data_dict=sample_telemetry
    )
    
    # Mainframe receives data over the network port socket listener
    success, audit_msg = auth_engine.verify_incoming_packet(valid_network_datagram)
    print(f"Mainframe Fire-Wall Result -> Verified: {success} | Message: {audit_msg}")

    # -------------------------------------------------------------
    # SCENARIO 2: Spoofed device or payload modification attempt
    # -------------------------------------------------------------
    print("\n[Scenario 2: Rogue Device Intercepts and Modifies Data]")
    # Malicious actor decodes the payload, increases power limits unsafely to 500 Watts,
    # and tries re-injecting the stream back to the mainframe server
    intercepted_dict = json.loads(valid_network_datagram)
    intercepted_dict["payload"]["output_power_watts"] = 500.0  # Modified value
    corrupted_network_datagram = json.dumps(intercepted_dict)
    
    success, audit_msg = auth_engine.verify_incoming_packet(corrupted_network_datagram)
    print(f"Mainframe Fire-Wall Result -> Verified: {success} | Message: {audit_msg}")
