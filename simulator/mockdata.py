import pyarrow as pa
from datetime import datetime

alternative_trips = [{"id":1,
    "arrival_times": [datetime.timestamp(datetime.fromisoformat("2026-02-02T06:54:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:06:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:13:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:21:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:25:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:32:00.000Z"))],
    "departure_times":[datetime.timestamp(datetime.fromisoformat("2026-02-02T06:54:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:06:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:13:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:21:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:25:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:32:00.000Z"))],
    'path': ["EUS","HRW","WFJ","HML","BKM","TRI"],
    'first_departure': datetime.timestamp(datetime.fromisoformat("2026-02-02T06:54:00.000Z"))
},
{"id":2,
    "arrival_times": [datetime.timestamp(datetime.fromisoformat("2026-02-02T06:56:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:04:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:20:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:24:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:25:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:27:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:31:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:38:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:57:00.000Z")) ],
    "departure_times":[datetime.timestamp(datetime.fromisoformat("2026-02-02T06:56:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:04:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:20:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:24:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:25:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:27:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:31:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:38:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:57:00.000Z")) ],
    'path': ["BLY","LBZ","BKM","HML","APS","KGL","WFJ","HRW","EUS"],
    'first_departure': datetime.timestamp(datetime.fromisoformat("2026-02-02T06:56:00.000Z"))
},
{"id":3,
    "arrival_times": [datetime.timestamp(datetime.fromisoformat("2026-02-02T05:34:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T05:49:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T05:52:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T05:55:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:02:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:12:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:16:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:20:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:28:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:29:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:34:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:52:00.000Z"))],
    "departure_times":[datetime.timestamp(datetime.fromisoformat("2026-02-02T05:34:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T05:49:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T05:52:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T05:55:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:02:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:12:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:16:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:20:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:28:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:29:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:34:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:52:00.000Z"))],
    'path': ["NMP","WOL","MKC","BLY","LBZ","TRI","BKM","HML","WFJ","BSH","HRW","EUS"],
    'first_departure': datetime.timestamp(datetime.fromisoformat("2026-02-02T05:34:00.000Z"))
},

{"id":4,
    "arrival_times": [datetime.timestamp(datetime.fromisoformat("2026-02-02T06:34:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:49:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:52:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:55:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:02:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:12:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:16:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:20:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:28:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:29:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:34:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:52:00.000Z"))],
    "departure_times": [datetime.timestamp(datetime.fromisoformat("2026-02-02T06:34:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:49:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:52:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T06:55:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:02:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:12:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:16:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:20:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:28:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:29:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:34:00.000Z")),datetime.timestamp(datetime.fromisoformat("2026-02-02T07:52:00.000Z"))],
    'path': ["NMP","WOL","MKC","BLY","LBZ","TRI","BKM","HML","WFJ","BSH","HRW","EUS"],
    'first_departure': datetime.timestamp(datetime.fromisoformat("2026-02-02T06:34:00.000Z"))
}
]
schema = pa.schema([
    ('id', pa.int64()),
    ('path', pa.list_(pa.string())),          
    ('distance', pa.float64()),               
    ('arrival_times', pa.list_(pa.timestamp("s"))), 
    ('departure_times', pa.list_(pa.timestamp("s"))),
    ('first_departure', pa.timestamp("s"))          
])
trips = pa.Table.from_pylist(alternative_trips, schema)
