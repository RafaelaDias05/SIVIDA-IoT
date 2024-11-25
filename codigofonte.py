import sqlite3
import time
from datetime import datetime
import Adafruit_DHT


class EnvironmentalMonitor:
    def __init__(self, db_name="environment_data.db"):
        self.db_name = db_name
        self.sensor = Adafruit_DHT.DHT22
        self.pin = 4  # GPIO do sensor
        self.create_table()

    def create_table(self):
        """Cria a tabela no banco de dados para armazenar os dados ambientais."""
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS environment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                temperature REAL,
                humidity REAL,
                air_quality TEXT
            )
        """)
        connection.commit()
        connection.close()

    def read_sensors(self):
        """Lê dados do sensor DHT22."""
        humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.pin)
        air_quality = "Bom"  # Aqui você pode integrar outro sensor para qualidade do ar
        if humidity is not None and temperature is not None:
            return {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "temperature": round(temperature, 2),
                "humidity": round(humidity, 2),
                "air_quality": air_quality
            }
        else:
            print("Falha ao ler os dados do sensor. Tentando novamente...")
            return None

    def save_to_database(self, data):
        """Salva os dados coletados no banco de dados."""
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO environment (timestamp, temperature, humidity, air_quality)
            VALUES (?, ?, ?, ?)
        """, (data['timestamp'], data['temperature'], data['humidity'], data['air_quality']))
        connection.commit()
        connection.close()

    def display_data(self, data):
        """Exibe os dados no terminal."""
        print(f"[{data['timestamp']}] Temperatura: {data['temperature']}°C | "
              f"Umidade: {data['humidity']}% | Qualidade do Ar: {data['air_quality']}")

    def get_logs(self):
        """Recupera e exibe os registros salvos no banco de dados."""
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM environment")
        rows = cursor.fetchall()
        connection.close()
        print("Registros no Banco de Dados:")
        for row in rows:
            print(row)


def main():
    monitor = EnvironmentalMonitor()
    print("Monitoramento ambiental iniciado. Pressione Ctrl+C para encerrar.")

    try:
        while True:
            data = monitor.read_sensors()
            if data:
                monitor.save_to_database(data)
                monitor.display_data(data)
            time.sleep(2)  # Intervalo entre leituras
    except KeyboardInterrupt:
        print("\nMonitoramento encerrado pelo usuário.")
        monitor.get_logs()


if __name__ == "__main__":
    main()
