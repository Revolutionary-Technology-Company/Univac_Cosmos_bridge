""" cosmos_tracking_bridge.py """
""" Space Force Deep-Space Arbitrary Precision (360-bit) Tracking Bridge """
""" Optimized: Else-Less Guard Clauses | 10-Word Stacking | 97-Digit Precision """

import socket
import struct
from decimal import Decimal, getcontext

""" Establish absolute mathematical limits for the Space Force tracking grid """
""" 100 digits ensures the 97-digit 10-word stack never overflows the memory context """
getcontext().prec = 100

""" ===================================================================== """
""" --- PURE MATH KERNELS (THE ARBITRARY PRECISION ENGINE) --- """
""" NO @njit here. Numba cannot compile 360-bit arbitrary precision.      """
""" This relies on Python's heavily optimized C-backend decimal library.  """
""" ===================================================================== """

def unpack_360_bit_word_stack(byte_payload):
    """ 
    Reconstructs a single 97-digit precision number from a 45-byte (360-bit) payload.
    Conforms perfectly to the UNIVAC 10-word stacking architecture.
    """
    
    """ GUARD 1: Payload size mismatch (Prevents buffer underruns) """
    if len(byte_payload) != 45:
        return Decimal('0.0')

    """ 1. Convert the raw 45 bytes into a single massive 360-bit integer """
    massive_int = int.from_bytes(byte_payload, byteorder='big', signed=False)
    
    """ 
    2. Anatomy of the 10-Word Stack (360 bits total)
    Bit 359: Sign Bit (1 bit)
    Bits 344-358: Exponent (15 bits, Bias 16384)
    Bits 0-343: Mantissa (344 bits of pure fractional precision)
    """
    
    sign_bit = (massive_int >> 359) & 0x1
    raw_exponent = (massive_int >> 344) & 0x7FFF
    raw_mantissa = massive_int & ((1 << 344) - 1)
    
    """ GUARD 2: Absolute Zero """
    if raw_exponent == 0 and raw_mantissa == 0:
        return Decimal('0.0')
        
    """ 3. Reconstruct the Exponent """
    true_exponent = raw_exponent - 16384
    
    """ 4. Reconstruct the 97-Digit Mantissa """
    """ The mantissa is stored as a binary fraction. We divide by 2^344 to get [0.5, 1.0) """
    mantissa_fraction = Decimal(raw_mantissa) / Decimal(1 << 344)
    
    """ 5. Assemble the final arbitrary-precision float """
    """ Value = (-1)^Sign * Mantissa * 2^Exponent """
    sign_multiplier = Decimal('-1') if sign_bit == 1 else Decimal('1')
    base_two = Decimal('2')
    
    final_value = sign_multiplier * mantissa_fraction * (base_two ** true_exponent)
    
    return final_value


def validate_deep_space_vector(x_au, y_au, z_au):
    """ Enforces geometric reality checks on the massive numbers. """
    
    """ GUARD 1: Object is within Earth's atmosphere (Should be handled by standard Aegis, not Cosmos) """
    if abs(x_au) < Decimal('0.0001') and abs(y_au) < Decimal('0.0001') and abs(z_au) < Decimal('0.0001'):
        return False
        
    """ HAPPY PATH """
    return True


""" ===================================================================== """
""" --- THE ORCHESTRATOR (THE COSMOS RECEIVER) --- """
""" ===================================================================== """

class CosmosTrackingBridge:
    """ Listens for 135-byte packed structures from the flight computer and decodes them. """
    
    def __init__(self, port=12010):
        self.PORT = int(port)
        
        """ 45 bytes per coordinate (X, Y, Z) = 135 bytes total """
        self.EXPECTED_PAYLOAD_SIZE = 135 
        
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(("0.0.0.0", self.PORT))
        self.udp_socket.setblocking(False)

    def process_galactic_packet(self, raw_bytes, ip_address):
        """ Slices the payload into three 10-word stacks. """
        
        """ GUARD 1: Buffer length mismatch """
        if len(raw_bytes) != self.EXPECTED_PAYLOAD_SIZE:
            return {"status": "REJECTED_BUFFER_SIZE"}
            
        """ Slice the 135 bytes into three 45-byte (360-bit) chunks """
        x_bytes = raw_bytes[0:45]
        y_bytes = raw_bytes[45:90]
        z_bytes = raw_bytes[90:135]
        
        """ Extract 97-digit precision vectors """
        x_au = unpack_360_bit_word_stack(x_bytes)
        y_au = unpack_360_bit_word_stack(y_bytes)
        z_au = unpack_360_bit_word_stack(z_bytes)
        
        """ GUARD 2: Deep space boundary validation """
        if not validate_deep_space_vector(x_au, y_au, z_au):
            return {"status": "REJECTED_TERRESTRIAL_NOISE"}
            
        """ HAPPY PATH: Format string to display all 97 digits for the UI """
        return {
            "status": "TRACKING_LOCKED",
            "source_ip": str(ip_address),
            "precision_level": "360_BIT_10_WORD_STACK",
            "vector_x_au": format(x_au, '.97f'),
            "vector_y_au": format(y_au, '.97f'),
            "vector_z_au": format(z_au, '.97f')
        }

    def execute_listening_tick(self):
        """ Non-blocking receiver. """
        try:
            raw_bytes, address = self.udp_socket.recvfrom(1024)
            ip_address = address[0]
            return self.process_galactic_packet(raw_bytes, ip_address)
        except BlockingIOError:
            return None
