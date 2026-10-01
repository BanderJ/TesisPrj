/*
  test_motor_2.ino — Prueba aislada del motor de la faja.

  Driver: L298N (módulo doble puente H) — control de 3 pines por canal.
  Motor:  JGY370 DC 12V, reductor sinfín 10 RPM, alto par, autobloqueante.

  Cableado (canal A del L298N):
    ENA  → D5  (PWM, velocidad)   — RETIRAR el jumper de ENA del módulo
    IN1  → D4  (sentido)
    IN2  → D3  (sentido)
    OUT1 / OUT2 → los 2 cables del motor JGY370
    +12V → fuente de 12 V            GND → GND común con el Arduino
    Jumper de 5V del módulo: quitarlo si el Arduino se alimenta por USB;
    dejarlo solo si la fuente es ≤ 12 V y se usa el regulador interno.

  Notas del hardware nuevo:
    - El L298N cae ~1.8–2 V: con fuente de 12 V el motor recibe ~10 V.
    - El reductor sinfín es autobloqueante — al parar (ENA=0) la faja queda
      retenida por el propio engranaje; no hace falta freno activo.
    - Motor muy reducido (10 RPM): más fricción de arranque que un DC
      directo. Usar 'T' para ver a qué PWM mínimo arranca sin ayuda.

  Usa los MISMOS conceptos que logica_hardware.ino (velocidad PWM, sentido)
  para validar cableado, sentido de giro y arranque antes de producción.
  No toca servo, ultrasónico ni protocolo backend.

  Uso: cargar el sketch, abrir Monitor Serie a 9600 baud (fin de línea: NL)
  y enviar comandos de una letra:

    A  → giro ADELANTE a la velocidad actual
    R  → giro en REVERSA a la velocidad actual
    P  → parar motor (el reductor lo mantiene fijo)
    +  → subir velocidad (+25 PWM)
    -  → bajar velocidad (-25 PWM)
    V  → fijar velocidad exacta, ej: V150
    T  → secuencia automática de prueba (rampa adelante, pausa, reversa)
    ?  → mostrar estado y ayuda

  Nota: la velocidad de producción es 150 (VELOCIDAD en logica_hardware.ino,
  sincronizada con FAJA_VELOCIDAD_PWM en src/config.py). Con el reductor
  JGY370 puede requerir recalibración: si a 150 la faja no arranca sola,
  subir el valor en ambos sitios.
*/

#define MOTOR_ENA  5   // PWM — velocidad (jumper ENA del L298N retirado)
#define MOTOR_IN1  4   // sentido
#define MOTOR_IN2  3   // sentido

const int VELOCIDAD_INICIAL = 150;  // igual a producción — recalibrar con el reductor
const int VELOCIDAD_MIN     = 0;
const int VELOCIDAD_MAX     = 255;
const int PASO_VELOCIDAD    = 55;

int  velocidad = VELOCIDAD_INICIAL;
int  sentido   = -1;   // 0 = parado, 1 = adelante, -1 = reversa
String lineaSerial = "";

void setup() {
  Serial.begin(9600);  // clones con resonador cerámico fallan a 115200
  pinMode(MOTOR_ENA, OUTPUT);
  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MOTOR_IN2, OUTPUT);
  aplicarMotor();
  Serial.println("TEST MOTOR L298N LISTO");
  imprimirAyuda();
}

void loop() {
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
}

void procesarComando(String cmd) {
  cmd.toUpperCase();
  char letra = cmd.charAt(0);

  switch (letra) {
    case 'A':
      sentido = 1;
      aplicarMotor();
      break;

    case 'R':
      sentido = -1;
      aplicarMotor();
      break;

    case 'P':
      sentido = 0;
      aplicarMotor();
      break;

    case '+':
      velocidad = min(velocidad + PASO_VELOCIDAD, VELOCIDAD_MAX);
      aplicarMotor();
      break;

    case '-':
      velocidad = max(velocidad - PASO_VELOCIDAD, VELOCIDAD_MIN);
      aplicarMotor();
      break;

    case 'V': {
      int v = cmd.substring(1).toInt();
      if (v >= VELOCIDAD_MIN && v <= VELOCIDAD_MAX) {
        velocidad = v;
        aplicarMotor();
      } else {
        Serial.println("ERROR: velocidad fuera de rango (0-255)");
      }
      break;
    }

    case 'T':
      secuenciaAutomatica();
      break;

    case '?':
      imprimirAyuda();
      break;

    default:
      Serial.print("Comando desconocido: ");
      Serial.println(cmd);
  }
}

// Programa el L298N: dir = 1 adelante, -1 reversa, 0 parado; pwm 0-255.
// Velocidad por ENA (PWM), sentido por IN1/IN2 (digital).
void motorHardware(int dir, int pwm) {
  if (dir == 1) {
    digitalWrite(MOTOR_IN1, HIGH);
    digitalWrite(MOTOR_IN2, LOW);
    analogWrite(MOTOR_ENA, pwm);
  } else if (dir == -1) {
    digitalWrite(MOTOR_IN1, LOW);
    digitalWrite(MOTOR_IN2, HIGH);
    analogWrite(MOTOR_ENA, pwm);
  } else {
    analogWrite(MOTOR_ENA, 0);
    digitalWrite(MOTOR_IN1, LOW);
    digitalWrite(MOTOR_IN2, LOW);
  }
}

// Escribe el estado actual (sentido + velocidad) en el L298N y lo reporta.
void aplicarMotor() {
  motorHardware(sentido, velocidad);
  imprimirEstado();
}

void imprimirEstado() {
  Serial.print("ESTADO: ");
  if (sentido == 0)       Serial.print("PARADO");
  else if (sentido == 1)  Serial.print("ADELANTE");
  else                    Serial.print("REVERSA");
  Serial.print(" | PWM: ");
  Serial.println(velocidad);
}

/*
  Secuencia automática:
    1. Rampa de arranque adelante: sube PWM de 0 a la velocidad configurada
       en pasos de 25, 500 ms por paso — permite observar a qué PWM mínimo
       arranca físicamente la faja con el reductor JGY370.
    2. Mantiene 3 s a velocidad plena.
    3. Para 1 s (el reductor sinfín retiene la faja).
    4. Reversa 2 s a velocidad configurada.
    5. Para y restaura el estado.
  Bloqueante a propósito: es una prueba de banco, no producción.
*/
void secuenciaAutomatica() {
  int velObjetivo = velocidad;
  Serial.println("--- SECUENCIA AUTOMATICA ---");

  Serial.println("1. Rampa adelante (observar PWM minimo de arranque):");
  for (int v = PASO_VELOCIDAD; v <= velObjetivo; v += PASO_VELOCIDAD) {
    motorHardware(1, v);
    Serial.print("   PWM: ");
    Serial.println(v);
    delay(500);
  }

  Serial.println("2. Velocidad plena 3 s...");
  motorHardware(1, velObjetivo);
  delay(3000);

  Serial.println("3. Parada 1 s (autobloqueo del reductor)...");
  motorHardware(0, 0);
  delay(1000);

  Serial.println("4. Reversa 2 s...");
  motorHardware(-1, velObjetivo);
  delay(2000);

  Serial.println("5. Fin — motor parado.");
  sentido = 0;
  aplicarMotor();
}

void imprimirAyuda() {
  Serial.println("Comandos: A=adelante R=reversa P=parar +/-=velocidad");
  Serial.println("          V<n>=fijar PWM (ej V150) T=secuencia auto ?=ayuda");
  imprimirEstado();
}
