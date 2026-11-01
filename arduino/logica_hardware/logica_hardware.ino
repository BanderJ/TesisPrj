#include <Servo.h>

// === PINES ===
// Motor de la faja: JGY370 12V 10 RPM (reductor sinfín autobloqueante)
// con driver L298N, canal A. Retirar el jumper de ENA del módulo.
#define MOTOR_ENA    5   // PWM — velocidad
#define MOTOR_IN1    4   // sentido
#define MOTOR_IN2    3   // sentido
#define TRIG_PIN     7   // morado
#define ECHO_PIN     8   // gris
#define SERVO_PIN    9   // naranja

// === AJUSTES ===
const float DISTANCIA_UMBRAL       = 5.30;   // cm — verificación de tapa
const int   VELOCIDAD              = 90;    // velocidad faja (0-255; 255 = máxima).
const int   SENTIDO                = -1;     // giro de la faja: 1 = IN1 alto, -1 = IN2 alto (validado en test_motor_2)
const int   ANGULO_BUENO           = 0;      // servo: posición reposo — granos buenos/verdes
const int   ANGULO_DEFECTO         = 15;     // servo: separador — granos defectuosos
const unsigned long MS_DISTANCIA   = 100;    // reporte sensor cada 100 ms

Servo  servoSeparador;

// Temporizadores millis()
unsigned long tDistancia = 0;

// Buffer para leer líneas serial sin bloquear
String lineaSerial = "";

void setup() {
  Serial.begin(9600);  // clones con resonador cerámico fallan a 115200

  pinMode(MOTOR_ENA, OUTPUT);
  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MOTOR_IN2, OUTPUT);
  aplicarMotor(false);
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

  // 2. Reporte de distancia
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
    aplicarMotor(true);

  } else if (cmd == "OFF") {
    aplicarMotor(false);
    servoSeparador.write(ANGULO_BUENO);

  } else if (cmd == "SERVO:BUENO") {
    servoSeparador.write(ANGULO_BUENO);

  } else if (cmd == "SERVO:DEFECTO") {
    servoSeparador.write(ANGULO_DEFECTO);

  }
  // TARE y SCALE deshabilitados — báscula HX711 retirada temporalmente
}

// L298N: velocidad por ENA (PWM), sentido por IN1/IN2. Al parar, el reductor
// sinfín retiene la faja; no hace falta freno activo.
void aplicarMotor(bool encender) {
  if (!encender) {
    analogWrite(MOTOR_ENA, 0);
    digitalWrite(MOTOR_IN1, LOW);
    digitalWrite(MOTOR_IN2, LOW);
    return;
  }
  digitalWrite(MOTOR_IN1, SENTIDO == 1 ? HIGH : LOW);
  digitalWrite(MOTOR_IN2, SENTIDO == 1 ? LOW : HIGH);
  analogWrite(MOTOR_ENA, VELOCIDAD);
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
