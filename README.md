# Streapy
Python streaming server and client using the python web framework Snakelets - the holy grail of 2007!

## Installation
Es muss eine aktuelle Python-Installation (Python2.5) vorhanden sein.
Außerdem müssen die Module Crypto, wxPython und sqlite3 installiert sein!

- Eine Konsole öffnen
- Die Datei streapy.tar.gz entpacken (z.B. /home/user/)
- In das Verzeichnis /home/user/streapy wechseln
- Die streapy.py ausführbar machen
- /.streapy.py ausführen
-> Sollte der Server nicht starten, sollten zuerst die unteren Schritte ausgeführt werden und vor dem nächsten Versuch die Server-Konfiguration im WebInterface angepasst werden.
-> Zum Beenden des Server muss das ./stopserver.py Script im selben Verzeicheis ausgeführt werden.
- Nun läuft der Streaming-Server
- Mit einer neuen Konsole in das Unterverzeichnis snakelets_webserver/Snakelets-1.44 wechseln und python serv.py ausführen.
- Das WebApp zur Konfiguration sollte nun laufen
- Für den Client in das Unterverzeichnis client/ wechseln und python client.py ausführen
- WICHTIG: Die Programme MÜSSEN jeweils aus diesen Verzeichnissen gestartet werden, damit die Module korrekt geladen werden.

## Benutzung

Der Standardbenutzer:
User: admin
PW: test

Zuerst sollte man im WebInterface Einstellungen am Server vornehmen:
	- Wenn der Server nur lokal eingesetzt werden soll, kann die IP auf 127.0.0.1 belassen werden
	- Den Port kann man nach belieben anpassen, er sollte aber immer größer als 1024 sein!
	- Auch die Verbindungen- und Banbreiten-Einstellung muss ersteinmal nicht verändert werden
	- Das DocRoot sollte unbedingt angepasst werden. Es auf / zu belassen ist RISIKOREICH!
		- Stellen Sie sicher, dass der Server Leserechte auf das DocRoot hat
	- Sollte der Server bereits laufen, muss er nun über den Menüpunkt "Server neustarten" neugestartet werden

Nun kann man weitere Benutzer oder zuerst Gruppen und Freigaben anlegen. 
Durch das Bearbeiten der einzelnen Punkte können je nach Belieben Rechte gegeben und entzogen werden.
Die Freigaben müssen als Unterordner im DocRoot existieren, sie sind NICHT virtuell!

Möchte man dem Server Medien hinzufügen, so reicht es die Dateien in das DocRoot oder andere Freigaben zu kopieren.
Danach müssen die Freigaben über das WebInterface erneuert werden. ("Freigaben erneuern")

## Client

Nachdem der Client gestartet wurde muss man die Verbindungsdaten zum Server angeben und einen externen Mediaplayer angeben.
Wenn man den richtigen Benutzer angegeben hat und die Passwörter übereinstimmen, werden die freigegebenen Ordner und Dateien angezeigt.
Klickt man nun doppelt auf einen Dateinamen, öffnet sich diese in dem angegeben Player.
