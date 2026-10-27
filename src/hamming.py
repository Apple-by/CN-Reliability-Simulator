
def hamming_encode(data):
    """Encode data using even-parity Hamming Code."""
    if not data or any(bit not in "01" for bit in data):
        raise ValueError("Data must be a non-empty binary string.")

    m = len(data)
    r = 0

    while 2 ** r < m + r + 1:
        r += 1

    n = m + r
    code = ["0"] * (n + 1)

    data_index = 0

    for pos in range(1, n + 1):
        if pos & (pos - 1):
            code[pos] = data[data_index]
            data_index += 1

    for i in range(r):
        parity_pos = 2 ** i
        parity = 0

        for pos in range(1, n + 1):
            if pos & parity_pos:
                parity ^= int(code[pos])

        code[parity_pos] = str(parity)

    return "".join(code[1:])


def hamming_decode(received):
    """Correct one-bit errors and return decoded data and status."""
    if not received or any(bit not in "01" for bit in received):
        raise ValueError("Received codeword must contain only binary bits.")

    n = len(received)
    r = 0

    while 2 ** r < n + 1:
        r += 1

    if n != 2 ** r - r - 1 and n != 2 ** r - 1:
        raise ValueError("Unsupported Hamming codeword length.")

    code = ["0"] + list(received)
    syndrome = 0

    for i in range(r):
        parity_pos = 2 ** i
        parity = 0

        for pos in range(1, n + 1):
            if pos & parity_pos:
                parity ^= int(code[pos])

        if parity:
            syndrome += parity_pos

    if syndrome > n:
        raise ValueError("Invalid syndrome: cannot correct this codeword.")

    corrected = syndrome != 0

    if corrected:
        code[syndrome] = "1" if code[syndrome] == "0" else "0"

    data = "".join(
        code[pos]
        for pos in range(1, n + 1)
        if pos & (pos - 1)
    )

    return data, corrected, syndrome
