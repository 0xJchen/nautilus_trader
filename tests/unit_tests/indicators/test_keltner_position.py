# -------------------------------------------------------------------------------------------------
#  Copyright (C) 2015-2020 Nautech Systems Pty Ltd. All rights reserved.
#  The use of this source code is governed by the license as found in the LICENSE file.
#  https://nautechsystems.io
# -------------------------------------------------------------------------------------------------

import sys
import unittest

from nautilus_trader.indicators.keltner_position import KeltnerPosition
from tests.test_kit.series import BatterySeries


class KeltnerPositionTests(unittest.TestCase):

    # Fixture Setup
    def setUp(self):
        # Arrange
        self.kp = KeltnerPosition(10, 2.5)

    def test_name_returns_expected_name(self):
        # Act
        # Assert
        self.assertEqual('KeltnerPosition', self.kp.name)

    def test_str_returns_expected_string(self):
        # Act
        # Assert
        self.assertEqual('KeltnerPosition(10, 2.5, EXPONENTIAL, SIMPLE, True, 0.0)', str(self.kp))

    def test_repr_returns_expected_string(self):
        # Act
        # Assert
        self.assertTrue(repr(self.kp).startswith(
            '<KeltnerPosition(10, 2.5, EXPONENTIAL, SIMPLE, True, 0.0) object at'))
        self.assertTrue(repr(self.kp).endswith('>'))

    def test_initialized_without_inputs_returns_false(self):
        # Act
        # Assert
        self.assertEqual(False, self.kp.initialized)

    def test_initialized_with_required_inputs_returns_true(self):
        # Arrange
        for i in range(10):
            self.kp.update(1.00000, 1.00000, 1.00000)

        # Act
        # Assert
        self.assertEqual(True, self.kp.initialized)

    def test_period_returns_expected_value(self):
        # Act
        # Assert
        self.assertEqual(10, self.kp.period)

    def test_k_multiple_returns_expected_value(self):
        # Act
        # Assert
        self.assertEqual(2.5, self.kp.k_multiplier)

    def test_value_with_one_input_returns_zero(self):
        # Arrange
        self.kp.update(1.00020, 1.00000, 1.00010)

        # Act
        # Assert
        self.assertEqual(0.0, self.kp.value)

    def test_value_with_zero_width_input_returns_zero(self):
        # Arrange
        # Arrange
        for i in range(10):
            self.kp.update(1.00000, 1.00000, 1.00000)

        # Act
        # Assert
        self.assertEqual(0.0, self.kp.value)

    def test_value_with_three_inputs_returns_expected_value(self):
        # Arrange
        self.kp.update(1.00020, 1.00000, 1.00010)
        self.kp.update(1.00030, 1.00010, 1.00020)
        self.kp.update(1.00040, 1.00020, 1.00030)

        # Act
        # Assert
        self.assertEqual(0.29752066115754594, self.kp.value)

    def test_value_with_close_on_high_returns_positive_value(self):
        # Arrange
        high = 1.00010
        low = 1.00000

        for i in range(10):
            high += 0.00010
            low += 0.00010
            close = high
            self.kp.update(high=high, low=low, close=close)

        # Act
        # Assert
        self.assertEqual(1.637585941284833, self.kp.value)

    def test_value_with_close_on_low_returns_lower_value(self):
        # Arrange
        high = 1.00010
        low = 1.00000

        for i in range(10):
            high -= 0.00010
            low -= 0.00010
            close = low
            self.kp.update(high=high, low=low, close=close)

        # Act
        # Assert
        self.assertAlmostEqual(-1.637585941284833, self.kp.value)

    def test_value_with_ten_inputs_returns_expected_value(self):
        # Arrange
        self.kp.update(1.00020, 1.00000, 1.00010)
        self.kp.update(1.00030, 1.00010, 1.00020)
        self.kp.update(1.00050, 1.00020, 1.00030)
        self.kp.update(1.00030, 1.00000, 1.00010)
        self.kp.update(1.00030, 1.00010, 1.00020)
        self.kp.update(1.00040, 1.00020, 1.00030)
        self.kp.update(1.00010, 1.00000, 1.00010)
        self.kp.update(1.00030, 1.00010, 1.00020)
        self.kp.update(1.00030, 1.00020, 1.00030)
        self.kp.update(1.00020, 1.00010, 1.00010)

        # Act
        # Assert
        self.assertEqual(-0.14281747514671334, self.kp.value)

    def test_reset_successfully_returns_indicator_to_fresh_state(self):
        # Arrange
        self.kp.update(1.00020, 1.00000, 1.00010)
        self.kp.update(1.00030, 1.00010, 1.00020)
        self.kp.update(1.00040, 1.00020, 1.00030)

        # Act
        self.kp.reset()  # No assertion errors.

    def test_with_battery_signal(self):
        # Arrange
        self.kp = KeltnerPosition(10, 2.5, atr_floor=0.00010)
        battery_signal = BatterySeries.create()
        output = []

        # Act
        for point in BatterySeries.create():
            self.kp.update(point, sys.float_info.epsilon, sys.float_info.epsilon)
            output.append(self.kp.value)

        # Assert
        self.assertEqual(len(battery_signal), len(output))
