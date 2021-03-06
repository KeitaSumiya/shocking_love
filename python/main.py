import sys
import numpy as np
import tensorflow as tf
import dlib
import cv2

import wave
import pyaudio
import threading
from time import sleep

from osax import *

CHUNK = 1024
sa = OSAX()

class AudioPlayer(object):
    """ A Class For Playing Audio """

    def __init__(self, audio_file):
        self.audio_file = audio_file
        self.playing = threading.Event()

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


NUM_CLASSES = 2
IMAGE_SIZE = 28
IMAGE_PIXELS = IMAGE_SIZE*IMAGE_SIZE*3

def inference(images_placeholder, keep_prob):


    def weight_variable(shape):
      initial = tf.truncated_normal(shape, stddev=0.1)
      return tf.Variable(initial)

    def bias_variable(shape):
      initial = tf.constant(0.1, shape=shape)
      return tf.Variable(initial)

    def conv2d(x, W):
      return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

    def max_pool_2x2(x):
      return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                            strides=[1, 2, 2, 1], padding='SAME')
    
    x_image = tf.reshape(images_placeholder, [-1, 28, 28, 3])

    with tf.name_scope('conv1') as scope:
        W_conv1 = weight_variable([5, 5, 3, 32])
        b_conv1 = bias_variable([32])
        h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)

    with tf.name_scope('pool1') as scope:
        h_pool1 = max_pool_2x2(h_conv1)
    
    with tf.name_scope('conv2') as scope:
        W_conv2 = weight_variable([5, 5, 32, 64])
        b_conv2 = bias_variable([64])
        h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)

    with tf.name_scope('pool2') as scope:
        h_pool2 = max_pool_2x2(h_conv2)

    with tf.name_scope('fc1') as scope:
        W_fc1 = weight_variable([7*7*64, 1024])
        b_fc1 = bias_variable([1024])
        h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
        h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)
        h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

    with tf.name_scope('fc2') as scope:
        W_fc2 = weight_variable([1024, NUM_CLASSES])
        b_fc2 = bias_variable([NUM_CLASSES])

    with tf.name_scope('softmax') as scope:
        y_conv=tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

    return y_conv


detector = dlib.get_frontal_face_detector()

cap = cv2.VideoCapture(0)

player1 = AudioPlayer("in/heart120.wav")
player2 = AudioPlayer("in/heart60.wav")
#player1 = AudioPlayer("in/1.wav")
#player2 = AudioPlayer("in/2.wav")


images_placeholder = tf.placeholder("float", shape=(None, IMAGE_PIXELS))
labels_placeholder = tf.placeholder("float", shape=(None, NUM_CLASSES))
keep_prob = tf.placeholder("float")

logits = inference(images_placeholder, keep_prob)
sess = tf.InteractiveSession()

saver = tf.train.Saver()
sess.run(tf.initialize_all_variables())
saver.restore(sess, "in/model.ckpt")

count = 0
#isMe = 'other'
while(True):
    count = count + 1
    print(count)
    # Capture frame-by-frame
    #print("len", len(cap.read()))
    ret, frame = cap.read()
#    print("height", len(frame) )
#    print("width", len(frame[0]) )
    height = len(frame)

    if(ret):
        dets = detector(frame)

        isMe = 'other'
        if len(dets) != 0:
            for d in dets:
                if d.top() > 0 and d.left() > 0 and d.bottom() > 0 and d.right() > 0: 
                    cv2.rectangle(frame, (d.left(), d.top()), (d.right(), d.bottom()), (0, 0, 255), 2)
                    print( d.left(), d.top(), d.right(), d.bottom(), d.right()-d.left(), d.bottom()-d.top() )

                    img = frame[d.top():d.bottom(), d.left():d.right()]
                    img = cv2.resize(img, (28, 28))
                    #print( len(img[0]) )
                    test_image = np.asarray(img.flatten().astype(np.float32)/255.0)

                    pred = np.argmax(logits.eval(feed_dict={ 
                        images_placeholder: [test_image],
                        keep_prob: 1.0 })[0])
                    print( "prediction", pred )
                    if( pred == 0 ):
                        isMe = 'me'
                        cv2.rectangle(frame, (d.left(), d.top()), (d.right(), d.bottom()), (255, 0, 255), 4)

                if( isMe == 'me' ):
                    player2.stop()
                    print("play 1")
                    sa.set_volume(70)
                    if( d.bottom() - d.top() > 0.6*height ):
                        sa.set_volume(140)
                    player1.play()
                    sleep(1)
                elif( isMe == 'other' ):
                    player1.stop()
                    sa.set_volume(3)
                    player2.play()
                    sleep(1)
        else:
            player1.stop()
            sa.set_volume(3)
            player2.play()
            sleep(1)
        # Display the resulting frame
        cv2.imshow("frame",frame)

    else:
        player1.stop()
        sa.set_volume(3)
        player2.play()
        sleep(1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break



#        # Display the resulting frame
#        cv2.imshow("frame",frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
