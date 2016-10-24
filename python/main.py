# http://qiita.com/serinuntius/items/ce8183a283795d9fdb01#_reference-b16085e1ba9c4002dabe
# http://gamepro.blog.jp/python/pyaudio%E3%81%A7wav%E5%86%8D%E7%94%9F

import dlib
import cv2
import wave
import pyaudio
import threading
from time import sleep

CHUNK = 1024


class AudioPlayer(object):
    """ A Class For Playing Audio """

    def __init__(self, audio_file):
        self.audio_file = audio_file
        self.playing = threading.Event()    # 再生中フラグ

    def run(self):
        """ Play audio in a sub-thread """
        audio = pyaudio.PyAudio()
        input = wave.open(self.audio_file, "rb")
        output = audio.open(format=audio.get_format_from_width(input.getsampwidth()),
                            channels=input.getnchannels(),
                            rate=input.getframerate(),
                            output=True)

        while self.playing.is_set():
            data = input.readframes(CHUNK)
            if len(data) > 0:
                # play audio
                output.write(data)
            else:
                # end playing audio
                self.playing.clear()

        # stop and close the output stream
        output.stop_stream()
        output.close()
        # close the input file
        input.close()
        # close the PyAudio
        audio.terminate()

    def play(self):
        """ Play audio. """
        if not self.playing.is_set():
            self.playing.set()
            self.thread = threading.Thread(target=self.run)
            self.thread.start()

    def wait(self):
        if self.playing.is_set():
            self.thread.join()

    def stop(self):
        """ Stop playing audio and wait until the sub-thread terminates. """
        if self.playing.is_set():
            self.playing.clear()
            self.thread.join()




detector = dlib.get_frontal_face_detector()

cap = cv2.VideoCapture(1)


player1 = AudioPlayer("in/1.wav")
player2 = AudioPlayer("in/2.wav")

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    dets = detector(frame)

    for d in dets:
        cv2.rectangle(frame, (d.left(), d.top()), (d.right(), d.bottom()), (0, 0, 255), 2)
        print( d.left(), d.top(), d.right(), d.bottom(), d.right()-d.left(), d.bottom()-d.top() )

        if(d.right()-d.left() > 300):
            print("play 1")
            player1.play()
        if(d.right()-d.left() < 300):
            print("play 2")
            player2.play()





    # Display the resulting frame
    cv2.imshow("frame",frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if cv2.waitKey(1) & 0xFF == ord('s'):
        player2.stop()
        player1.stop()

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()



