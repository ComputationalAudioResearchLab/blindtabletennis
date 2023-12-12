import numpy as np
import cv2


class VisualiseFrames:

    def __init__(self, frame_width, frame_height, output_path) -> None:
        self.height = frame_height
        self.width = frame_width
        print("frame size: {}h {}w".format(self.height, self.width))
        self.out_put = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(
            *'avc1'), 100, (frame_width, frame_height))

    '''
    Save single frame to the video 
    '''

    def write_event_frame(self, events, rectangles, ball):

        frame = np.ones((self.height, self.width, 3), dtype=np.uint8) * 50
        for event in events:
            if event[2]:
                frame[self.height - 1 - event[1]][event[0]] = 255
            else:
                frame[self.height - 1 - event[1]][event[0]] = 100
        for box in rectangles:
            cv2.rectangle(frame, (box[1][0], self.height - box[1][1]),
                          (box[0][0], self.height - box[0][1]), (0, 255, 0), 2)

        if ball is not None:
            cv2.circle(frame, (ball[0], self.height -
                       ball[1]), 10, (0, 0, 255))
            print(f"ball {ball}")
        else:
            cv2.putText(frame, "Ball Not Found", (20, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        self.out_put.write(frame)


    def save_video(self):
        self.out_put.release()

def visualise_single(events, height, width, ball):

    frame = np.ones((height, width, 3), dtype=np.uint8) * 50
    for event in events:
        if event[2]:
            frame[height - 1 - event[1]][event[0]] = 255
        else:
            frame[height - 1 - event[1]][event[0]] = 100
    
    # for box in clusters:
    #         bbox = np.min(box[0]), np.max(box[0]), np.min(box[1]), np.max(box[1])
    #         cv2.rectangle(frame, (bbox[0], height - bbox[2]),
    #                       (bbox[1], height - bbox[3]), (0, 255, 0), 2)

    if ball is not None:
        cv2.circle(frame, (ball[0], height - ball[1]), 10, (0, 0, 255))
        print(f"ball {ball}")
    else:
        cv2.putText(frame, "Ball Not Found", (20, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("boxes", frame)

    # Wait until a key is pressed and then close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def display_estimate_frame(height, width, events1, events2,  ball1, ball2, estimate):

        frame1 = np.ones((height, width, 3), dtype=np.uint8) * 50
        frame2 = np.ones((height, width, 3), dtype=np.uint8) * 50
        for event in events1:
            if event[2]:
                frame1[height - 1 - event[1]][event[0]] = 255
            else:
                frame1[height - 1 - event[1]][event[0]] = 100
        for event in events2:
            if event[2]:
                frame2[height - 1 - event[1]][event[0]] = 255
            else:
                frame2[height - 1 - event[1]][event[0]] = 100
        
        if ball1 is not None:
            cv2.circle(frame1, (ball1[0], height - ball1[1]), 10, (0, 0, 255))
            print(f"ball {ball1}")
        if ball2 is not None:
            cv2.circle(frame2, (ball2[0], height - ball2[1]), 10, (0, 0, 255))
            print(f"ball {ball2}")

        if estimate is not None:
            cv2.putText(frame1, "Ball Not Found", (20, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            cv2.putText(frame1, estimate, (20, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        img = np.concatenate((frame1, frame2), axis=1) 

        cv2.imshow("boxes", img)

        cv2.waitKey(5)
        cv2.destroyAllWindows()