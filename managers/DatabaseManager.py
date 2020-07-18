import config
import sqlite3
import sys
from datetime import datetime, timedelta
import pytz

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class DatabaseManager:
    _dbname = ""
    _connnection = None
    _bot = None

    def __init__(self, bot):
        self._bot = bot
        self._dbname = config.database['file_name']
        self._connnection = sqlite3.connect(self._dbname)
        self._connnection.row_factory = dict_factory
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
                'name' VARCHAR(255),
                'prefix' VARCHAR(10) NOT NULL DEFAULT '!',
                'admin_id' UNSIGNED BIG INT NOT NULL,
                'is_admin_user' BOOLEAN NOT NULL DEFAULT TRUE,
                'calendars_num' INT NOT NULL DEFAULT 0,
                'calendars_max' INT NOT NULL DEFAULT 20
            );
            CREATE TABLE IF NOT EXISTS calendar(
                'ID' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                'server_id' UNSIGNED BIG INT,
                'timezone' VARCHAR(50) NOT NULL,
                'channel_id' UNSIGNED BIG INT NOT NULL,
                'message_id' UNSIGNED BIG INT NOT NULL,
                'teamup_calendar_key' VARCHAR(100) NOT NULL,
                'timetype' UNSIGNED TINYINT NOT NULL default '0',
                'datetype' UNSIGNED TINYINT NOT NULL default '0',
                'reminder_time' UNSIGNED SMALLINT NOT NULL default '15',
                'last_update' DATETIME NOT NULL,
                FOREIGN KEY(server_id) REFERENCES server(server_id)
            );
            CREATE TABLE IF NOT EXISTS reminded_event(
                'ID' INTEGER NOT NULL,
                'version' VARCHAR(50) NOT NULL,
                'timestamp' TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
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
                INSERT INTO server(server_id, prefix, admin_id, is_admin_user, name) 
                VALUES(:server_id, :prefix, :admin_id, :is_admin_user, :name)
                """, server_data)
        except Exception as e: # TODO
            cursor.close()
            raise e

        self.commit()
        cursor.close()
    
    def update_server(self, new_server_data):
        cursor = self.get_cursor()
        try:
            if not 'server_id' in new_server_data or not 'prefix' in new_server_data \
            or not 'admin_id' in new_server_data or not 'is_admin_user' in new_server_data:
                raise Exception("[DatabaseManager.update_server] Missing parameters")
                
            row = cursor.execute("""
                UPDATE server SET prefix=:prefix, admin_id=:admin_id, is_admin_user=:is_admin_user WHERE server_id=:server_id
            """, new_server_data)
        except Exception as e:
            cursor.close()
            raise e
            
        self.commit()
        cursor.close()

    def get_server(self, server_id):
        cursor = self.get_cursor()
        try:
            row = cursor.execute("SELECT * FROM server WHERE server_id=?;", (server_id,)).fetchone()
        except Exception as e:
            cursor.close()
            raise e

        cursor.close()
        return row

    def get_servers(self):
        # only cacheManager should use this
        cursor = self.get_cursor()
        servers = cursor.execute("SELECT * FROM server;").fetchall()
        cursor.close()
        return servers

    # ==============
    #    CALENDAR
    # ==============

    def insert_calendar(self, calendar_data):
        cursor = self.get_cursor()
        last_id = -1
        try:
            if not 'server_id' in calendar_data or not 'timezone' in calendar_data \
            or not 'channel_id' in calendar_data or not 'message_id' in calendar_data:
                raise Exception("[DatabaseManager.insert_calendar] Missing parameters")

            server = self.get_server(calendar_data["server_id"])
            if server != None:
                now_utc = datetime.utcnow()
                calendar_data["last_update"] = now_utc
                row = cursor.execute("""
                    INSERT INTO calendar(server_id, timezone, channel_id, message_id, teamup_calendar_key, last_update) 
                    VALUES(:server_id, :timezone, :channel_id, :message_id, :teamup_calendar_key, :last_update)
                    """, calendar_data)

                last_id = cursor.execute("SELECT seq FROM sqlite_sequence WHERE name='calendar';").fetchone()
            else:
                raise Exception("[DatabaseManager.insert_calendar] Server_id not in database")
        except Exception as e:
            cursor.close()
            raise e

        self.commit()
        cursor.close()
        return last_id["seq"]
        
    def get_calendar(self, server_id, calendar_id):
        if server_id == None or calendar_id == None:
            raise Exception("[DatabaseManager.get_calendar] Server_id or Calendar_id missing")
        
        cursor = self.get_cursor()
        try:
            row = cursor.execute("SELECT * FROM calendar WHERE ID=? AND server_id=?;", (calendar_id, server_id, )).fetchone()
        except Exception as e:
            cursor.close()
            raise e

        cursor.close()
        return row
    
    def update_calendar_timestamp(self, calendar_id):
        if calendar_id == None:
            raise Exception("[DatabaseManager.get_calendar] Server_id or Calendar_id missing")
        cursor = self.get_cursor()
        try:
            row = cursor.execute("UPDATE calendar SET last_update=? WHERE ID=?;", (datetime.now(), calendar_id, ))
        except Exception as e:
            cursor.close()
            raise e

        cursor.close()
        return row

    def update_calendar_setting(self, server_id, calendar_id, name, value):
        if name != "timezone" and name != "datetype" and name != "timetype" and name != "reminder":
            raise Exception("[DatabaseManager.update_calendar_setting] name must be timezone/datetype/timetype/reminder")

        cursor = self.get_cursor()
        try:
            # can't put variable as column name :(
            if name == "timezone":
                row = cursor.execute("UPDATE calendar SET timezone=? WHERE ID=? AND server_id=?;", (value, calendar_id, server_id, ))
            elif name == "datetype":
                row = cursor.execute("UPDATE calendar SET datetype=? WHERE ID=? AND server_id=?;", (value, calendar_id, server_id, ))
            elif name == "timetype":
                row = cursor.execute("UPDATE calendar SET timetype=? WHERE ID=? AND server_id=?;", (value, calendar_id, server_id, ))
            elif name == "reminder":
                row = cursor.execute("UPDATE calendar SET reminder_time=? WHERE ID=? AND server_id=?;", (value, calendar_id, server_id, ))
        except Exception as e:
            raise e
        
        self.commit()
        cursor.close()
        return row

    # SOME DELETING
    def delete_calendars_by_channel(self, channel_id):
        # unable to find this channel_id -> delete all calendars with this channel
        cursor = self.get_cursor()
        try:
            row = cursor.execute("DELETE FROM calendar WHERE channel_id=?;", (channel_id, ))
        except Exception as e:
            raise e
        
        self.commit()
        cursor.close()
        return row

    def delete_calendars_by_message(self, message_id):
        # unable to find this message_id -> delete calendar
        cursor = self.get_cursor()
        try:
            row = cursor.execute("DELETE FROM calendar WHERE message_id=?;", (message_id, ))
        except Exception as e:
            raise e
        
        self.commit()
        cursor.close()
        return row
    
    def delete_server(self, server_id):
        # unable to find server -> delete server and all calendars
        cursor = self.get_cursor()
        try:
            row2 = cursor.execute("DELETE FROM calendar WHERE server_id=?;", (server_id, ))
            row = cursor.execute("DELETE FROM server WHERE server_id=?;", (server_id, ))
        except Exception as e:
            raise e
        
        self.commit()
        cursor.close()
        return row2

    # =====================
    #    REMINDED EVENTS
    # =====================

    def clean_reminded_events(self):
        cursor = self.get_cursor()
        try:
            time_2weeks_back = (datetime.now() - timedelta(days=14))
            row = cursor.execute("DELETE FROM reminded_event WHERE timestamp <= ?", (time_2weeks_back, )).fetchall()
            print("{0} Database cleaned".format(datetime.now()))
        except Exception as e: # no further raising since it's only used in periodic checks
            cursor.close()
            self._bot.backend_log("[DatabaseManager.clean_reminded_events]", str(e))

        self.commit()
        cursor.close()

    def add_reminded_event(self, event_id, version):
        cursor = self.get_cursor()
        try:
            row = cursor.execute("""
                INSERT INTO reminded_event(ID, version) 
                VALUES(?, ?)
                """, (event_id, version, ))
        except Exception as e: # no further raising since it's only used in periodic checks
            cursor.close()
            self._bot.backend_log("[DatabaseManager.add_reminded_event]", str(e))

        self.commit()
        cursor.close()

    def get_reminded_event(self, event_id, version):
        cursor = self.get_cursor()
        try:
            row = cursor.execute("SELECT * FROM reminded_event WHERE ID=? AND version=?;", (event_id, version, )).fetchone()
        except Exception as e: # no further raising since it's only used in periodic checks
            cursor.close()
            self._bot.backend_log("[DatabaseManager.add_reminded_event]", str(e))

        cursor.close()
        return row