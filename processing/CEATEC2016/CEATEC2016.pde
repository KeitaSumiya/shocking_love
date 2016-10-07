import gab.opencv.*;
import processing.video.*;
import java.awt.*;
import processing.serial.*;
import ddf.minim.*;
import ddf.minim.signals.*;

AudioPlayer player1;
AudioPlayer player2;
// The serial port:
Serial myPort;

//parametrs
String myCamera = ""; // "HD Pro Webcam C920 #3";
String mySound1 = "in/heart60.mp3";
String mySound2 = "in/heart120.mp3";
String COM_PORT="/dev/tty.usbmodem1412"; //  How to check your COM_PORT: ls /dev/tty.usbmodem*

//hardware definitions
//   -1.0        0            1.0
//0.87      4  3  2  1  0
//       10  9  8  7  6  5
//      17 16 15 14 13 12 11
//     25 24 23 22 21 20 19 18
//0.0 34 33 32 31 30 29 28 27 26
//     42 41 40 39 38 37 36 35
//      49 48 47 46 45 44 43
//       55 54 53 52 51 50
//-0.87      60 59 58 57 56

int ELECTRODE_NUM=61;
float[] Electrode_Pos_X ={
        0.5,  0.25,  0.0,  -0.25,  -0.5,
      0.625,  0.375,  0.125,  -0.125,  -0.375, -0.625,  
    0.75,  0.5,  0.25,  0.0,  -0.25,  -0.5,  -0.75,  
  0.875,  0.625,  0.375,  0.125,  -0.125,  -0.375,  -0.625,  -0.875,  
1.0,  0.75,  0.5,  0.25,  0.0,  -0.25,  -0.5,  -0.75,  -1.0,  
  0.875,  0.625,  0.375,  0.125,  -0.125,  -0.375, -0.625,  -0.875,  
    0.75,  0.5,  0.25,  0.0,  -0.25,  -0.5,  -0.75,  
      0.625,  0.375,  0.125,  -0.125,  -0.375,  -0.625,  
        0.5,  0.25,  0.0,  -0.25,  -0.5};

float[] Electrode_Pos_Y ={
        0.8660254 , 0.8660254 , 0.8660254 , 0.8660254 , 0.8660254 , 
      0.649519 , 0.649519 , 0.649519 , 0.649519 , 0.649519 , 0.649519 , 
    0.4330127 , 0.4330127 , 0.4330127 , 0.4330127 , 0.4330127 , 0.4330127 , 0.4330127 , 
  0.21650635 , 0.21650635 , 0.21650635 , 0.21650635 , 0.21650635 , 0.21650635 , 0.21650635 , 0.21650635 , 
0.0 , 0.0 , 0.0 , 0.0 , 0.0 , 0.0 , 0.0 , 0.0 , 0.0 , 
  -0.21650635 , -0.21650635 , -0.21650635 , -0.21650635 , -0.21650635 , -0.21650635 , -0.21650635 , -0.21650635 , 
    -0.4330127 , -0.4330127 , -0.4330127 , -0.4330127 , -0.4330127 , -0.4330127 , -0.4330127 , 
      -0.649519 , -0.649519 , -0.649519 , -0.649519 , -0.649519 , -0.649519 , 
        -0.8660254 , -0.8660254 , -0.8660254 , -0.8660254 , -0.8660254};

//software definitions
int PC_MBED_STIM_PATTERN=0xFF;
int PC_MBED_MEASURE_REQUEST=0xFE;
int MBED_PC_MEASURE_RESULT=0xFF;

// thresholds
int AREASIZE_THRESHOLD=5;
int IMPEDANCE_THRESHOLD=10;

//graphical attributes
//int WINDOW_SIZE_X=400;
//int WINDOW_SIZE_Y=400;
int ELECTRODE_SIZE=25;

int scrn_width;
int scrn_height;

float r,t=0;
float freq;
int stimulation_val;
float bpm;
float framerate;
float r_pin;
float amp;
float amp_old;
float prod;
float face_coe;
color statuscolor;
int timer=0;
int[] stimulation = new int[ELECTRODE_NUM];
int[] impedance = new int[ELECTRODE_NUM];
int[] prev_impedance = new int[ELECTRODE_NUM];
int[] impedance_offset = new int[ELECTRODE_NUM];
int  AreaSize;
float CoGX, CoGY, Sum;



// Impedance Distribution Measurement Function
int[] MeasureImpedanceDistribution(){
  int pin,rcv,stoptime;
  int[] imp=new int[ELECTRODE_NUM];
  
    myPort.write((byte)PC_MBED_MEASURE_REQUEST); 
    stoptime=millis()+10; //wait 10ms
    while(stoptime>millis());
    rcv = myPort.read();
    for(pin=0;pin<ELECTRODE_NUM;pin++){
      rcv=myPort.read(); 
      imp[pin]=rcv;
    }
    return imp;
}

 
Capture video;
OpenCV opencv;
 
Minim minim;
AudioOutput out;
SineWave sine;

void setup() {
  int pin;
  
  //with electro-shock-device only 1/3
//  myPort = new Serial(this, COM_PORT, 921600);

  //with electro-shock-device only 2/3
//  impedance_offset = MeasureImpedanceDistribution(); //measure once and use the data as offset.

  scrn_width = 1280;
  scrn_height = 960;  
  size(scrn_width, scrn_height);

  if(myCamera.length() == 0) {
    video = new Capture(this, scrn_width/2, scrn_height/2);
  } else {
    video = new Capture(this, scrn_width/2, scrn_height/2, myCamera);
  }
  opencv = new OpenCV(this, scrn_width/2, scrn_height/2);

  opencv.loadCascade(OpenCV.CASCADE_FRONTALFACE);   
 
  video.start();

  minim = new Minim(this);
  framerate = 20.0;

  player1 = minim.loadFile(mySound1);
  player2 = minim.loadFile(mySound2);

}
 
void draw() {
  scale(2);
  opencv.loadImage(video);
  image(video, 0, 0 );
 
  noFill();
  stroke(0, 255, 0);
  strokeWeight(3);
  Rectangle[] faces = opencv.detect();
  float bpmbase = 350.0; //この辺は正しいBPMとして作動しない. 要修正
 
  if (faces.length == 0){
    bpm = bpmbase;
    freq = bpm/60.0;
    
    player1.play();
    player2.pause(); player2.rewind();
  }
  if (faces.length > 0){
    for (int face = 0; face < faces.length; face++) {
      float face_val = float(faces[face].height)/float(scrn_height/2);
      if(face_val < 0.3){
        face_coe = 1;
        player1.play();
        player2.pause(); player2.rewind();
      }else{
        face_coe = 2;
        player2.play();
        player1.pause(); player1.rewind();
      }
      bpm = bpmbase*face_coe;
      freq = bpm/60.0;
      rect(faces[face].x, faces[face].y, faces[face].width, faces[face].height);
      
      //with electro-shock-device only 3/3
      //electro_shock(freq, t);
    }
  }

  t += 1.0/framerate;
}
 
 
void electro_shock(float freq, float t) {
  int i,pin;
  
  stimulation_val = 200;
  r = abs(sin(PI*freq*t));
  for(pin=0;pin<ELECTRODE_NUM;pin++){
    r_pin = sqrt(pow(Electrode_Pos_X[pin], 2) + pow(Electrode_Pos_Y[pin], 2));
    if(r_pin < r){
      stimulation[pin]=stimulation_val; //Pulse Width in micro-seconds. 
   }else{
      stimulation[pin]=0;
    }
  }

  //send stimulation signal to mbed
  myPort.write((byte)PC_MBED_STIM_PATTERN); 
  for(pin=0;pin<ELECTRODE_NUM;pin++){
    myPort.write((byte)stimulation[pin]); 
  }

  //Measure impedance and calculate center of gravity and contact area (every 2 times)
  AreaSize=0;
  CoGX=0;
  CoGY=0;
  Sum=0;
  impedance = MeasureImpedanceDistribution();
  
  for(pin=0;pin<ELECTRODE_NUM;pin++){
    if(impedance[pin]==-1){//avoid serial transmission error.  
      impedance[pin]=prev_impedance[pin];
    }else{//average previous data to avoid noise
      int tmp = (impedance[pin]+prev_impedance[pin])/2;
      prev_impedance[pin]=impedance[pin];
      impedance[pin]=tmp;
    }
  }
  for(pin=0;pin<ELECTRODE_NUM;pin++){
    impedance[pin] = impedance_offset[pin]-impedance[pin];
    if(impedance[pin]>IMPEDANCE_THRESHOLD){
      //impedance[pin]-=IMPEDANCE_THRESHOLD;
      AreaSize++;
      CoGX += Electrode_Pos_X[pin]*(float)impedance[pin];
      CoGY += Electrode_Pos_Y[pin]*(float)impedance[pin];
      Sum += (float)impedance[pin];
    }else if(impedance[pin]<0){
      impedance[pin]=0;
    }
  }
  if(AreaSize>AREASIZE_THRESHOLD){
    CoGX /= Sum;
    CoGY /= Sum;  
  }else{
    CoGX=0;
    CoGY=0;
  }

} 
 

void stop() {
  out.close();
  minim.stop();

  super.stop();
} 
 
void captureEvent(Capture c) {
  c.read();
}
