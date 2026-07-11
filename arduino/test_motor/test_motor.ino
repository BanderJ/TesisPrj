/*
  test_motor.ino — Prueba aislada del motor de la faja (puente H).

  Usa los MISMOS pines que logica_hardware.ino (MOTOR_IN1=5, MOTOR_IN2=6)
  para validar cableado, sentido de giro y velocidad PWM antes de cargar
  el sketch de producción. No toca servo, ultrasonico ni protocolo backend.

  Uso: cargar el sketch, abrir Monitor Serie a 9600 baud (fin de línea: NL)
  y enviar comandos de una letra:

    A  → giro ADELANTE a la velocidad actual
    R  → giro en REVERSA a la velocidad actual
    P  → parar motor
    +  → subir velocidad (+25 PWM)
    -  → bajar velocidad (-25 PWM)
    V  → fijar velocidad exacta, ej: V150
    T  → secuencia automática de prueba (rampa adelante, pausa, reversa)
    ?  → mostrar estado y ayuda

  Nota: la velocidad de producción es 150 (VELOCIDAD en logica_hardware.ino,
  sincronizada con FAJA_VELOCIDAD_PWM en src/config.py). Verificar que la
  faja arranque sin ayuda a ese valor — si no arranca, el driver o la
  alimentación necesitan revisión.
*/

#define MOTOR_IN1  5   // PWM — adelante
#define MOTOR_IN2  6   // PWM — reversa

const int VELOCIDAD_INICIAL = 150;  // igual a producción
const int VELOCIDAD_MIN     = 0;
const int VELOCIDAD_MAX     = 255;
const int PASO_VELOCIDAD    = 25;

int  velocidad = VELOCIDAD_INICIAL;
int  sentido   = 0;   // 0 = parado, 1 = adelante, -1 = reversa
String lineaSerial = "";

void setup() {
  Serial.begin(9600);  // clones con resonador cerámico fallan a 115200
  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MOTOR_IN2, OUTPUT);
  aplicarMotor();
  Serial.println("TEST MOTOR LISTO");
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

// Escribe el estado actual (sentido + velocidad) en el puente H y lo reporta.
void aplicarMotor() {
  if (sentido == 1) {
    analogWrite(MOTOR_IN1, velocidad);
    analogWrite(MOTOR_IN2, 0);
  } else if (sentido == -1) {
    analogWrite(MOTOR_IN1, 0);
    analogWrite(MOTOR_IN2, velocidad);
  } else {
    analogWrite(MOTOR_IN1, 0);
    analogWrite(MOTOR_IN2, 0);
  }
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
       arranca físicamente la faja.
    2. Mantiene 3 s a velocidad plena.
    3. Para 1 s.
    4. Reversa 2 s a velocidad configurada.
    5. Para y restaura el estado.
  Bloqueante a propósito: es una prueba de banco, no producción.
*/
void secuenciaAutomatica() {
  int velObjetivo = velocidad;
  Serial.println("--- SECUENCIA AUTOMATICA ---");

  Serial.println("1. Rampa adelante (observar PWM minimo de arranque):");
  for (int v = PASO_VELOCIDAD; v <= velObjetivo; v += PASO_VELOCIDAD) {
    analogWrite(MOTOR_IN1, v);
    analogWrite(MOTOR_IN2, 0);
    Serial.print("   PWM: ");
    Serial.println(v);
    delay(500);
  }

  Serial.println("2. Velocidad plena 3 s...");
  analogWrite(MOTOR_IN1, velObjetivo);
  analogWrite(MOTOR_IN2, 0);
  delay(3000);

  Serial.println("3. Parada 1 s...");
  analogWrite(MOTOR_IN1, 0);
  analogWrite(MOTOR_IN2, 0);
  delay(1000);

  Serial.println("4. Reversa 2 s...");
  analogWrite(MOTOR_IN1, 0);
  analogWrite(MOTOR_IN2, velObjetivo);
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
