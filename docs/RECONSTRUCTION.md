# Reconstruction du laboratoire

## Machines repérées dans les sauvegardes

| VM | Rôle | CPU | RAM observée |
|---|---|---:|---:|
| pfSense | Routage, NAT, alias BLOCKED_IPS | 4 | 512 Mo |
| Snort Ubuntu | Capteur IDS | 2 | 1352 Mo |
| Shuffle/Grafana Ubuntu | Orchestration et visualisation | 4 | 8192 Mo |
| Metasploitable | Cible de laboratoire | 1 | 512 Mo |

Ces ressources proviennent des fichiers VMware sauvegardés ; elles ne représentent pas une recommandation de dimensionnement. Kali est décrit dans le rapport, mais absent de cette sauvegarde.

## Réseau

Créer des segments VMware distincts pour le réseau de test, le LAN et la DMZ. Relier pfSense aux trois zones, Metasploitable et Snort à la DMZ. L'attaquant vise l'adresse exposée par pfSense ; la translation NAT mène à la cible interne. Le capteur doit effectivement recevoir le trafic (miroir de port ou autre dispositif de capture à vérifier). Une connexion au même segment ne garantit pas la capture de tout le trafic unicast.

Les sauvegardes comportent également des interfaces NAT, bridgées et host-only historiques. Vérifier leur rôle avant démarrage et garder les services vulnérables isolés du réseau domestique et d'Internet.

## Étapes

1. Créer les VM ou ouvrir les sauvegardes locales dans VMware. Ne pas publier leurs disques sur GitHub.
2. Configurer les interfaces et un plan d'adressage adapté au laboratoire.
3. Configurer pfSense : NAT vers la DMZ, alias BLOCKED_IPS et règles de blocage sur les interfaces concernées.
4. Installer Snort compatible avec les règles fournies, définir HOME_NET et inclure local.rules. Valider la configuration avec `snort -T -c /etc/snort/snort.conf` avant lancement.
5. Installer Python 3 et curl sur le capteur. Définir SNORT_RELAY_URL vers le relais et lancer le watcher avec les permissions nécessaires pour lire les alertes et écrire son état.
6. Sur le poste relais, définir SHUFFLE_WEBHOOK_URL. Le relais écoute par défaut sur 127.0.0.1 ; définir RELAY_BIND sur l'adresse du laboratoire si le capteur est distant et limiter l'accès par pare-feu. Lancer `python scripts/snort_shuffle_relay.py`.
7. Recréer/importer le workflow Shuffle : webhook, extraction de l'IP, mise à jour de BLOCKED_IPS, application du filtrage et enregistrement de l'incident. Configurer les authentifications dans Shuffle, jamais dans Git.
8. Configurer PostgreSQL et sa source de données Grafana. Recréer/importer le dashboard des incidents. Les exports exacts et le schéma SQL ne sont pas encore inclus dans ce dépôt.
9. Dans le laboratoire autorisé, vérifier la chaîne : alerte Snort, réception Shuffle, mise à jour de l'alias, blocage effectif, incident enregistré et affichage Grafana. Conserver les résultats horodatés sans secrets.

## Exports à ajouter

Exporter le workflow depuis Shuffle, le dashboard JSON depuis Grafana, la configuration pfSense et le schéma PostgreSQL depuis leurs interfaces. Retirer tous les mots de passe, tokens, clés privées, données personnelles et identifiants de webhook. Les fichiers VMware fournis à GitHub doivent être des modèles anonymisés, pas des sauvegardes complètes.
