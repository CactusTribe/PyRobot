import socket

hote = ''
port = 12800

serveur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur_socket.bind((hote, port))
serveur_socket.listen(5)
print("Le serveur écoute à présent sur le port {}".format(port))

client_socket, infos_connexion = serveur_socket.accept()

msg_recu = b""
while msg_recu != b"fin":
    msg_recu = client_socket.recv(1024)
    recu_utf8 = msg_recu.decode()
    print(recu_utf8)
    client_socket.send(b""+recu_utf8+"")

print("Fermeture de la connexion")
client_socket.close()
serveur_socket.close()