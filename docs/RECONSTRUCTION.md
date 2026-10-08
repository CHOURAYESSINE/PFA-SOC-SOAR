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
6. Si le relais optionnel est utilisé, définir SHUFFLE_WEBHOOK_URL sur le poste relais. Le relais écoute par défaut sur 127.0.0.1 ; définir RELAY_BIND sur l'adresse du laboratoire si le capteur est distant et limiter l'accès par pare-feu. Lancer `python scripts/snort_shuffle_relay.py`.
7. Recréer/importer le workflow Shuffle : webhook, extraction de l'IP, mise à jour de BLOCKED_IPS, application du filtrage et enregistrement de l'incident. Configurer les authentifications dans Shuffle, jamais dans Git.
8. Configurer PostgreSQL et sa source de données Grafana. Recréer/importer le dashboard des incidents. Consulter docs/IMPORT.md pour les fichiers fournis et la reconfiguration des sources de données.
9. Dans le laboratoire autorisé, vérifier la chaîne : alerte Snort, réception Shuffle, mise à jour de l'alias, blocage effectif, incident enregistré et affichage Grafana. Conserver les résultats horodatés sans secrets.

## Exports à ajouter

Exporter le workflow depuis Shuffle, le dashboard JSON depuis Grafana, la configuration pfSense et le schéma PostgreSQL depuis leurs interfaces. Retirer tous les mots de passe, tokens, clés privées, données personnelles et identifiants de webhook. Les fichiers VMware fournis à GitHub doivent être des modèles anonymisés, pas des sauvegardes complètes.


## Scénario WAN privé reproduit

Le test validé utilise une interface supplémentaire bridgée dans Kali, sur le même segment Ethernet que le WAN de pfSense. L'adresse de test est 192.168.1.200/24 ; le WAN existant est 192.168.1.34. Vérifier que cette adresse est libre avant réutilisation et adapter les adresses à votre laboratoire. L'interface LAN de Kali reste séparée. NetworkManager ne doit pas retirer l'adresse de test pendant le scénario. La redirection TCP/80 mène à la cible DMZ 10.1.2.100.

Les résultats de détection, blocage et retour à HTTP 200 après nettoyage sont détaillés dans VALIDATION.md. Ne pas confondre cette entrée WAN privée avec une exposition sur Internet public.
## Reconstruction du capteur sur une VM neuve — 8 octobre 2026

Une VM KVM séparée a été créée sur OVH depuis l'image officielle Ubuntu 22.04.5 LTS publiée le 4 octobre 2026. Son SHA-256 a été comparé au manifeste officiel. Aucun disque de sauvegarde ni configuration privée du capteur existant n'a été importé. Ressources : 2 vCPU, 1536 Mo, disque qcow2 de 12 Go ; SSH lié exclusivement à 127.0.0.1:22221 sur l'hôte. La VM a été arrêtée après validation, ses fichiers sont conservés dans /home/ubuntu/pfa-rebuild sur le VPS.

Snort 2.9.15.1 a été installé depuis les paquets Ubuntu. La configuration minimale et les règles viennent du dépôt. Validation snort -T réussie ; 15 SID sur 15 observés à la lecture du PCAP synthétique ; aucun événement pour la source témoin 10.1.1.90. Les checksums sont désactivés uniquement pour ce PCAP artificiel. Bagage répond toujours HTTP 200 après arrêt de la VM.

Cette preuve couvre une reconstruction neuve du capteur ; elle ne remplace pas une reconstruction complète pfSense + Shuffle/PostgreSQL/Grafana + cible. Le test de la chaîne opérationnelle demeure celui du laboratoire existant.

Preuves : [résumé](preuves/fresh-snort-summary.json), [sortie Snort et OS](preuves/fresh-snort-proof.txt). Scripts : scripts/create_fresh_snort_vm.sh et scripts/validate_fresh_snort_vm.sh. Ils sont spécifiques à un hôte Ubuntu avec KVM et utilisent /home/ubuntu/pfa-rebuild ; le premier installe les outils QEMU et refuse d'écraser un disque déjà présent.

Sources : [image Canonical](https://cloud-images.ubuntu.com/releases/jammy/release-20261004/), [paquet Snort Ubuntu](https://packages.ubuntu.com/jammy/snort).
