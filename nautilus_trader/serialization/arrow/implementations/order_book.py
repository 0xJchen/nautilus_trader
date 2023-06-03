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

import itertools
from itertools import repeat
from typing import Union

from nautilus_trader.model.data import BookOrder
from nautilus_trader.model.data import OrderBookDelta
from nautilus_trader.model.data import OrderBookDeltas
from nautilus_trader.model.data import OrderBookSnapshot
from nautilus_trader.model.enums import BookAction
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.serialization.arrow.serializer import register_parquet


def _parse_delta(delta: OrderBookDelta, cls):
    return dict(**OrderBookDelta.to_dict(delta), _type=cls.__name__)


def serialize(data: Union[OrderBookDelta, OrderBookDeltas, OrderBookSnapshot]):
    if isinstance(data, OrderBookDelta):
        result = [_parse_delta(delta=data, cls=OrderBookDelta)]
    elif isinstance(data, OrderBookDeltas):
        result = [_parse_delta(delta=delta, cls=OrderBookDeltas) for delta in data.deltas]
    elif isinstance(data, OrderBookSnapshot):
        # For a snapshot, we store the individual deltas required to rebuild, namely a CLEAR, followed by ADDs
        result = [
            _parse_delta(
                OrderBookDelta(
                    instrument_id=data.instrument_id,
                    order=None,
                    action=BookAction.CLEAR,
                    ts_event=data.ts_event,
                    ts_init=data.ts_init,
                ),
                cls=OrderBookSnapshot,
            ),
        ]
        orders = list(zip(repeat(OrderSide.BUY), data.bids)) + list(
            zip(repeat(OrderSide.SELL), data.asks),
        )
        result.extend(
            [
                _parse_delta(
                    OrderBookDelta(
                        instrument_id=data.instrument_id,
                        ts_event=data.ts_event,
                        ts_init=data.ts_init,
                        order=BookOrder(price=price, size=volume, side=side),
                        action=BookAction.ADD,
                    ),
                    cls=OrderBookSnapshot,
                )
                for side, (price, volume) in orders
            ],
        )
    else:  # pragma: no cover (design-time error)
        raise TypeError(f"invalid order book data, was {type(data)}")
    # Add a "last" message to let downstream consumers know the end of this group of messages
    if result:
        result[-1]["_last"] = True
    return result


def _is_orderbook_snapshot(values: list):
    return values[0]["_type"] == "OrderBookSnapshot"


def _build_order_book_snapshot(values):
    # First value is a CLEAR message, which we ignore
    assert len({v["instrument_id"] for v in values}) == 1
    assert len(values) >= 2, f"Not enough values passed! {values}"
    return OrderBookSnapshot(
        instrument_id=InstrumentId.from_str(values[1]["instrument_id"]),
        bids=[(order["price"], order["size"]) for order in values[1:] if order["side"] == "BUY"],
        asks=[(order["price"], order["size"]) for order in values[1:] if order["side"] == "SELL"],
        ts_event=values[1]["ts_event"],
        ts_init=values[1]["ts_init"],
    )


def _build_order_book_deltas(values):
    return OrderBookDeltas(
        instrument_id=InstrumentId.from_str(values[0]["instrument_id"]),
        deltas=[OrderBookDelta.from_dict(v) for v in values],
        ts_event=values[0]["ts_event"],
        ts_init=values[0]["ts_init"],
    )


def _sort_func(x):
    return x["instrument_id"], x["ts_event"]


def deserialize(data: list[dict]):
    assert not {d["side"] for d in data}.difference((None, "BUY", "SELL")), "Wrong sides"
    results = []
    for _, chunk in itertools.groupby(sorted(data, key=_sort_func), key=_sort_func):
        chunk = list(chunk)  # type: ignore
        if _is_orderbook_snapshot(values=chunk):  # type: ignore
            results.append(_build_order_book_snapshot(values=chunk))
        elif len(chunk) >= 1:  # type: ignore
            results.append(_build_order_book_deltas(values=chunk))
    return sorted(results, key=lambda x: x.ts_event)


for cls in [OrderBookDelta, OrderBookDeltas, OrderBookSnapshot]:
    register_parquet(
        cls=cls,
        serializer=serialize,
        deserializer=deserialize,
        table=OrderBookDelta,
        chunk=True,
    )
