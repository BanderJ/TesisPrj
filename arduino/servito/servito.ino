/*
  servito.ino — Prueba aislada del servo separador.

  Sirve para separar las dos causas posibles de "el servo no reacciona":
    1. Falla física (cableado, alimentación, ángulo insuficiente) → modo manual.
    2. El comando del backend no llega al Arduino → modo backend.

  Cableado (igual que logica_hardware.ino):
    Señal (naranja) → D9
    VCC (rojo)      → 5 V
    GND (marrón)    → GND común con el Arduino
  Si el servo tiembla, se reinicia el Arduino o no llega al ángulo, la causa
  suele ser la alimentación: el pin 5V del Arduino por USB no da la corriente
  de arranque de un servo. Alimentarlo con una fuente de 5 V aparte, uniendo
  los GND.

  Comparte pin, ANGULO_BUENO y ANGULO_DEFECTO con logica_hardware.ino.
  HOLD_MS solo controla los pulsos manuales P/C. En modo backend, Python
  controla la duración mediante SERVO_HOLD_S y envía SERVO:BUENO para volver.
  No toca motor, ultrasónico ni báscula.

  ── Modo manual ─────────────────────────────────────────────────────────
  Cargar el sketch, abrir Monitor Serie a 9600 baud (fin de línea: NL) y
  enviar:

    D     → posición DEFECTO (ANGULO_DEFECTO)
    B     → posición BUENO (ANGULO_BUENO)
    P     → pulso manual: DEFECTO, sostiene HOLD_MS, vuelve a BUENO
    C     → 10 pulsos seguidos (uno cada segundo) para ver si es constante
    G<n>  → mover a un ángulo exacto, ej: G30 (0-180), para hallar el ángulo
            que de verdad saca el grano de la faja
    ?     → estado y ayuda

  ── Modo backend ────────────────────────────────────────────────────────
  Con este sketch cargado, cerrar el Monitor Serie (el puerto queda libre) y
  arrancar la app. El sketch también acepta los comandos de producción
  SERVO:DEFECTO y SERVO:BUENO, y en cada SERVO:DEFECTO enciende el LED de la
  placa (D13) durante 1 s. Pasar un grano negro:
    - LED enciende y el servo se mueve  → backend y servo bien.
    - LED enciende y el servo NO se mueve → falla física (ver modo manual).
    - LED no enciende                    → el backend no envía el comando
      (revisar [servo-debug] con ML_DEBUG_SERVO=true y los errores [ArduinoSerial];
      no se registra cada envío exitoso del servo ni su instante).
  La faja no arranca con este sketch: mover el grano a mano bajo la cámara.

  Si se vuelve a ajustar el ángulo, mantener ANGULO_DEFECTO igual aquí y en
  logica_hardware.ino.
*/

#include <Servo.h>

#define SERVO_PIN  9   // naranja
#define LED_PIN    13  // LED de la placa: aviso de comando recibido

const int ANGULO_BUENO   = 0;    // igual que logica_hardware.ino
const int ANGULO_DEFECTO = 30;   // igual que logica_hardware.ino
const unsigned long HOLD_MS     = 300;   // 0.3 s, solo para pulsos manuales P/C
const unsigned long LED_AVISO_MS = 1000;

Servo servoSeparador;
int anguloActual = ANGULO_BUENO;
unsigned long recibidos = 0;     // SERVO:DEFECTO recibidos desde el backend
unsigned long tApagarLed = 0;

String lineaSerial = "";

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  servoSeparador.attach(SERVO_PIN);
  mover(ANGULO_BUENO);

  Serial.println("SISTEMA:LISTO");
  mostrarAyuda();
}

void loop() {
  // Lectura no bloqueante, carácter a carácter (igual que producción)
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

  if (tApagarLed != 0 && millis() >= tApagarLed) {
    digitalWrite(LED_PIN, LOW);
    tApagarLed = 0;
  }
}

void procesarComando(String cmd) {
  // Comandos de producción (modo backend)
  if (cmd == "SERVO:DEFECTO") {
    recibidos++;
    digitalWrite(LED_PIN, HIGH);
    tApagarLed = millis() + LED_AVISO_MS;
    mover(ANGULO_DEFECTO);
    return;
  }
  if (cmd == "SERVO:BUENO") {
    mover(ANGULO_BUENO);
    return;
  }
  // ON / OFF / TARE del backend: se ignoran, este sketch no maneja la faja.
  if (cmd == "ON" || cmd == "OFF" || cmd.startsWith("TARE")) return;

  // Comandos manuales (Monitor Serie)
  char op = toupper(cmd.charAt(0));
  switch (op) {
    case 'D':
      mover(ANGULO_DEFECTO);
      informar("DEFECTO");
      break;
    case 'B':
      mover(ANGULO_BUENO);
      informar("BUENO");
      break;
    case 'P':
      pulso();
      informar("PULSO");
      break;
    case 'C':
      for (int i = 1; i <= 10; i++) {
        pulso();
        Serial.print("Pulso ");
        Serial.print(i);
        Serial.println("/10");
        delay(1000 - HOLD_MS);
      }
      informar("CICLO TERMINADO");
      break;
    case 'G': {
      int angulo = cmd.substring(1).toInt();
      if (angulo < 0 || angulo > 180) {
        Serial.println("Angulo fuera de rango (0-180)");
        return;
      }
      mover(angulo);
      informar("ANGULO MANUAL");
      break;
    }
    case '?':
      mostrarAyuda();
      break;
    default:
      Serial.print("Comando desconocido: ");
      Serial.println(cmd);
  }
}

// Pulso manual bloqueante; el backend controla su propia duración.
void pulso() {
  mover(ANGULO_DEFECTO);
  delay(HOLD_MS);
  mover(ANGULO_BUENO);
}

void mover(int angulo) {
  servoSeparador.write(angulo);
  anguloActual = angulo;
}

void informar(const char* accion) {
  Serial.print(accion);
  Serial.print(" -> angulo ");
  Serial.println(anguloActual);
}

void mostrarAyuda() {
  Serial.println("--- servito: prueba del servo separador ---");
  Serial.print("Angulo actual: ");
  Serial.print(anguloActual);
  Serial.print(" | BUENO=");
  Serial.print(ANGULO_BUENO);
  Serial.print(" DEFECTO=");
  Serial.print(ANGULO_DEFECTO);
  Serial.print(" | SERVO:DEFECTO recibidos del backend: ");
  Serial.println(recibidos);
  Serial.println("D=defecto  B=bueno  P=pulso  C=10 pulsos  G<n>=angulo  ?=ayuda");
}
