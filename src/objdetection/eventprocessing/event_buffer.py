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
        """
        Retrieve a chunk of data from the device stream.

        This method retrieves data packets from the device and processes them to form a chunk
        of events within a specified time range. 
        
        If the end time of the events in the current packet is less than the specified end time, the events are appended to a buffer, and
        Otherwise, the events are processed, and a chunk is returned.

        Returns:
            np.ndarray: Events of fromat [('t', '<u8'), ('x', '<u2'), ('y', '<u2'), ('on', '?')]
        """
        
        while True:
            status, packet = self.device.__next__()

            if self.end_t is None:
                # Streams usually dont start from timestamp 0 as has some elapsed time before recording
                self.end_t = packet["t"][0] + DURATION_SIZE

            if packet["t"][0] > self.end_t:
                # If the first event in the packet have timestamp greater than the specified end time,
                # processing has fallen behind. 
                # Current solution is just to skip time duration to catch up but should handle better
                self.end_t += DURATION_SIZE

            elif packet["t"][-1] < self.end_t:
                self.buffers.append(packet)
                # Append current packet to buffer and recursively call
            else:
                mask = packet["dvs_events"]["t"] < self.end_t
                self.buffers.append(packet["dvs_events"][mask])
                result = np.concatenate(self.buffers) #return to rest of pipeline
                not_mask = np.logical_not(mask)
                self.buffers = [packet[not_mask]]
                self.end_t += DURATION_SIZE
            
                return result
