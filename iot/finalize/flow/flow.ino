#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>


int X;
int Y;
float TIME = 0;
float FREQUENCY = 0;
float WATER = 0;
float TOTAL = 0;
float LS = 0;
const int input = A0;
void setup()
{
  delay(2000);
  pinMode(input,INPUT);
  Serial.begin(115200);


  WiFi.begin("Mysha", "Tanjim2003");

  while (WiFi.status() != WL_CONNECTED) {

    delay(1000);
    Serial.println("Connecting..");

  }
  Serial.println("Connected to WiFi Network");
}
void loop()
{
  X = pulseIn(input, HIGH);
  Y = pulseIn(input, LOW);
  TIME = X + Y;
  FREQUENCY = 1000000/TIME;
  WATER = FREQUENCY/7.5;
  LS = ((WATER/60) * 10);
  if(FREQUENCY >= 0)
  {
    if(isinf(FREQUENCY))
    {
      //off
    }
  else
    {
      //TOTAL = TOTAL + LS;
      if (WiFi.status() == WL_CONNECTED) 
      {
        String idc = String(LS);
        String link = "http://192.168.0.107:5000/send_data/flow/tanjim/";
        String hit = link + idc;
        HTTPClient http;  //Declare an object of class HTTPClient
        http.begin("http://192.168.1.88:8090/helloesp"); //Specify request destination
        int httpCode = http.GET(); //Send the request
        if (httpCode > 0) 
          {
            String payload = http.getString();   //Get the request response payload
            Serial.println(payload);             //Print the response payload
           }else Serial.println("An error ocurred");
         http.end();   //Close connection
      }  
    }
  }
  delay(10000);
}
