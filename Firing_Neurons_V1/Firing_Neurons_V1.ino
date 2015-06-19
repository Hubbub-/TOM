#include <Adafruit_NeoPixel.h>

int timeDelay = 1000;
byte longStrip = 28;
byte shortStrip = 24;
byte stripLength[5] = {
  shortStrip, longStrip, longStrip, shortStrip, longStrip};
byte readIndex = 0;
byte writeIndex = 0;
int pulseBuffer = 30;

unsigned int integerValue=0;  // Max value is 65535
char incomingByte;
int input[7];

byte stripPixelArray [5][28][3];
int pulseArray[30][9];
//strip number, strip length, start time, position, direction(1 for in 0 for out), length, R, G, B

Adafruit_NeoPixel strip0 = Adafruit_NeoPixel(stripLength[0], 2, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip1 = Adafruit_NeoPixel(stripLength[1], 3, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip2 = Adafruit_NeoPixel(stripLength[2], 4, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip3 = Adafruit_NeoPixel(stripLength[3], 5, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip4 = Adafruit_NeoPixel(stripLength[4], 6, NEO_GRB + NEO_KHZ800);

void setup() {
  Serial.begin(9600);
  strip0.begin();
  strip1.begin();
  strip2.begin();
  strip3.begin();
  strip4.begin();

}

void loop() {
  if (Serial.available()>0) {   // something came across serial
    int dir = Serial.parseInt();
    int strip = Serial.parseInt();
    int col = Serial.parseInt();
    if (Serial.read() == '\n'){
      createPulse(dir,strip,col);
    }

  }
  
  
  //createPulses();
  //Serial.println(millis());
  updatePulses(pulseArray);
  updatePixels(pulseArray);
  drawPixels(stripPixelArray);
  memset(stripPixelArray, 0, sizeof(stripPixelArray)); 
} 

void createPulse(int direc, int stripnum, int col){
  int dir = direc;
  int stripNum = stripnum;
  int colour = col;
//  int dir, stripNum, colour;
//  Serial.println(data);
//  
//  
//  
//  dir = data/100;
//  data -= dir*100;
//  
//  stripNum = data/10;
//  colour = data - stripNum*10;
//  

  
  int R,G,B;
  
  if (colour == 0){
  R = 100;
  G = 0;
  B = 0;
  }
  if (colour == 1){
  R = 0;
  G = 100;
  B = 0;
  }
  if (colour == 2){
  R = 0;
  G = 0;
  B = 100;
  }
  if (colour == 3){
  R = 50;
  G = 50;
  B = 0;
  }
  if (colour == 4){
  R = 50;
  G = 0;
  B = 50;
  }
  if (colour == 5){
  R = 0;
  G = 50;
  B = 50;
  }
  if (colour == 6){
  R = 40;
  G = 40;
  B = 40;
  }
  if (colour == 7){
  R = 80;
  G = 20;
  B = 0;
  }
  if (colour == 8){
  R = 80;
  G = 0;
  B = 20;
  }
  if (colour == 9){
  R = 20;
  G = 0;
  B = 80;
  }

  int stripLen;

  switch (stripNum) {
  case 0:
    stripLen = stripLength[0];
    break;
  case 1:
    stripLen = stripLength[1];
    break;
  case 2:
    stripLen = stripLength[2];
    break;
  case 3:
    stripLen = stripLength[3];
    break;
  case 4:
    stripLen = stripLength[4];
    break;
  }

  int startTime = millis();
  int pos;
  int len = 7;
  
  switch (dir) {
  case 0:
    pos = 0;
    break;

  case 1:
    pos = stripLen - 1;
    break;
  }


  byte w;
  if (writeIndex >= 50) {
    w = writeIndex - 50;
  } 
  else {
    w = writeIndex;
  }

  pulseArray[w][0] = stripNum;
  pulseArray[w][1] = stripLen;
  pulseArray[w][2] = startTime;
  pulseArray[w][3] = pos;
  pulseArray[w][4] = dir;
  pulseArray[w][5] = len;
  pulseArray[w][6] = R;
  pulseArray[w][7] = G;
  pulseArray[w][8] = B;

  writeIndex ++;
}

void createPulses() {
  //strip number, start time, position, direction(1 for in 0 for out), length, R, G, B

  int num = random(100);
  if (num < 3) {
    
      int stripNum = int(random(0,5));
      int stripLen;

      switch (stripNum) {
      case 0:
        stripLen = stripLength[0];
        break;
      case 1:
        stripLen = stripLength[1];
        break;
      case 2:
        stripLen = stripLength[2];
        break;
      case 3:
        stripLen = stripLength[3];
        break;
      case 4:
        stripLen = stripLength[4];
        break;
      }

      int startTime = millis();
      int pos;
      int dir = int(random(0, 2));

      switch (dir) {
      case 0:
        pos = 0;
        break;
        pos = stripLen - 1;
      case 1:
        break;
      }

      int len = random(3, 10);
      int R = random(0, 250);
      int G = random(0, 250);
      int B = random(0, 250);

      byte w;
      if (writeIndex >= 50) {
        w = writeIndex - 50;
      } 
      else {
        w = writeIndex;
      }

      pulseArray[w][0] = stripNum;
      pulseArray[w][1] = stripLen;
      pulseArray[w][2] = startTime;
      pulseArray[w][3] = pos;
      pulseArray[w][4] = dir;
      pulseArray[w][5] = len;
      pulseArray[w][6] = R;
      pulseArray[w][7] = G;
      pulseArray[w][8] = B;

      writeIndex ++;
    }
  
}


void updatePulses(int theArray[][9]) {
  byte indexRemoveCount = 0;
  for (byte i = readIndex; i < writeIndex; i++) {
    int stripLen = theArray[i][1];
    int startTime = theArray[i][2];
    int timeSince = millis() - startTime;
    int pos = theArray[i][3];
    byte dir = theArray[i][4];
    switch (dir) {
    case 0:
      theArray[i][3] = map (timeSince, 0, timeDelay, 0, stripLen - 1);
      break;
    case 1:
      theArray[i][3] = map (timeSince, 0, timeDelay, stripLen - 1, 0);
    }
    if (pos > pulseBuffer || pos < -pulseBuffer) {
      readIndex ++;
      //Serial.println(readIndex);
    }
  }
}


void updatePixels(int theArray[][9]) {
  if (readIndex >= pulseBuffer) {
    readIndex = 0;
    writeIndex -= pulseBuffer;
  }
  for (byte i = readIndex; i < writeIndex; i++) {
    byte j;
    if (i >= pulseBuffer) {
      j = i - pulseBuffer;
    } 
    else {
      j = i;
    }
    byte stripNum = theArray[j][0];
    byte stripLen = theArray[j][1];
    byte pos = theArray[j][3];
    byte dir = theArray[j][4];
    byte len = theArray[j][5];
    byte R = theArray[j][6];
    byte G = theArray[j][7];
    byte B = theArray[j][8];

    switch (dir) {
    case 0:
      for (int p = pos; p > pos - len; p -- ) {
        float brightness = map(p, pos - len, pos, 0, 10) * 0.1;
        //Serial.println(brightness);
        if (p < stripLen && p >= 0) {
          stripPixelArray[stripNum][p][0] += int(R * brightness);
          stripPixelArray[stripNum][p][1] += int(G * brightness);
          stripPixelArray[stripNum][p][2] += int(B * brightness);
        }
      }
      break;
    case 1:
      for (int p = pos; p < pos + len; p ++ ) {
        float brightness = map(p, pos + len, pos, 0, 10) * 0.1;
        //Serial.println(brightness);
        if (p < stripLen && p >= 0) {
          stripPixelArray[stripNum][p][0] += int(R * brightness);
          stripPixelArray[stripNum][p][1] += int(G * brightness);
          stripPixelArray[stripNum][p][2] += int(B * brightness);
        }
      }
      break;
    }
  }
}

void drawPixels(byte theArray[][28][3]) {
  for (byte s = 0; s < 5; s++) {
    for (byte i = 0; i < stripLength[s]; i++) {
      byte r = theArray[s][i][0];
      byte g = theArray[s][i][1];
      byte b = theArray[s][i][2];

      switch (s) {
      case 0:
        strip0.setPixelColor(i, strip0.Color(r , g , b) ); // Draw pixel
        strip0.show();
        break;
      case 1:
        strip1.setPixelColor(i, strip1.Color(r , g , b) ); // Draw pixel
        strip1.show();
        break;
      case 2:
        strip2.setPixelColor(i, strip2.Color(r , g , b) ); // Draw pixel
        strip2.show();
        break;
      case 3:
        strip3.setPixelColor(i, strip3.Color(r , g , b) ); // Draw pixel
        strip3.show();
        break;
      case 4:
        strip4.setPixelColor(i, strip4.Color(r , g , b) ); // Draw pixel
        strip4.show();
        break;
      }
    }
  }
}


