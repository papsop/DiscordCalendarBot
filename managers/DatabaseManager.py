import config
import sqlite3
import sys

class DatabaseManager:
    _dbname = ""
    _connnection = None
    _bot = None

    def __init__(self, bot):
        self._bot = bot
        self._dbname = config.database['file_name']
        self._connnection = sqlite3.connect(self._dbname)
        print("✓ DatabaseManager initialized")
        self.create_tables()

    def get_cursor(self):
        return self._connnection.cursor()
    def commit(self):
        self._connnection.commit()

    def create_tables(self):
        cursor = self.get_cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS server(
                'server_id' UNSIGNED BIG INT NOT NULL UNIQUE PRIMARY KEY,
                'prefix' VARCHAR(10) NOT NULL DEFAULT '!',
                'admin_id' UNSIGNED BIG INT NOT NULL,
                'is_admin_user' BOOLEAN NOT NULL DEFAULT TRUE,
                'calendars_num' INT NOT NULL DEFAULT 0,
                'calendars_max' INT NOT NULL DEFAULT 10
            );
            CREATE TABLE IF NOT EXISTS calendar(
                'server_id' UNSIGNED BIG INT,
                'timezone' VARCHAR(50) NOT NULL,
                'channel_id' UNSIGNED BIG INT NOT NULL,
                'message_id' UNSIGNED BIG INT NOT NULL,
                FOREIGN KEY(server_id) REFERENCES server(server_id)
            );
        """)
        print("  ✓ Database tables updated")

    # ============
    #    SERVER
    # ============
    def insert_server(self, server_data):
        cursor = self.get_cursor()
        try:
            if not 'server_id' in server_data or not 'prefix' in server_data \
            or not 'admin_id' in server_data or not 'is_admin_user' in server_data:
                raise Exception("[DatabaseManager.insert_server] Missing parameters")

            row = cursor.execute("""
                INSERT INTO server(server_id, prefix, admin_id, is_admin_user) 
                VALUES(:server_id, :prefix, :admin_id, :is_admin_user)
                """, server_data)
        except: # TODO
            cursor.close()
            raise

        self.commit()
        cursor.close()
        print("Server {0[server_id]} with prefix '{0[prefix]}' successfully added.".format(server_data))

    def get_server(self, server_id):
        cursor = self.get_cursor()
        try:
            row = cursor.execute("SELECT server_id, prefix FROM server WHERE server_id=?;", (server_id,)).fetchone()
        except:
            cursor.close()
            raise

        cursor.close()
        return row

    def get_servers(self):
        # only cacheManager should use this
        cursor = self.get_cursor()
        servers = cursor.execute("SELECT server_id, prefix, admin_id, is_admin_user FROM server;").fetchall()
        cursor.close()
        return servers

    # ==============
    #    CALENDAR
    # ==============

    def insert_calendar(self, calendar_data):
        cursor = self.get_cursor()
        try:
            if not 'server_id' in calendar_data or not 'timezone' in calendar_data \
            or not 'channel_id' in calendar_data or not 'message_id' in calendar_data:
                raise Exception("[DatabaseManager.insert_calendar] Missing parameters")

            row = cursor.execute("""
                INSERT INTO calendar(server_id, timezone, channel_id, message_id) 
                VALUES(:server_id, :timezone, :channel_id, :message_id)
                """, calendar_data)
        except:
            cursor.close()
            raise

        self.commit()
        cursor.close()