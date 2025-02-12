# -------------------------------------------------------------------------------------------------
#  Copyright (C) 2015-2023 Nautech Systems Pty Ltd. All rights reserved.
#  https://nautechsystems.io
#
#  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");
#  You may not use this file except in compliance with the License.
#  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# -------------------------------------------------------------------------------------------------
import pytest

from nautilus_trader.adapters.bybit.common.enums import BybitInstrumentType
from nautilus_trader.adapters.bybit.schemas.symbol import BybitSymbol


class TestBybitSymbol:
    def test_symbol_missing_instrument_type(self):
        with pytest.raises(ValueError):
            BybitSymbol("BTCUSD")

        with pytest.raises(ValueError):
            BybitSymbol("BTCUSD-CDF")

        BybitSymbol("BTCUSD-LINEAR")

    def test_format_symbol(self):
        symbol_str = "ETHUSDT-LINEAR"
        symbol = BybitSymbol(symbol_str)

        assert symbol == "ETHUSDT-LINEAR"
        assert symbol.instrument_type == BybitInstrumentType.LINEAR
        assert symbol.raw_symbol == "ETHUSDT"
