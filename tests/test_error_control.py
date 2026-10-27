
import unittest

from src.crc import crc_encode, crc_check
from src.hamming import hamming_encode, hamming_decode


class TestCRC(unittest.TestCase):
    def test_clean_message(self):
        codeword = crc_encode("1011")
        self.assertTrue(crc_check(codeword))

    def test_single_bit_error(self):
        codeword = crc_encode("1011")
        corrupted = list(codeword)
        corrupted[0] = "1" if corrupted[0] == "0" else "0"
        self.assertFalse(crc_check("".join(corrupted)))

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            crc_encode("10A1")


class TestHamming(unittest.TestCase):
    def test_clean_message(self):
        codeword = hamming_encode("1011")
        decoded, corrected, syndrome = hamming_decode(codeword)

        self.assertEqual(decoded, "1011")
        self.assertFalse(corrected)
        self.assertEqual(syndrome, 0)

    def test_single_bit_correction(self):
        codeword = list(hamming_encode("1011"))
        codeword[2] = "1" if codeword[2] == "0" else "0"

        decoded, corrected, syndrome = hamming_decode("".join(codeword))

        self.assertEqual(decoded, "1011")
        self.assertTrue(corrected)
        self.assertEqual(syndrome, 3)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            hamming_encode("10A1")


if __name__ == "__main__":
    unittest.main()
