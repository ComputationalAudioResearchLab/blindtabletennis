import event_stream
import os
import numpy as np

#packet size
#Sleep for same amount in outer call
DURATION_SIZE = 200000

class EventStreamReaderOffline:

    def __init__(self, filename) -> None:
        self.filename: os.PathLike = filename
        print(self.filename)
        assert(os.path.isfile(self.filename))
        
        self.eventDecoder:event_stream.Decoder = event_stream.Decoder(self.filename)
        print(f'{self.eventDecoder.type} events, {self.eventDecoder.width} x {self.eventDecoder.height} sensor')
        self.buffers = [] #np.array([], dtype=event_stream.dvs_dtype)
        self.end_t = None

    
    def get_chunk(self) -> np.ndarray:
        print("End: ", self.end_t)
            
        # flush out buffers
        if self.end_t is not None and len(self.buffers) > 0 and self.buffers[-1]["t"][-1] >= self.end_t:
            accumulated_events = np.concatenate(self.buffers)
            print("Buffer: ", accumulated_events["t"][0], accumulated_events["t"][-1])

            mask = accumulated_events["t"] < self.end_t
            not_mask = np.logical_not(mask)

            self.buffers = [accumulated_events[not_mask]]
            print(len(self.buffers[0]))
            self.end_t += DURATION_SIZE

     
            result = accumulated_events[mask]
            print("Number of events in result: ",len(result))
            return result 


        while True:
            try:
                chunk =  next(iter(self.eventDecoder))
                print("Chunk: ", chunk["t"][0], chunk["t"][-1])
                # return chunk
            except StopIteration:
                print("End of file")
                return None
            if self.end_t is None:
                # Streams usually dont start from timestamp 0 as has some elapsed time before recording
                self.end_t = chunk["t"][0] + DURATION_SIZE
            
            if chunk["t"][-1] < self.end_t:
                self.buffers.append(chunk)
            else:
                mask = chunk["t"] < self.end_t
                self.buffers.append(chunk[mask])
                result = np.concatenate(self.buffers) #return to rest of pipeline

                not_mask = np.logical_not(mask)
                self.buffers = [chunk[not_mask]]
                self.end_t += DURATION_SIZE

                return result
             

        
    def get_height(self):
        return self.eventDecoder.height
    def get_width(self):
        return self.eventDecoder.width

