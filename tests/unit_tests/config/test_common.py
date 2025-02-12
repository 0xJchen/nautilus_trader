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

import msgspec.json
import pandas as pd
import pytest

from nautilus_trader.config import ImportableConfig
from nautilus_trader.config.common import CUSTOM_DECODINGS
from nautilus_trader.config.common import CUSTOM_ENCODINGS
from nautilus_trader.config.common import msgspec_decoding_hook
from nautilus_trader.config.common import msgspec_encoding_hook
from nautilus_trader.config.common import register_config_decoding
from nautilus_trader.config.common import register_config_encoding
from nautilus_trader.core.uuid import UUID4
from nautilus_trader.model.data import BarType
from nautilus_trader.model.identifiers import ComponentId
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity


def test_importable_config_simple() -> None:
    # Arrange
    raw = msgspec.json.encode(
        {
            "path": "nautilus_trader.adapters.binance.config:BinanceDataClientConfig",
            "config": {
                "api_key": "abc",
            },
        },
    )

    # Act
    config = msgspec.json.decode(raw, type=ImportableConfig).create()

    # Assert
    assert config.api_key == "abc"


def test_register_custom_encodings() -> None:
    # Arrange
    test_encoder = str

    # Act
    register_config_encoding(Price, test_encoder)

    # Assert
    assert CUSTOM_ENCODINGS[Price] == test_encoder


def test_register_custom_decodings() -> None:
    # Arrange
    test_decoder = Price.from_str
    register_config_decoding(Price, test_decoder)

    # Assert
    assert CUSTOM_DECODINGS[Price] == test_decoder


def test_encoding_uuid4() -> None:
    # Arrange
    obj = UUID4()

    # Act
    result = msgspec_encoding_hook(obj)

    # Assert
    assert result == obj.value


def test_decoding_uuid4() -> None:
    # Arrange
    obj_type = UUID4
    obj = "b07bf5fa-cee6-49eb-91b1-a08d09d22a1a"

    # Act
    result = msgspec_decoding_hook(obj_type, obj)

    # Assert
    assert result == UUID4(obj)


def test_encoding_component_id() -> None:
    # Arrange
    obj = ComponentId("TRADER-001")

    # Act
    result = msgspec_encoding_hook(obj)

    # Assert
    assert result == obj.value


def test_decoding_component_id() -> None:
    # Arrange
    obj_type = ComponentId
    obj = "TRADER-001"

    # Act
    result = msgspec_decoding_hook(obj_type, obj)

    # Assert
    assert result == ComponentId(obj)


def test_encoding_instrument_id() -> None:
    # Arrange
    obj = InstrumentId.from_str("AUD/USD.SIM")

    # Act
    result = msgspec_encoding_hook(obj)

    # Assert
    assert result == str(obj)


def test_decoding_instrument_id() -> None:
    # Arrange
    obj_type = InstrumentId
    obj = "AUD/USD.SIM"

    # Act
    result = msgspec_decoding_hook(obj_type, obj)

    # Assert
    assert result == InstrumentId.from_str(obj)


def test_encoding_bar_type() -> None:
    # Arrange
    obj = BarType.from_str("AUD/USD.SIM-100-TICK-MID-INTERNAL")

    # Act
    result = msgspec_encoding_hook(obj)

    # Assert
    assert result == str(obj)


def test_decoding_bar_type() -> None:
    # Arrange
    obj_type = BarType
    obj = "AUD/USD.SIM-100-TICK-MID-INTERNAL"

    # Act
    result = msgspec_decoding_hook(obj_type, obj)

    # Assert
    assert result == BarType.from_str(obj)


def test_encoding_price() -> None:
    # Arrange
    obj = Price.from_str("1.2345")

    # Act
    result = msgspec_encoding_hook(obj)

    # Assert
    assert result == str(obj)


def test_decoding_price() -> None:
    # Arrange
    obj_type = Price
    obj = "1.2345"

    # Act
    result = msgspec_decoding_hook(obj_type, obj)

    # Assert
    assert result == Price.from_str(obj)


def test_encoding_quatity() -> None:
    # Arrange
    obj = Quantity.from_str("100000")

    # Act
    result = msgspec_encoding_hook(obj)

    # Assert
    assert result == str(obj)


def test_decoding_quantity() -> None:
    # Arrange
    obj_type = Quantity
    obj = "100000"

    # Act
    result = msgspec_decoding_hook(obj_type, obj)

    # Assert
    assert result == Quantity.from_str(obj)


def test_encoding_timestamp() -> None:
    # Arrange
    obj = pd.Timestamp("2023-01-01")

    # Act
    result = msgspec_encoding_hook(obj)

    # Assert
    assert result == obj.isoformat()


def test_decoding_timestamp() -> None:
    # Arrange
    obj_type = pd.Timestamp
    obj = "2023-01-01T00:00:00"

    # Act
    result = msgspec_decoding_hook(obj_type, obj)

    # Assert
    assert result == pd.Timestamp(obj)


def test_encoding_timedelta() -> None:
    # Arrange
    obj = pd.Timedelta("1 HOUR")

    # Act
    result = msgspec_encoding_hook(obj)

    # Assert
    assert result == obj.isoformat()


def test_decoding_timedelta() -> None:
    # Arrange
    obj_type = pd.Timedelta
    obj = "P0DT1H0M0S"

    # Act
    result = msgspec_decoding_hook(obj_type, obj)

    # Assert
    assert result == pd.Timedelta(obj)


def test_encoding_unsupported_type() -> None:
    # Arrange
    unsupported_obj: list[int] = [1, 2, 3]

    # Act, Assert
    with pytest.raises(TypeError) as exinfo:
        msgspec_encoding_hook(unsupported_obj)

        # Verifying the exception message
        assert str(exinfo) == "Encoding objects of type <class 'list'> is unsupported"


def test_decoding_unsupported_type() -> None:
    # Arrange
    unsupported_type = list
    unsupported_obj = "[1, 2, 3]"

    # Act, Assert
    with pytest.raises(TypeError) as exinfo:
        msgspec_decoding_hook(unsupported_type, unsupported_obj)

        # Verifying the exception message
        assert str(exinfo) == "Decoding objects of type <class 'list'> is unsupported"
