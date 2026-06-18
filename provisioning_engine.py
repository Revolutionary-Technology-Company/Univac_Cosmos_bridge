import os
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

class MainframeProvisioningEngine:
    def __init__(self):
        # Master Static ECDH Key Pair belonging to your core cloud mainframe frame
        self.mainframe_private_key = ec.generate_private_key(ec.SECP256R1())
        self.mainframe_public_key = self.mainframe_private_key.public_key()

    def handle_client_handshake(self, client_public_key_bytes):
        """
        Processes a registration request from a newly connected client device.
        Derives an identical session-locked HMAC secret key using ECDH.
        """
        try:
            # 1. Deserialize the incoming client public key payload
            peer_public_key = ec.EllipticCurvePublicKey.from_encoded_point(
                ec.SECP256R1(), client_public_key_bytes
            )
            
            # 2. Compute the mathematical shared cryptographic secret
            shared_secret = self.mainframe_private_key.exchange(
                ec.ECDH(), peer_peer_public_key
            )
            
            # 3. Apply HKDF to safely stretch the raw secret into a cryptographically strong HMAC key
            ephemeral_hmac_key = HKDF(
                algorithm=hashes.SHA256(),
                length=32, # Output a 256-bit symmetric key
                salt=None,
                info=b"univac_cosmos_bridge_session_provisioning"
            ).derive(shared_secret)
            
            return {
                "status": "PROVISIONED_SUCCESS",
                "session_hmac_key": ephemeral_hmac_key,
                "mainframe_pub_bytes": self.mainframe_public_key.encoded_point_x962()
            }
            
        except Exception as e:
            return {"status": "PROVISIONING_FAILED", "reason": str(e), "session_hmac_key": None}

# --- LIFECYCLE RUNTIME TEST ---
if __name__ == "__main__":
    mainframe = MainframeProvisioningEngine()
    
    # Client App (Basic-Aviation-Knowledge) boots up locally
    client_private = ec.generate_private_key(ec.SECP256R1())
    client_public_bytes = client_private.public_key().encoded_point_x962()
    
    # Execution: Client transmits client_public_bytes to mainframe server port
    provisioning_payload = mainframe.handle_client_handshake(client_public_bytes)
    
    print("=== AUTOMATED DEVICE PROVISIONING ===")
    print(f"Key Handshake Status: {provisioning_payload['status']}")
    print(f"Generated Ephemeral Secret String Matrix: {provisioning_payload['session_hmac_key'].hex()}")
