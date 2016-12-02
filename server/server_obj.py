
gl_clients = []
gl_nicknames = []

def client_exists(n_client):
    return n_client in gl_clients

def nickname_exists(n_nick):
    return n_nick in gl_nicknames

def new_client(n_client, n_nick):
    if not (client_exists(n_client) or nickname_exists(n_nick)):
        gl_clients.append(n_client)
        gl_nicknames.append(n_nick)
        return True
    return False
