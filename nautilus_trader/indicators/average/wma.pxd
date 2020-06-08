# -------------------------------------------------------------------------------------------------
#  Copyright (C) 2015-2020 Nautech Systems Pty Ltd. All rights reserved.
#  The use of this source code is governed by the license as found in the LICENSE file.
#  https://nautechsystems.io
# -------------------------------------------------------------------------------------------------

from nautilus_trader.indicators.average.moving_average cimport MovingAverage


cdef class WeightedMovingAverage(MovingAverage):
    cdef object _inputs

    cdef readonly object weights

    cpdef void update(self, double point)
    cpdef void reset(self)
