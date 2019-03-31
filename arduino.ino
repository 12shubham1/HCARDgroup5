//using HID library of arduino
#include <Mouse.h>
//Defining initials value, max/minreading taken from testing
int anglePin = 2;
float maxreading=1023;
float minreading=0;
float center;
int i=0;
void setup()
{
  //measuring the first value of potentiometer as center point for calibration purpose
Serial.begin(9600);
Mouse.begin();
float multValue = ((maxreading-minreading)/180);
float input = analogRead(anglePin);
float angleReading = (input - minreading) / multValue;
center=angleReading;
}
void loop()
{
  //reading the current angle of potentiometer
float multValue = ((maxreading-minreading)/180);
float input = analogRead(anglePin);

float angleReading = (input - minreading) / multValue;

Serial.println(center);
Serial.println(angleReading);

//deciding the mouse/controller direction and speed according to the potentiometer/angle values
if (angleReading>center+0.5 && angleReading<center+1)
{Mouse.move(-3,0,0);
delay(8);}
if (angleReading>center+1)
{Mouse.move(-3,0,0);
delay(3);}
else if (angleReading<center-0.5 && angleReading>center-1)
{Mouse.move(3,0,0);
delay(8);}
else if (angleReading<center-1)
{Mouse.move(3,0,0);
delay(3);}
else
{Mouse.move(0,0,0);
delay(1);}
}
