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

from nautilus_trader.adapters.databento.loaders import DatabentoDataLoader
from nautilus_trader.adapters.databento.types import DatabentoImbalance
from nautilus_trader.adapters.databento.types import DatabentoStatistics
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType
from nautilus_trader.model.data import OrderBookDelta
from nautilus_trader.model.data import OrderBookDeltas
from nautilus_trader.model.data import QuoteTick
from nautilus_trader.model.data import TradeTick
from nautilus_trader.model.enums import AggressorSide
from nautilus_trader.model.enums import AssetClass
from nautilus_trader.model.enums import AssetType
from nautilus_trader.model.enums import BookAction
from nautilus_trader.model.enums import OptionKind
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.identifiers import Symbol
from nautilus_trader.model.identifiers import TradeId
from nautilus_trader.model.instruments import Equity
from nautilus_trader.model.instruments import FuturesContract
from nautilus_trader.model.instruments import OptionsContract
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity
from tests import TEST_DATA_DIR


DATABENTO_TEST_DATA_DIR = TEST_DATA_DIR / "databento"


@pytest.mark.skip(reason="Used for initial development")
def test_loader_definition_glbx_all_symbols() -> None:
    # Arrange
    loader = DatabentoDataLoader()
    path = DATABENTO_TEST_DATA_DIR / "definition-glbx-all-symbols2.dbn.zst"

    # Act
    data = loader.from_dbn(path)

    # Assert
    assert len(data) == 10_000_000


def test_get_publishers() -> None:
    # Arrange
    loader = DatabentoDataLoader()

    # Act
    result = loader.publishers

    # Assert
    assert len(result) == 43  # From built-in map


def test_get_instruments_when_no_instruments() -> None:
    # Arrange
    loader = DatabentoDataLoader()

    # Act
    result = loader.instruments

    # Assert
    assert len(result) == 0  # No instruments loaded yet


def test_get_instruments() -> None:
    # Arrange
    loader = DatabentoDataLoader()
    path = DATABENTO_TEST_DATA_DIR / "definition-glbx-es-fut.dbn.zst"

    # Act
    loader.load_instruments(path)
    instruments = loader.instruments

    # Assert
    expected_id = InstrumentId.from_str("ESM3.GLBX")
    assert len(instruments) == 1
    assert instruments[expected_id].id == expected_id


def test_loader_definition_glbx_futures() -> None:
    # Arrange
    loader = DatabentoDataLoader()
    path = DATABENTO_TEST_DATA_DIR / "definition-glbx-es-fut.dbn.zst"

    # Act
    data = loader.from_dbn(path)

    # Assert
    assert len(data) == 2
    assert isinstance(data[0], FuturesContract)
    assert isinstance(data[1], FuturesContract)
    instrument = data[0]
    assert instrument.id == InstrumentId.from_str("ESM3.GLBX")
    assert instrument.raw_symbol == Symbol("ESM3")
    assert instrument.asset_class == AssetClass.INDEX
    assert instrument.asset_type == AssetType.FUTURE
    assert instrument.quote_currency == USD
    assert not instrument.is_inverse
    assert instrument.underlying == "ES"
    assert instrument.price_precision == 2
    assert instrument.price_increment == Price.from_str("0.25")
    assert instrument.size_precision == 0
    assert instrument.size_increment == 1
    assert instrument.multiplier == 1
    assert instrument.lot_size == 1
    assert instrument.ts_event == 1680451436501583647
    assert instrument.ts_init == 1680451436501583647


def test_loader_definition_glbx_futures_spread() -> None:
    # Arrange
    loader = DatabentoDataLoader()
    path = DATABENTO_TEST_DATA_DIR / "definition-glbx-es-futspread.dbn.zst"

    # Act
    data = loader.from_dbn(path)

    # Assert
    assert len(data) == 2
    assert isinstance(data[0], FuturesContract)
    assert isinstance(data[1], FuturesContract)
    instrument = data[0]
    assert instrument.id == InstrumentId.from_str("ESH5-ESM5.GLBX")
    assert instrument.raw_symbol == Symbol("ESH5-ESM5")
    assert instrument.asset_class == AssetClass.INDEX
    assert instrument.asset_type == AssetType.FUTURE
    assert instrument.quote_currency == USD
    assert not instrument.is_inverse
    assert instrument.underlying == "ES"
    assert instrument.price_precision == 2
    assert instrument.price_increment == Price.from_str("0.05")
    assert instrument.size_precision == 0
    assert instrument.size_increment == 1
    assert instrument.multiplier == 1
    assert instrument.lot_size == 1
    assert instrument.ts_event == 1690848000000000000
    assert instrument.ts_init == 1690848000000000000


def test_loader_definition_glbx_options() -> None:
    # Arrange
    loader = DatabentoDataLoader()
    path = DATABENTO_TEST_DATA_DIR / "definition-glbx-es-opt.dbn.zst"

    # Act
    data = loader.from_dbn(path)

    # Assert
    assert len(data) == 2
    assert isinstance(data[0], OptionsContract)
    assert isinstance(data[1], OptionsContract)
    instrument = data[0]
    assert instrument.id == InstrumentId.from_str("ESM4 C4250.GLBX")
    assert instrument.raw_symbol == Symbol("ESM4 C4250")
    assert instrument.asset_class == AssetClass.EQUITY
    assert instrument.asset_type == AssetType.OPTION
    assert instrument.quote_currency == USD
    assert not instrument.is_inverse
    assert instrument.underlying == "ESM4"
    assert instrument.kind == OptionKind.CALL
    assert instrument.strike_price == Price.from_str("4250.00")
    assert instrument.price_precision == 2
    assert instrument.price_increment == Price.from_str("0.01")
    assert instrument.size_precision == 0
    assert instrument.size_increment == 1
    assert instrument.multiplier == 1
    assert instrument.lot_size == 1
    assert instrument.ts_event == 1690848000000000000
    assert instrument.ts_init == 1690848000000000000


def test_loader_definition_opra_pillar() -> None:
    # Arrange
    loader = DatabentoDataLoader()
    path = DATABENTO_TEST_DATA_DIR / "definition-opra.dbn.zst"

    # Act
    data = loader.from_dbn(path)

    # Assert
    assert len(data) == 2
    assert isinstance(data[0], OptionsContract)
    assert isinstance(data[1], OptionsContract)
    instrument = data[0]
    assert instrument.id == InstrumentId.from_str("SPY   240119P00340000.OPRA")  # OSS symbol
    assert instrument.raw_symbol == Symbol("SPY   240119P00340000")
    assert instrument.asset_class == AssetClass.EQUITY
    assert instrument.asset_type == AssetType.OPTION
    assert instrument.quote_currency == USD
    assert not instrument.is_inverse
    assert instrument.underlying == "SPY"
    assert instrument.kind == OptionKind.PUT
    assert instrument.strike_price == Price.from_str("340.00")
    assert instrument.price_precision == 2
    assert instrument.price_increment == Price.from_str("0.01")
    assert instrument.size_precision == 0
    assert instrument.size_increment == 1
    assert instrument.multiplier == 1
    assert instrument.lot_size == 1
    assert instrument.ts_event == 1690885800419158943
    assert instrument.ts_init == 1690885800419158943


def test_loader_with_xnasitch_definition() -> None:
    # Arrange
    loader = DatabentoDataLoader()
    path = DATABENTO_TEST_DATA_DIR / "definition.dbn.zst"

    # Act
    data = loader.from_dbn(path)

    # Assert
    assert len(data) == 2
    assert isinstance(data[0], Equity)
    assert isinstance(data[1], Equity)
    instrument = data[0]
    assert instrument.id == InstrumentId.from_str("MSFT.XNAS")
    assert instrument.raw_symbol == Symbol("MSFT")
    assert instrument.asset_class == AssetClass.EQUITY
    assert instrument.asset_type == AssetType.SPOT
    assert instrument.quote_currency == USD
    assert not instrument.is_inverse
    assert instrument.price_precision == 2
    assert instrument.price_increment == Price.from_str("0.01")
    assert instrument.size_precision == 0
    assert instrument.size_increment == 1
    assert instrument.multiplier == 1
    assert instrument.lot_size == 100
    assert instrument.ts_event == 1633331241618029519
    assert instrument.ts_init == 1633331241618029519


def test_loader_with_xnasitch_mbo() -> None:
    # Arrange
    loader = DatabentoDataLoader()
    path = DATABENTO_TEST_DATA_DIR / "mbo.dbn.zst"

    # Act
    data = loader.from_dbn(path)

    # Assert
    assert len(data) == 2
    assert isinstance(data[0], OrderBookDelta)
    assert isinstance(data[1], OrderBookDelta)
    delta = data[0]
    assert delta.instrument_id == InstrumentId.from_str("ESH1.GLBX")
    assert delta.action == BookAction.DELETE
    assert delta.order.side == OrderSide.BUY
    assert delta.order.price == Price.from_str("3722.75")
    assert delta.order.size == Quantity.from_int(1)
    assert delta.order.order_id == 647784973705
    assert delta.flags == 128
    assert delta.sequence == 1170352
    assert delta.ts_event == 1609160400000704060
    assert delta.ts_init == 1609160400000704060


def test_loader_with_mbp_1() -> None:
    # Arrange
    loader = DatabentoDataLoader()
    path = DATABENTO_TEST_DATA_DIR / "mbp-1.dbn.zst"

    # Act
    data = loader.from_dbn(path)

    # Assert
    assert len(data) == 2
    assert isinstance(data[0], QuoteTick)
    assert isinstance(data[1], QuoteTick)
    quote = data[0]
    assert quote.instrument_id == InstrumentId.from_str("ESH1.GLBX")
    assert quote.bid_price == Price.from_str("3720.25")
    assert quote.ask_price == Price.from_str("3720.50")
    assert quote.bid_size == Quantity.from_int(24)
    assert quote.ask_size == Quantity.from_int(11)
    assert quote.ts_event == 1609160400006136329
    assert quote.ts_init == 1609160400006136329


def test_loader_with_mbp_10() -> None:
    # Arrange
    loader = DatabentoDataLoader()
    path = DATABENTO_TEST_DATA_DIR / "mbp-10.dbn.zst"

    # Act
    data = loader.from_dbn(path)

    # Assert
    assert len(data) == 2
    assert isinstance(data[0], OrderBookDeltas)
    assert isinstance(data[1], OrderBookDeltas)
    deltas = data[0]
    assert deltas.instrument_id == InstrumentId.from_str("ESH1.GLBX")
    assert len(deltas.deltas) == 21


def test_loader_with_tbbo() -> None:
    # Arrange
    loader = DatabentoDataLoader()
    path = DATABENTO_TEST_DATA_DIR / "tbbo.dbn.zst"

    # Act
    data = loader.from_dbn(path)

    # Assert
    assert len(data) == 4
    assert isinstance(data[0], QuoteTick)
    assert isinstance(data[1], TradeTick)
    assert isinstance(data[2], QuoteTick)
    assert isinstance(data[3], TradeTick)
    quote = data[0]
    assert quote.instrument_id == InstrumentId.from_str("ESH1.GLBX")
    assert quote.bid_price == Price.from_str("3720.25")
    assert quote.ask_price == Price.from_str("3720.50")
    assert quote.bid_size == Quantity.from_int(26)
    assert quote.ask_size == Quantity.from_int(7)
    assert quote.ts_event == 1609160400099150057
    assert quote.ts_init == 1609160400099150057
    trade = data[1]
    assert trade.instrument_id == InstrumentId.from_str("ESH1.GLBX")
    assert trade.price == Price.from_str("3720.25")
    assert trade.size == Quantity.from_int(5)
    assert trade.aggressor_side == AggressorSide.BUYER
    assert trade.trade_id == TradeId("1170380")
    assert trade.ts_event == 1609160400099150057
    assert trade.ts_init == 1609160400099150057


def test_loader_with_trades() -> None:
    # Arrange
    loader = DatabentoDataLoader()
    path = DATABENTO_TEST_DATA_DIR / "trades.dbn.zst"

    # Act
    data = loader.from_dbn(path)

    # Assert
    assert len(data) == 2
    assert isinstance(data[0], TradeTick)
    assert isinstance(data[1], TradeTick)
    trade = data[0]
    assert trade.instrument_id == InstrumentId.from_str("ESH1.GLBX")
    assert trade.price == Price.from_str("3720.25")
    assert trade.size == Quantity.from_int(5)
    assert trade.aggressor_side == AggressorSide.BUYER
    assert trade.trade_id == TradeId("1170380")
    assert trade.ts_event == 1609160400099150057
    assert trade.ts_init == 1609160400099150057


def test_loader_with_ohlcv_1s() -> None:
    # Arrange
    loader = DatabentoDataLoader()
    path = DATABENTO_TEST_DATA_DIR / "ohlcv-1s.dbn.zst"

    # Act
    data = loader.from_dbn(path)

    # Assert
    assert len(data) == 2
    assert isinstance(data[0], Bar)
    assert isinstance(data[1], Bar)
    bar = data[0]
    assert bar.bar_type == BarType.from_str("ESH1.GLBX-1-SECOND-LAST-EXTERNAL")
    assert bar.open == Price.from_str("3720.25")
    assert bar.high == Price.from_str("3720.50")
    assert bar.low == Price.from_str("3720.25")
    assert bar.close == Price.from_str("3720.50")
    assert bar.volume == Price.from_str("0")
    assert bar.ts_event == 1609160401000000000
    assert bar.ts_init == 1609160401000000000


def test_loader_with_ohlcv_1m() -> None:
    # Arrange
    loader = DatabentoDataLoader()
    path = DATABENTO_TEST_DATA_DIR / "ohlcv-1m.dbn.zst"

    # Act
    data = loader.from_dbn(path)

    # Assert
    assert len(data) == 2
    assert isinstance(data[0], Bar)
    assert isinstance(data[1], Bar)
    bar = data[0]
    assert bar.bar_type == BarType.from_str("ESH1.GLBX-1-MINUTE-LAST-EXTERNAL")
    assert bar.open == Price.from_str("3720.25")
    assert bar.ts_event == 1609160460000000000
    assert bar.ts_init == 1609160460000000000


def test_loader_with_ohlcv_1h() -> None:
    # Arrange
    loader = DatabentoDataLoader()
    path = DATABENTO_TEST_DATA_DIR / "ohlcv-1h.dbn.zst"

    # Act
    data = loader.from_dbn(path)

    # Assert
    assert len(data) == 2
    assert isinstance(data[0], Bar)
    assert isinstance(data[1], Bar)
    bar = data[0]
    assert bar.bar_type == BarType.from_str("ESH1.GLBX-1-HOUR-LAST-EXTERNAL")
    assert bar.open == Price.from_str("3720.25")  # Bug??
    assert bar.ts_event == 1609164000000000000
    assert bar.ts_init == 1609164000000000000


def test_loader_with_ohlcv_1d() -> None:
    # Arrange
    loader = DatabentoDataLoader()
    path = DATABENTO_TEST_DATA_DIR / "ohlcv-1d.dbn.zst"

    # Act
    data = loader.from_dbn(path)

    # Assert
    assert len(data) == 0  # ??


def test_loader_with_imbalance() -> None:
    # Arrange
    loader = DatabentoDataLoader()
    path = DATABENTO_TEST_DATA_DIR / "imbalance.dbn.zst"

    # Act
    data = loader.from_dbn(path)

    # Assert
    assert len(data) == 4
    assert isinstance(data[0], DatabentoImbalance)


def test_loader_with_statistics() -> None:
    # Arrange
    loader = DatabentoDataLoader()
    path = DATABENTO_TEST_DATA_DIR / "statistics.dbn.zst"

    # Act
    data = loader.from_dbn(path)

    # Assert
    assert len(data) == 4
    assert isinstance(data[0], DatabentoStatistics)
