#include <Servo.h>
#include <HX711.h>

// === PINES ===
#define MOTOR_IN1    5
#define MOTOR_IN2    6
#define TRIG_PIN     7
#define ECHO_PIN     8
#define SERVO_PIN    9
#define HX711_DOUT   2
#define HX711_SCK    3

// === AJUSTES ===
const float DISTANCIA_UMBRAL       = 20.0;   // cm — verificación de tapa
const int   VELOCIDAD              = 220;    // velocidad faja (0-255)
const int   ANGULO_BUENO           = 150;    // servo: canal granos buenos
const int   ANGULO_DEFECTO         = 30;     // servo: canal granos defectuosos
const float FACTOR_CALIBRACION     = 2280.0; // ajustar tras calibración real (ver abajo)
const int   BUFFER_PESO            = 5;      // muestras para promedio deslizante
const unsigned long MS_DISTANCIA   = 100;    // reporte sensor cada 100 ms
const unsigned long MS_PESO        = 500;    // reporte peso cada 500 ms

/*
  CALIBRACIÓN DE LA CELDA DE CARGA:
  1. Cargar sketch con FACTOR_CALIBRACION = 1.0
  2. Tara con plataforma vacía (comando TARE)
  3. Colocar peso conocido (ej. 500 g)
  4. Leer valor raw del Serial: bascula.read_average(20)
  5. FACTOR_CALIBRACION = valor_raw / 500.0
*/

Servo  servoSeparador;
HX711  bascula;
bool   motorActivo = false;

// Promedio deslizante de peso
float  bufferPeso[BUFFER_PESO] = {0.0};
int    idxPeso                 = 0;
bool   bufferLleno             = false;

// Temporizadores millis()
unsigned long tDistancia = 0;
unsigned long tPeso      = 0;

// Buffer para leer líneas serial sin bloquear
String lineaSerial = "";

void setup() {
  Serial.begin(9600);

  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MOTOR_IN2, OUTPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  servoSeparador.attach(SERVO_PIN);
  servoSeparador.write(ANGULO_BUENO);

  bascula.begin(HX711_DOUT, HX711_SCK);
  bascula.set_scale(FACTOR_CALIBRACION);
  bascula.tare();

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

  // 4. Lectura y reporte de peso (celda de carga)
  if (ahora - tPeso >= MS_PESO && bascula.is_ready()) {
    tPeso = ahora;

    // Leer 1 muestra (no bloquea ya que is_ready() fue true)
    float lectura = bascula.get_units(1);

    // Actualizar promedio deslizante
    bufferPeso[idxPeso] = lectura;
    idxPeso = (idxPeso + 1) % BUFFER_PESO;
    if (idxPeso == 0) bufferLleno = true;

    int n = bufferLleno ? BUFFER_PESO : idxPeso;
    float suma = 0.0;
    for (int i = 0; i < n; i++) suma += bufferPeso[i];
    float promedio = suma / n;

    Serial.print("PESO:");
    Serial.println(promedio, 2);
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

  } else if (cmd == "TARE") {
    bascula.tare();
    // Resetear buffer tras tara
    for (int i = 0; i < BUFFER_PESO; i++) bufferPeso[i] = 0.0;
    idxPeso    = 0;
    bufferLleno = false;
    Serial.println("TARE:OK");

  } else if (cmd.startsWith("SCALE:")) {
    float factor = cmd.substring(6).toFloat();
    if (factor != 0.0) {
      bascula.set_scale(factor);
      Serial.println("SCALE:OK");
    }
  }
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
