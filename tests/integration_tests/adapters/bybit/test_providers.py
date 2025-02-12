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


import pkgutil

import pytest

from nautilus_trader.adapters.bybit.common.enums import BybitInstrumentType
from nautilus_trader.adapters.bybit.http.client import BybitHttpClient
from nautilus_trader.adapters.bybit.provider import BybitInstrumentProvider
from nautilus_trader.common.clock import LiveClock
from nautilus_trader.common.logging import Logger
from nautilus_trader.config import InstrumentProviderConfig
from nautilus_trader.core.nautilus_pyo3 import HttpClient
from nautilus_trader.core.nautilus_pyo3 import HttpResponse
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.identifiers import Symbol
from nautilus_trader.model.identifiers import Venue


class TestBybitInstrumentProvider:
    def setup(self):
        self.clock = LiveClock()
        self.live_logger = Logger(clock=self.clock)
        self.http_client: BybitHttpClient = BybitHttpClient(
            clock=self.clock,
            logger=self.live_logger,
            api_key="BYBIT_API_KEY",
            api_secret="BYBIT_API_SECRET",
            base_url="https://api-testnet.bybit.com",
        )
        self.provider = self.get_target_instrument_provider(
            [
                BybitInstrumentType.SPOT,
                BybitInstrumentType.LINEAR,
                BybitInstrumentType.OPTION,
            ],
        )

    def get_target_instrument_provider(
        self,
        instrument_types: list[BybitInstrumentType],
    ) -> BybitInstrumentProvider:
        return BybitInstrumentProvider(
            client=self.http_client,
            logger=self.live_logger,
            clock=self.clock,
            instrument_types=instrument_types,
            config=InstrumentProviderConfig(load_all=True),
        )

    @pytest.mark.asyncio
    async def test_load_ids_async_incorrect_venue_raise_exception(self):
        provider = self.get_target_instrument_provider(BybitInstrumentType.SPOT)
        binance_instrument_ethusdt = InstrumentId(Symbol("BTCUSDT"), Venue("BINANCE"))
        with pytest.raises(ValueError):
            await provider.load_ids_async(
                instrument_ids=[binance_instrument_ethusdt],
            )

    # @pytest.mark.asyncio
    # async def test_load_ids(
    #     self,
    #     monkeypatch,
    # ):
    #     response = pkgutil.get_data(
    #         "tests.integration_tests.adapters.bybit.resources.http_responses.linear",
    #         "instrument_btc_usdt.json",
    #     )
    #     monkeypatch.setattr(HttpClient, "request", get_mock(response))
    #     instrument_ids: list[InstrumentId] = [
    #         InstrumentId.from_str("BTCUSDT-LINEAR.BYBIT"),
    #     ]
    #     await self.provider.load_ids_async(instrument_ids)
    #     instruments = self.provider.get_all()
    #     instruments_ids = list(instruments.keys())
    #     assert len(instruments_ids) == 1
    #     assert str(instruments_ids[0]) == "BTCUSDT-LINEAR.BYBIT"

    # @pytest.mark.asyncio()
    # async def test_spot_load_all_async(
    #     self,
    #     monkeypatch,
    # ):
    #     instrument_provider = self.get_target_instrument_provider([BybitInstrumentType.SPOT] )
    #     instrument_response = pkgutil.get_data(
    #         "tests.integration_tests.adapters.bybit.resources.http_responses.spot",
    #         "instruments.json",
    #     )
    #     fee_response = pkgutil.get_data(
    #         "tests.integration_tests.adapters.bybit.resources.http_responses",
    #         "fee_rate.json",
    #     )
    #     async def mock_requests(*args):
    #         url = args[2]
    #         if "fee-rate" in url:
    #             return HttpResponse(status=200, body=fee_response)
    #         else:
    #             return HttpResponse(status=200, body=instrument_response)
    #     monkeypatch.setattr(HttpClient, "request", mock_requests)
    #     await instrument_provider.load_all_async()
    #     instruments = instrument_provider.get_all()
    #     instruments_ids = list(instruments.keys())
    #     assert len(instruments_ids) == 2
    #     assert str(instruments_ids[0]) == "BTCUSDT-SPOT.BYBIT"
    #     assert str(instruments_ids[1]) == "ETHUSDT-SPOT.BYBIT"

    @pytest.mark.asyncio()
    async def test_linear_load_all_async(self, monkeypatch):
        instrument_provider = self.get_target_instrument_provider([BybitInstrumentType.LINEAR])
        instrument_response = pkgutil.get_data(
            "tests.integration_tests.adapters.bybit.resources.http_responses.linear",
            "instruments.json",
        )
        fee_response = pkgutil.get_data(
            "tests.integration_tests.adapters.bybit.resources.http_responses",
            "fee_rate.json",
        )

        async def mock_requests(*args):
            url = args[2]
            if "fee-rate" in url:
                return HttpResponse(status=200, body=fee_response)
            else:
                return HttpResponse(status=200, body=instrument_response)

        monkeypatch.setattr(HttpClient, "request", mock_requests)
        await instrument_provider.load_all_async()
        instruments = instrument_provider.get_all()
        instruments_ids = list(instruments.keys())
        assert len(instruments_ids) == 2
        assert str(instruments_ids[0]) == "BTCUSDT-LINEAR.BYBIT"
        assert str(instruments_ids[1]) == "ETHUSDT-LINEAR.BYBIT"

    # @pytest.mark.asyncio()
    # async def test_options_load_all_async(self, monkeypatch):
    #     instrument_provider = self.get_target_instrument_provider([BybitInstrumentType.OPTION])
    #     response = pkgutil.get_data(
    #         "tests.integration_tests.adapters.bybit.resources.http_responses.option",
    #         "instruments.json",
    #     )
    #     monkeypatch.setattr(HttpClient, "request", get_mock(response))
    #     await instrument_provider.load_all_async()
    #     instruments = instrument_provider.get_all()
    #     instruments_ids = list(instruments.keys())
    #     assert len(instruments_ids) == 2
    #     assert str(instruments_ids[0]) == "BTCUSDT-OPTION.BYBIT"
    #     assert str(instruments_ids[1]) == "ETHUSDT-OPTION.BYBIT"
