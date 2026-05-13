// === LIBRERÍAS ===
#include <Servo.h>
#include <HX711.h>

// === PINES MOTOR (MX1508) ===
#define MOTOR_IN1 5   // PWM ~5
#define MOTOR_IN2 6   // PWM ~6

// === PINES SERVO ===
#define SERVO_PIN 9   // PWM ~9

// === PINES HC-SR04 ===
#define TRIG_PIN  7
#define ECHO_PIN  8

// === PINES HX711 ===
#define HX711_DT  A1
#define HX711_SCK A0

// ================================================================
// VARIABLES GLOBALES
// ================================================================

Servo  miServo;
HX711  balanza;

int velocidad   = 200;  // 0–255
int anguloServo = 90;   // 0–180 grados

// HC-SR04 — lectura cada 200 ms
const unsigned long INTERVALO_SENSOR   = 200;
unsigned long tiempoUltimaLectura      = 0;
float distanciaCm                      = 999.0;
const float DISTANCIA_LIMITE           = 30.0;
const float DISTANCIA_TRIGGER          = 20.0;  // objeto detectado → arrancar motor
bool  motorActivo                      = false;

// HX711 — lectura cada 500 ms
const unsigned long INTERVALO_BALANZA  = 500;
unsigned long tiempoUltimaBalanza      = 0;
float pesoGramos                       = 0.0;

// Factor de calibración — ajustar con comando CAL:<valor>
// Para calibrar: poner peso conocido, enviar "CAL:<peso_conocido / lectura_raw>"
float factorCalibracion = 420.0;  // Valor inicial aproximado — DEBE calibrarse

// ================================================================
// PROMEDIO MOVIL PARA PESO
// ================================================================
#define MUESTRAS_MOVIL  8
float bufferPeso[MUESTRAS_MOVIL] = {0};
int   indicePeso                 = 0;
bool  bufferLleno                = false;

float actualizarPromedio(float nuevaLectura) {
  bufferPeso[indicePeso] = nuevaLectura;
  indicePeso = (indicePeso + 1) % MUESTRAS_MOVIL;
  if (indicePeso == 0) bufferLleno = true;

  int n = bufferLleno ? MUESTRAS_MOVIL : indicePeso;
  float suma = 0.0;
  for (int i = 0; i < n; i++) suma += bufferPeso[i];
  return suma / n;
}

// ================================================================
// SETUP
// ================================================================
void setup() {
  Serial.begin(9600);
  Serial.println("=== Sistema iniciado ===");
  Serial.println("Comandos:");
  Serial.println("  A              -> Motor adelante");
  Serial.println("  R              -> Motor reversa");
  Serial.println("  S              -> Motor stop");
  Serial.println("  V:<0-255>      -> Velocidad (ej: V:180)");
  Serial.println("  G:<0-180>      -> Giro servo (ej: G:90)");
  Serial.println("  D              -> Leer distancia ahora");
  Serial.println("  W              -> Leer peso ahora");
  Serial.println("  PF             -> Peso Final (20 muestras, salida JSON)");
  Serial.println("  TARA           -> Poner peso en cero");
  Serial.println("  CAL:<factor>   -> Ajustar factor calibracion");
  Serial.println("[Motor bloqueado si distancia > 30 cm]");

  // Motor
  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MOTOR_IN2, OUTPUT);

  // Sensor ultrasonico
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Servo
  miServo.attach(SERVO_PIN);
  miServo.write(anguloServo);

  // Balanza HX711
  balanza.begin(HX711_DT, HX711_SCK);
  balanza.set_scale(factorCalibracion);
  balanza.tare();  // Poner en cero al inicio
  Serial.println("Balanza lista. Factor: " + String(factorCalibracion));

  motorStop();
}

// ================================================================
// LOOP
// ================================================================
void loop() {
  unsigned long ahora = millis();

  // Lectura periódica HC-SR04
  if (ahora - tiempoUltimaLectura >= INTERVALO_SENSOR) {
    tiempoUltimaLectura = ahora;
    distanciaCm = medirDistancia();

    // Auto-motor: objeto detectado < 20 cm → adelante; si se aleja → stop
    if (distanciaCm < DISTANCIA_TRIGGER && !motorActivo) {
      motorActivo = true;
      analogWrite(MOTOR_IN1, velocidad);
      analogWrite(MOTOR_IN2, 0);
      Serial.println("AUTO: objeto detectado → motor adelante");
    } else if (distanciaCm >= DISTANCIA_TRIGGER && motorActivo) {
      motorActivo = false;
      analogWrite(MOTOR_IN1, 0);
      analogWrite(MOTOR_IN2, 0);
      Serial.println("AUTO: objeto alejado → motor stop");
    }
  }

  // Lectura periódica HX711 (solo si está listo para no bloquear)
  if (ahora - tiempoUltimaBalanza >= INTERVALO_BALANZA) {
    tiempoUltimaBalanza = ahora;
    if (balanza.is_ready()) {
      float raw  = balanza.get_units(3);
      pesoGramos = actualizarPromedio(raw);
      // Salida legible para monitor serial + JSON para el frontend
      Serial.print("Peso: ");
      Serial.print(pesoGramos, 2);
      Serial.print(" g | ");
      Serial.print(pesoGramos / 1000.0, 3);
      Serial.println(" kg");
    }
  }

  // Comandos serial
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    procesarComando(cmd);
  }
}

// ================================================================
// SENSOR HC-SR04
// ================================================================
float medirDistancia() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duracion = pulseIn(ECHO_PIN, HIGH, 30000);
  if (duracion == 0) return 999.0;

  return duracion * 0.0343 / 2.0;
}

bool motorPermitido() {
  if (distanciaCm > DISTANCIA_LIMITE) {
    Serial.print("BLOQUEADO: distancia ");
    Serial.print(distanciaCm, 1);
    Serial.println(" cm > 30 cm.");
    return false;
  }
  return true;
}

// ================================================================
// MOTOR
// ================================================================
void motorAdelante() {
  if (!motorPermitido()) return;
  analogWrite(MOTOR_IN1, velocidad);
  analogWrite(MOTOR_IN2, 0);
  Serial.print("Motor: adelante | vel=");
  Serial.println(velocidad);
}

void motorReversa() {
  if (!motorPermitido()) return;
  analogWrite(MOTOR_IN1, 0);
  analogWrite(MOTOR_IN2, velocidad);
  Serial.print("Motor: reversa | vel=");
  Serial.println(velocidad);
}

void motorStop() {
  analogWrite(MOTOR_IN1, 0);
  analogWrite(MOTOR_IN2, 0);
  Serial.println("Motor: stop");
}

// ================================================================
// SERVO
// ================================================================
void moverServo(int angulo) {
  angulo = constrain(angulo, 0, 180);
  anguloServo = angulo;
  miServo.write(anguloServo);
  Serial.print("Servo: ");
  Serial.print(anguloServo);
  Serial.println(" grados");
}

// ================================================================
// PARSER DE COMANDOS
// ================================================================
void procesarComando(String cmd) {
  cmd.toUpperCase();

  if (cmd == "A") {
    motorAdelante();

  } else if (cmd == "R") {
    motorReversa();

  } else if (cmd == "S") {
    motorStop();

  } else if (cmd == "D") {
    float d = medirDistancia();
    distanciaCm = d;
    Serial.print("Distancia: ");
    Serial.print(d, 1);
    Serial.println(" cm");

  } else if (cmd == "W") {
    // Lectura puntual con promedio de 5 muestras
    if (balanza.is_ready()) {
      float p = balanza.get_units(5);
      pesoGramos = actualizarPromedio(p);
      Serial.print("Peso: ");
      Serial.print(pesoGramos, 2);
      Serial.print(" g | ");
      Serial.print(pesoGramos / 1000.0, 3);
      Serial.println(" kg");
    } else {
      Serial.println("Balanza no lista todavia.");
    }

  } else if (cmd == "PF") {
    // Peso Final — promedio de 20 lecturas para maxima precision
    // Se envia como JSON: {"tipo":"peso_final","g":142.50,"kg":0.143}
    if (!balanza.is_ready()) {
      Serial.println("{\"tipo\":\"error\",\"msg\":\"Balanza no lista.\"}");
    } else {
      Serial.println("Capturando peso final...");
      float acumulado = 0.0;
      int   validas   = 0;

      for (int i = 0; i < 20; i++) {
        if (balanza.is_ready()) {
          acumulado += balanza.get_units(1);
          validas++;
        }
        delay(150);
      }

      if (validas == 0) {
        Serial.println("{\"tipo\":\"error\",\"msg\":\"No se obtuvieron lecturas.\"}");
      } else {
        float media  = acumulado / validas;
        float mediaKg = media / 1000.0;
        Serial.print("{\"tipo\":\"peso_final\",\"g\":");
        Serial.print(media, 2);
        Serial.print(",\"kg\":");
        Serial.print(mediaKg, 3);
        Serial.println("}");
      }
    }

  } else if (cmd == "TARA") {
    balanza.tare();
    Serial.println("Balanza tarada (cero).");

  } else if (cmd.startsWith("CAL:")) {
    float factor = cmd.substring(4).toFloat();
    if (factor != 0.0) {
      factorCalibracion = factor;
      balanza.set_scale(factorCalibracion);
      Serial.print("Factor calibracion actualizado: ");
      Serial.println(factorCalibracion);
    } else {
      Serial.println("Factor invalido.");
    }

  } else if (cmd.startsWith("V:")) {
    int val = cmd.substring(2).toInt();
    velocidad = constrain(val, 0, 255);
    Serial.print("Velocidad: ");
    Serial.println(velocidad);

  } else if (cmd.startsWith("G:")) {
    int angulo = cmd.substring(2).toInt();
    moverServo(angulo);

  } else {
    Serial.print("Comando desconocido: ");
    Serial.println(cmd);
  }
}
