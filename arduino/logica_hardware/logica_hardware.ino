#include <Servo.h>

// === PINES ===
#define MOTOR_IN1  5
#define MOTOR_IN2  6
#define TRIG_PIN   7
#define ECHO_PIN   8
#define SERVO_PIN  9

// === AJUSTES ===
const float DISTANCIA_UMBRAL = 20.0;  // cm — verificación de tapa
const int   VELOCIDAD        = 220;   // velocidad faja (0-255)
const int   ANGULO_BUENO     = 150;   // grano sin defecto
const int   ANGULO_DEFECTO   = 30;    // grano con defecto

Servo servoSeparador;
bool  motorActivo = false;

void setup() {
  Serial.begin(9600);

  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MOTOR_IN2, OUTPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  servoSeparador.attach(SERVO_PIN);
  servoSeparador.write(ANGULO_BUENO);  // posición default: canal bueno
}

void loop() {
  // Leer comando del backend si hay datos disponibles
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "ON") {
      motorActivo = true;

    } else if (cmd == "OFF") {
      motorActivo = false;
      servoSeparador.write(ANGULO_BUENO);  // reset servo al detener

    } else if (cmd == "SERVO:BUENO") {
      servoSeparador.write(ANGULO_BUENO);

    } else if (cmd == "SERVO:DEFECTO") {
      servoSeparador.write(ANGULO_DEFECTO);
    }
  }

  // Control de motor
  if (motorActivo) {
    analogWrite(MOTOR_IN1, VELOCIDAD);
    analogWrite(MOTOR_IN2, 0);
  } else {
    analogWrite(MOTOR_IN1, 0);
    analogWrite(MOTOR_IN2, 0);
  }

  // Reportar distancia (verificación de tapa en pantalla de registro)
  float distancia  = leerUltrasonico();
  bool  tapaCerrada = (distancia > 0 && distancia < DISTANCIA_UMBRAL);

  if (tapaCerrada) {
    Serial.print("LISTO:");
    Serial.println(distancia, 2);
  } else {
    Serial.print("NO_LISTO:");
    Serial.println(distancia, 2);
  }

  delay(100);
}

// Retorna -1.0 si no hay eco (sin objeto o fuera de rango).
float leerUltrasonico() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duracion = pulseIn(ECHO_PIN, HIGH, 30000);
  if (duracion == 0) return -1.0;
  return duracion * 0.0343 / 2.0;
}
