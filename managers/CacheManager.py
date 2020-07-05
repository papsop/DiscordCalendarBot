
class CacheManager:
    """
        -------- PLACEHOLDER --------
        Just to speed up checking prefixes for each message.
        TODO: better implementation, don't load all the servers
    """
    _databaseManager = None
    _servers_cache = {}
    hits = 0
    reloads = 0

    def __init__(self, bot):
        self._databaseManager = bot._databaseManager
        print("✓ CacheManager initialized")
        self.reload_servers_cache()

    #
    # Servers cache
    #

    def reload_servers_cache(self):
        self.reloads += 1
        self._servers_cache = {}
        servers = self._databaseManager.get_servers()
        for server in servers:
            self._servers_cache[server[0]] = {
                "prefix": server[1]
            }
        print("  ✓ servers_cache reloaded")

    def get_server_cache(self, server_id):
        self.hits += 1
        if server_id in self._servers_cache:
            return self._servers_cache[server_id]
        else:
            return None

    def insert_server(self, server_data):
        try:
            self._databaseManager.insert_server(server_data)
        except:
            raise
        self.reload_servers_cache()