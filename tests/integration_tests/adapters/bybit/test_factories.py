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


import asyncio

import pytest

from nautilus_trader.adapters.bybit.common.enums import BybitInstrumentType
from nautilus_trader.adapters.bybit.config import BybitDataClientConfig
from nautilus_trader.adapters.bybit.config import BybitExecClientConfig
from nautilus_trader.adapters.bybit.data import BybitDataClient
from nautilus_trader.adapters.bybit.execution import BybitExecutionClient
from nautilus_trader.adapters.bybit.factories import BybitLiveDataClientFactory
from nautilus_trader.adapters.bybit.factories import BybitLiveExecClientFactory
from nautilus_trader.adapters.bybit.factories import _get_http_base_url
from nautilus_trader.adapters.bybit.factories import _get_ws_base_url_public
from nautilus_trader.cache.cache import Cache
from nautilus_trader.common.clock import LiveClock
from nautilus_trader.common.component import MessageBus
from nautilus_trader.common.enums import LogLevel
from nautilus_trader.common.logging import Logger
from nautilus_trader.test_kit.mocks.cache_database import MockCacheDatabase
from nautilus_trader.test_kit.stubs.identifiers import TestIdStubs


class TestBybitFactories:
    def setup(self):
        self.loop = asyncio.get_event_loop()
        self.clock = LiveClock()
        self.logger = Logger(
            clock=self.clock,
            level_stdout=LogLevel.DEBUG,
            bypass=True,
        )

        self.trader_id = TestIdStubs.trader_id()
        self.strategy_id = TestIdStubs.strategy_id()
        self.account_id = TestIdStubs.account_id()

        self.msgbus = MessageBus(
            trader_id=self.trader_id,
            clock=self.clock,
            logger=self.logger,
        )

        self.cache_db = MockCacheDatabase(
            logger=self.logger,
        )

        self.cache = Cache(
            database=self.cache_db,
            logger=self.logger,
        )

    @pytest.mark.parametrize(
        ("is_testnet", "expected"),
        [
            [False, "https://api.bytick.com"],
            [True, "https://api-testnet.bybit.com"],
        ],
    )
    def test_get_http_base_url(self, is_testnet, expected):
        base_url = _get_http_base_url(is_testnet)
        assert base_url == expected

    @pytest.mark.parametrize(
        ("account_type", "is_testnet", "expected"),
        [
            [BybitInstrumentType.SPOT, False, "wss://stream.bybit.com/v5/public/spot"],
            [BybitInstrumentType.SPOT, True, "wss://stream-testnet.bybit.com/v5/public/spot"],
            [BybitInstrumentType.LINEAR, False, "wss://stream.bybit.com/v5/public/linear"],
            [BybitInstrumentType.LINEAR, True, "wss://stream-testnet.bybit.com/v5/public/linear"],
            [BybitInstrumentType.INVERSE, False, "wss://stream.bybit.com/v5/public/inverse"],
            [BybitInstrumentType.INVERSE, True, "wss://stream-testnet.bybit.com/v5/public/inverse"],
        ],
    )
    def test_get_ws_base_url(self, account_type, is_testnet, expected):
        base_url = _get_ws_base_url_public(account_type, is_testnet)
        assert base_url == expected

    def test_create_bybit_live_data_client(self, bybit_http_client):
        data_client = BybitLiveDataClientFactory.create(
            loop=self.loop,
            name="BYBIT",
            config=BybitDataClientConfig(
                api_key="SOME_BYBIT_API_KEY",
                api_secret="SOME_BYBIT_API_SECRET",
                instrument_types=[BybitInstrumentType.LINEAR],
            ),
            msgbus=self.msgbus,
            cache=self.cache,
            clock=self.clock,
            logger=self.logger,
        )
        assert isinstance(data_client, BybitDataClient)

    def test_create_bybit_live_exec_client(self, bybit_http_client):
        data_client = BybitLiveExecClientFactory.create(
            loop=self.loop,
            name="BYBIT",
            config=BybitExecClientConfig(
                api_key="SOME_BYBIT_API_KEY",
                api_secret="SOME_BYBIT_API_SECRET",
                instrument_types=[BybitInstrumentType.LINEAR],
            ),
            msgbus=self.msgbus,
            cache=self.cache,
            clock=self.clock,
            logger=self.logger,
        )
        assert isinstance(data_client, BybitExecutionClient)
