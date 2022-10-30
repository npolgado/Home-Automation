import cv2
import tkinter as tk
import PIL.Image, PIL.ImageTk
import time

class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.vid = MyVideoCapture(self.video_source)

        self.canvas = tk.Canvas(window, width = self.vid.width, height = self.vid.height)
        self.canvas.pack()

        # Button that lets the user take a snapshot
        self.btn_snapshot=tk.Button(window, text="Snapshot", width=50, command=self.snapshot)
        self.btn_snapshot.pack(anchor=tk.CENTER, expand=True)

        # Button that lets the user start/stop the live webcam feed
        self.btn_stop = tk.Button(window, text="Start/Stop", width=50, command=self.stop_webcam)
        self.btn_stop.pack(anchor=tk.CENTER, expand=True)

        # Button that lets the user apply the color filter
        self.btn_color = tk.Button(window, text="Color Filter", width=50, command=self.apply_color_filter)
        self.btn_color.pack(anchor=tk.CENTER, expand=True)

        # Button that lets the user apply the gray filter
        self.btn_gray = tk.Button(window, text="Gray Filter", width=50, command=self.apply_gray_filter)
        self.btn_gray.pack(anchor=tk.CENTER, expand=True)

        # Button that lets the user apply the edge filter
        self.btn_edge = tk.Button(window, text="Edge Filter", width=50, command=self.apply_edge_filter)
        self.btn_edge.pack(anchor=tk.CENTER, expand=True)

        # Button that lets the user clear the current filter
        self.btn_clear = tk.Button(window, text="Clear Filter", width=50, command=self.clear_filter)
        self.btn_clear.pack(anchor=tk.CENTER, expand=True)

        self.delay = 15
        self.update()

        self.window.mainloop()


    def apply_color_filter(self):
        '''apply color filter'''
        self.vid.color_filter = True
        self.vid.gray_filter = False
        self.vid.edge_filter = False
        self.vid.clear_filter = False

    def apply_gray_filter(self):
        '''apply gray filter'''
        self.vid.color_filter = False
        self.vid.gray_filter = True
        self.vid.edge_filter = False
        self.vid.clear_filter = False

    def apply_edge_filter(self):
        '''apply edge filter'''
        self.vid.color_filter = False
        self.vid.gray_filter = False
        self.vid.edge_filter = True
        self.vid.clear_filter = False

    def clear_filter(self):
        '''clear filter'''
        self.vid.color_filter = False
        self.vid.gray_filter = False
        self.vid.edge_filter = False
        self.vid.clear_filter = True

    def snapshot(self):
        '''Take snapshot and save'''
        ret, frame = self.vid.get_frame()
        if ret:
            cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    def stop_webcam(self):
        '''stop webcam'''
        if self.vid.webcam_running:
            self.vid.webcam_running = False
        else:
            self.vid.webcam_running = True

    def update(self):
        ret, frame = self.vid.get_frame()
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)

        self.window.after(self.delay, self.update)


class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

        # color filter
        self.color_filter = False

        # gray filter
        self.gray_filter = False

        # edge filter
        self.edge_filter = False

        # clear filter
        self.clear_filter = False

        # webcam running
        self.webcam_running = True

    def get_frame(self):
        if self.vid.isOpened():
            if self.webcam_running:
                ret, frame = self.vid.read()
                frame = cv2.resize(frame, (600, 800))

                if ret:
                    # color filter
                    if self.color_filter:
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                        min_color = (100,100,100)
                        max_color = (120,255,255)
                        frame = cv2.inRange(frame, min_color, max_color)
                        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

                    # gray filter
                    if self.gray_filter:
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

                    # edge filter
                    if self.edge_filter:
                        frame = cv2.Canny(frame, threshold1 = 100, threshold2 = 200)
                        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

                    # clear filter
                    if self.clear_filter:
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    return (ret, frame)
                else:
                    return (ret, None)
            else:
                return (0, None)
        else:
            return (0, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

# Create a window and pass it to the Application object
App(tk.Tk(), "Tkinter and OpenCV")