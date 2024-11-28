import sqlite3

class Database:
    """
    Diese Klasse verwaltet die SQLite-Datenbank für die Sensoren.
    Sie stellt Funktionen zur Verfügung, um Räume hinzuzufügen und Sensor-Daten zu speichern.
    """

    def __init__(self, db_file="sensors.db"):
        """
        Initialisiert die Datenbankverbindung und erstellt die benötigten Tabellen, falls diese noch nicht existieren.
        
        :param db_file: Der Dateiname der SQLite-Datenbank (Standard: "sensors.db")
        """
        self.connection = sqlite3.connect(db_file)
        self.create_tables()

    def create_tables(self):
        """
        Erstellt die Tabellen in der Datenbank, falls diese noch nicht existieren.
        Diese Tabellen beinhalten Informationen zu Räumen und Sensor-Daten (DHT22, Flammensensor, Gassensor, Lichtsensor).
        """
        with self.connection:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )
            """)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS dht22_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_id INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    temperature REAL,
                    humidity REAL,
                    FOREIGN KEY (room_id) REFERENCES rooms(id)
                )
            """)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS flame_sensor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_id INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fire_detected BOOLEAN,
                    raw_value REAL,
                    FOREIGN KEY (room_id) REFERENCES rooms(id)
                )
            """)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS gas_sensor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_id INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ppm REAL,
                    raw_value REAL,
                    FOREIGN KEY (room_id) REFERENCES rooms(id)
                )
            """)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS light_sensor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_id INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    lux REAL,
                    raw_value REAL,
                    FOREIGN KEY (room_id) REFERENCES rooms(id)
                )
            """)

    def insert_room(self, room_name):
        """
        Fügt einen neuen Raum in die Tabelle "rooms" ein.
        
        :param room_name: Der Name des Raumes, der hinzugefügt werden soll.
        """
        with self.connection:
            self.connection.execute("""
                INSERT INTO rooms (name)
                VALUES (?)
            """, (room_name,))

    def get_room_id_by_name(self, room_name):
        """
        Gibt die ID des Raums anhand des Namens zurück.
        
        :param room_name: Der Name des Raumes, dessen ID abgerufen werden soll.
        :return: Die ID des Raums oder None, falls der Raum nicht existiert.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM rooms WHERE name = ?", (room_name,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None

    def insert_data(self, table, room_id, value1, value2=None):
        """
        Fügt Sensor-Daten in die entsprechende Tabelle ein.
        
        :param table: Der Name der Tabelle, in die die Daten eingefügt werden sollen. (z.B. "dht22_data", "flame_sensor_data", etc.)
        :param room_id: Die ID des Raums, in dem der Sensor gemessen hat.
        :param value1: Der erste Wert, der gespeichert werden soll (z.B. Temperatur, Feuerstatus, etc.)
        :param value2: Ein optionaler zweiter Wert (z.B. Feuchtigkeit, Rohwert, etc.)
        """
        with self.connection:
            if table == "dht22_data":
                self.connection.execute("""
                    INSERT INTO dht22_data (room_id, temperature, humidity)
                    VALUES (?, ?, ?)
                """, (room_id, value1, value2))
            elif table == "flame_sensor_data":
                self.connection.execute("""
                    INSERT INTO flame_sensor_data (room_id, fire_detected, raw_value)
                    VALUES (?, ?, ?)
                """, (room_id, value1, value2))
            elif table == "gas_sensor_data":
                self.connection.execute("""
                    INSERT INTO gas_sensor_data (room_id, ppm, raw_value)
                    VALUES (?, ?, ?)
                """, (room_id, value1, value2))
            elif table == "light_sensor_data":
                self.connection.execute("""
                    INSERT INTO light_sensor_data (room_id, lux, raw_value)
                    VALUES (?, ?, ?)
                """, (room_id, value1, value2))
