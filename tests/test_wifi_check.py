import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "wifi"))
import wifi_check as w  # noqa: E402


class ParseTests(unittest.TestCase):
    def test_netsh_ssid_ignores_bssid(self):
        text = "    Name : Wi-Fi\n    SSID                   : Freebox_ab\n    BSSID                  : aa:bb:cc"
        self.assertEqual(w.parse_netsh(text), "Freebox_ab")

    def test_netsh_no_ssid(self):
        self.assertIsNone(w.parse_netsh("    State : disconnected"))

    def test_nmcli_escaped_colon(self):
        rows = w.parse_nmcli_terse("Livebox\\:5G:802-11-wireless:wlan0\nlo:loopback:lo")
        self.assertEqual(rows[0], ["Livebox:5G", "802-11-wireless", "wlan0"])
        self.assertEqual(rows[1][1], "loopback")


if __name__ == "__main__":
    unittest.main()
