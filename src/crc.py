
def binary_remainder(data, divisor):
    """Return the modulo-2 division remainder."""
    bits = list(data)
    divisor_len = len(divisor)

    for i in range(len(bits) - divisor_len + 1):
        if bits[i] == "1":
            for j in range(divisor_len):
                bits[i + j] = str(
                    int(bits[i + j]) ^ int(divisor[j])
                )

    return "".join(bits[-(divisor_len - 1):]) if divisor_len > 1 else ""


def crc_encode(data, generator="1101"):
    """Append CRC bits to the original binary data."""
    if not data or any(bit not in "01" for bit in data):
        raise ValueError("Data must be a non-empty binary string.")

    if len(generator) < 2 or generator[0] != "1":
        raise ValueError("Generator must start with 1 and have length >= 2.")

    if any(bit not in "01" for bit in generator):
        raise ValueError("Generator must contain only 0 and 1.")

    padded_data = data + "0" * (len(generator) - 1)
    remainder = binary_remainder(padded_data, generator)

    return data + remainder


def crc_check(codeword, generator="1101"):
    """Return True if the received codeword has zero CRC remainder."""
    if not codeword or any(bit not in "01" for bit in codeword):
        raise ValueError("Codeword must be a non-empty binary string.")

    if len(generator) < 2 or generator[0] != "1":
        raise ValueError("Invalid generator polynomial.")

    if any(bit not in "01" for bit in generator):
        raise ValueError("Generator must contain only 0 and 1.")

    remainder = binary_remainder(codeword, generator)
    return all(bit == "0" for bit in remainder)
