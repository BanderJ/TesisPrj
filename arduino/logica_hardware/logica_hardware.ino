#include <Servo.h>

// === PINES ===
#define MOTOR_IN1    5
#define MOTOR_IN2    6
#define TRIG_PIN     7
#define ECHO_PIN     8
#define SERVO_PIN    9

// === AJUSTES ===
const float DISTANCIA_UMBRAL       = 5.30;   // cm — verificación de tapa
const int   VELOCIDAD              = 220;    // velocidad faja (0-255)
const int   ANGULO_BUENO           = 0;      // servo: posición reposo — granos buenos/verdes
const int   ANGULO_DEFECTO         = 15;     // servo: separador — granos defectuosos
const unsigned long MS_DISTANCIA   = 100;    // reporte sensor cada 100 ms

Servo  servoSeparador;
bool   motorActivo = false;

// Temporizadores millis()
unsigned long tDistancia = 0;

// Buffer para leer líneas serial sin bloquear
String lineaSerial = "";

void setup() {
  Serial.begin(9600);  // clones con resonador cerámico fallan a 115200

  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MOTOR_IN2, OUTPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  servoSeparador.attach(SERVO_PIN);
  servoSeparador.write(ANGULO_BUENO);

  Serial.println("SISTEMA:LISTO");
}

void loop() {
  unsigned long ahora = millis();

  // 1. Leer comandos del backend (no-bloqueante, carácter a carácter)
  while (Serial.available() > 0) {
    char c = (char)Serial.read();
    if (c == '\n') {
      lineaSerial.trim();
      if (lineaSerial.length() > 0) procesarComando(lineaSerial);
      lineaSerial = "";
    } else {
      lineaSerial += c;
    }
  }

  // 2. Control de motor
  if (motorActivo) {
    analogWrite(MOTOR_IN1, VELOCIDAD);
    analogWrite(MOTOR_IN2, 0);
  } else {
    analogWrite(MOTOR_IN1, 0);
    analogWrite(MOTOR_IN2, 0);
  }

  // 3. Reporte de distancia
  if (ahora - tDistancia >= MS_DISTANCIA) {
    tDistancia = ahora;
    float dist = leerUltrasonico();
    if (dist > 0 && dist < DISTANCIA_UMBRAL) {
      Serial.print("LISTO:");
      Serial.println(dist, 2);
    } else {
      Serial.print("NO_LISTO:");
      Serial.println(dist, 2);
    }
  }

}

void procesarComando(String cmd) {
  if (cmd == "ON") {
    motorActivo = true;

  } else if (cmd == "OFF") {
    motorActivo = false;
    servoSeparador.write(ANGULO_BUENO);

  } else if (cmd == "SERVO:BUENO") {
    servoSeparador.write(ANGULO_BUENO);

  } else if (cmd == "SERVO:DEFECTO") {
    servoSeparador.write(ANGULO_DEFECTO);

  }
  // TARE y SCALE deshabilitados — báscula HX711 retirada temporalmente
}

// Retorna distancia en cm. Retorna -1.0 si no hay eco.
float leerUltrasonico() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long dur = pulseIn(ECHO_PIN, HIGH, 30000);
  if (dur == 0) return -1.0;
  return dur * 0.0343 / 2.0;
}
