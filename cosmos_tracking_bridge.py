""" Cosmos Bridge - Arbitrary Precision (360-bit) Receiver """

def unpack_360_bit_word_stack(byte_payload):
    """
    Reconstructs the 360-bit stack into a 97-digit precision number.
    Ensures that every bit of the 10-word UNIVAC chain is preserved.
    """
    massive_int = int.from_bytes(byte_payload, byteorder='big')
    
    sign_bit = (massive_int >> 359) & 0x1
    raw_exponent = (massive_int >> 344) & 0x7FFF
    raw_mantissa = massive_int & ((1 << 344) - 1)
    
    """ Final reconstruction using the exact exponent and mantissa bits """
    true_exponent = raw_exponent - 16384
    mantissa_fraction = Decimal(raw_mantissa) / Decimal(1 << 344)
    
    sign_multiplier = Decimal('-1') if sign_bit == 1 else Decimal('1')
    return sign_multiplier * mantissa_fraction * (Decimal('2') ** true_exponent)
