import numpy as np
import neuromorphic_drivers as nd


#packet size
DURATION_SIZE = 100000
class EventBuffer:
    def __init__(self, device):
        self.device = device
        self.buffers = [] #np.array([], dtype=event_stream.dvs_dtype)
        self.end_t = DURATION_SIZE

    def get_chunk(self) -> np.ndarray:
        status, packet = self.device.__next__()
        if packet["t"][-1] < self.end_t:
            self.buffers.append(packet)
            return None
        else:
            mask = packet["dvs_events"]["t"] < self.end_t
            self.buffers.append(packet["dvs_events"][mask])
            result = np.concatenate(self.buffers) #return to rest of pipeline
            not_mask = np.logical_not(mask)
            self.buffers = [packet[not_mask]]
            self.end_t += DURATION_SIZE
        
            return result
