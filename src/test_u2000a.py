import unittest
from unittest.mock import MagicMock, patch
from u2000a import USBPowerSensor

class TestUSBPowerSensor(unittest.TestCase):

    @patch('u2000a.pyvisa.ResourceManager')
    def setUp(self, mock_rm):
        # Mock instrument object with required attributes
        self.mock_instrument = MagicMock()
        
        # Setup ResourceManager mock to return mock instrument
        mock_rm_instance = mock_rm.return_value
        mock_rm_instance.open_resource.return_value = self.mock_instrument

        # Initialize USBPowerSensor, which will set instrument timeout
        self.sensor = USBPowerSensor("USB::FAKE::RESOURCE")

    def test_identify(self):
        self.mock_instrument.query.return_value = 'Keysight,U2000A,MY12345678,1.0.0\n'
        result = self.sensor.identify()
        self.mock_instrument.query.assert_called_with("*IDN?")
        self.assertEqual(result, 'Keysight,U2000A,MY12345678,1.0.0')

    def test_measure_power(self):
        self.mock_instrument.query.return_value = '0.005\n'
        result = self.sensor.measure_power()
        self.mock_instrument.query.assert_called_with("MEASure?")
        self.assertEqual(result, 0.005)

    def test_calibrate_zero_internal(self):
        self.sensor.calibrate_zero_internal()
        expected_calls = [
            unittest.mock.call("CALibration:ZERO:TYPE INTernal"),
            unittest.mock.call("CALibration:ZERO:AUTO ONCE")
        ]
        self.mock_instrument.write.assert_has_calls(expected_calls)

    def test_calibrate_zero_external(self):
        self.sensor.calibrate_zero_external()
        expected_calls = [
            unittest.mock.call("CALibration:ZERO:TYPE EXTernal"),
            unittest.mock.call("CALibration:ZERO:AUTO ONCE")
        ]
        self.mock_instrument.write.assert_has_calls(expected_calls)

    def test_set_display_unit_dbm(self):
        self.sensor.set_display_unit('dBm')
        self.mock_instrument.write.assert_called_with("UNIT:POWer DBM")

    def test_set_display_unit_mw(self):
        self.sensor.set_display_unit('mW')
        self.mock_instrument.write.assert_called_with("UNIT:POWer W")

    def test_set_display_unit_invalid(self):
        with self.assertRaises(ValueError):
            self.sensor.set_display_unit('invalid')

    def tearDown(self):
        self.sensor.close()
        self.mock_instrument.close.assert_called()
        self.sensor.rm.close.assert_called()

if __name__ == '__main__':
    unittest.main()
