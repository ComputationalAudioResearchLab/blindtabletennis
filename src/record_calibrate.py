print("start")

import neuromorphic_drivers as nd
import datetime
import pathlib
import time
import numpy as np
import event_stream


nd.print_device_list()

# PRIMARY_SERIAL = "00050423"
# SECONDARY_SERIAL = "00050870"
SECONDARY_SERIAL = "00050423"
PRIMARY_SERIAL = "00050870"

secondary_device = nd.open(
    serial=SECONDARY_SERIAL,
    iterator_timeout=0.1,
    configuration=nd.prophesee_evk4.Configuration(
        nd.prophesee_evk4.Biases(
            diff_on=150,
            diff_off=120,
        ),
        clock=nd.prophesee_evk4.Clock.EXTERNAL,
    ),
)

print("First open")
time.sleep(1.0)  # wait to make sure that secondary is ready
primary_device = nd.open(
    iterator_timeout=0.1,
    serial=PRIMARY_SERIAL,
    configuration=nd.prophesee_evk4.Configuration(
        nd.prophesee_evk4.Biases(
            diff_on=150,
            diff_off=120,
        ),
        clock=nd.prophesee_evk4.Clock.INTERNAL_WITH_OUTPUT_ENABLED,
    ),
)

print("Second open")
devices = [primary_device, secondary_device]

dirname = pathlib.Path(__file__).resolve().parent 
name = (
    datetime.datetime.now(tz=datetime.timezone.utc)
    .isoformat()
    .replace("+00:00", "Z")
    .replace(":", "-")
)
outputs = [
    event_stream.Encoder(dirname /"calibration_images" / "primary_ball"/ f"{name}_{PRIMARY_SERIAL}_primary.es", "dvs", 1280, 720),
    event_stream.Encoder(dirname /"calibration_images"/ "secondary_ball"/f"{name}_{SECONDARY_SERIAL}_secondary.es","dvs", 1280, 720),
]
print("Starting loop to record")

last_ts = np.array([0 for _ in devices], dtype=np.uint64)

while True:
    index = np.argmin(last_ts)
    status, packet = devices[index].__next__()
    if status.ring is None:
        continue    
    delay = status.delay()
    if delay is not None:
        if packet is not None and "dvs_events" in packet:
            events = packet["dvs_events"]
            if len(events) > 0:
                # if events["t"][-1] >= 5000000:
                #     last_ts[index] = 2 ** 63 # set to arbitrary large int
                #     if np.all(last_ts == 2 ** 63):
                #         break
                # else:
                last_ts[index] = events["t"][-1]
                print(
                    f"{index}: {round(delay * 1e6)} µs, {last_ts=}, num events: {len(events)}"
                )
                outputs[index].write(events)
        else:
            print(
                f"{index}: no events, {round(delay * 1e6)} µs, {last_ts=}"
            )
