// === CONFIGURACIÓN DE PINES ===
#define MOTOR_IN1 5   // Pin PWM para el motor
#define MOTOR_IN2 6   // Pin PWM para el motor
#define TRIG_PIN  7   // Sensor Ultrasonico Trig
#define ECHO_PIN  8   // Sensor Ultrasonico Echo

// === AJUSTES DEL SISTEMA ===
const float DISTANCIA_UMBRAL = 20.0; // Distancia en cm para activar
const int VELOCIDAD = 220;           // Velocidad de la faja (0 a 255)

void setup() {
  Serial.begin(9600);
  
  // Configuración de motores
  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MOTOR_IN2, OUTPUT);

  // Configuración de sensor
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  Serial.println("Sistema de Faja Automática Iniciado");
}

void loop() {
  // 1. Obtener la distancia actual
  float distancia = leerUltrasonico();

  // 2. Control del motor según la distancia
  if (distancia > 0 && distancia < DISTANCIA_UMBRAL) {
    // Objeto detectado: Mover motor hacia adelante
    analogWrite(MOTOR_IN1, VELOCIDAD);
    analogWrite(MOTOR_IN2, 0);
    
    Serial.print("OBJETO DETECTADO: ");
    Serial.print(distancia);
    Serial.println(" cm. Motor ENCENDIDO.");
  } 
  else {
    // No hay objeto o está lejos: Detener motor
    analogWrite(MOTOR_IN1, 0);
    analogWrite(MOTOR_IN2, 0);
    
    Serial.print("Despejado: ");
    Serial.print(distancia);
    Serial.println(" cm. Motor APAGADO.");
  }

  delay(100); // Pequeña pausa para estabilidad
}

// Función para medir la distancia con el HC-SR04
float leerUltrasonico() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duracion = pulseIn(ECHO_PIN, HIGH, 30000); // Timeout de 30ms
  
  // Calcular distancia en cm
  float cm = duracion * 0.0343 / 2.0;
  
  return cm;
}