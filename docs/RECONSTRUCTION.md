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

## Reconstruction complète et entrée Internet publique — 8 octobre 2026

Une installation indépendante fonctionne sur le VPS OVH, dans `/home/ubuntu/pfa-rebuild`. Aucun disque de sauvegarde du laboratoire existant n'a servi à cette reconstruction. Deux VM Ubuntu ont été créées depuis l'image Canonical contrôlée par SHA-256 ; pfSense CE 2.7.2 a été installé sur un disque vierge depuis l'image officielle Netgate, également contrôlée. La cible est une copie neuve de l'image officielle Metasploitable2, dont l'intégrité ZIP a été vérifiée ; il s'agit d'une image système préinstallée, pas d'une installation de Linux depuis zéro.

| Composant | Réseau isolé | Ressources VM |
|---|---|---|
| pfSense | WAN 172.30.250.2, LAN 172.30.251.2, DMZ 172.30.252.2 | 2 vCPU, 768 Mo, 8 Go |
| Shuffle, PostgreSQL, Grafana | LAN 172.30.251.10 | 2 vCPU, 3072 Mo, 24 Go |
| Snort et watcher | DMZ 172.30.252.102 | 1 vCPU, 768 Mo, 12 Go |
| Metasploitable2 | DMZ 172.30.252.100 | 1 vCPU, 256 Mo |

Les bridges QEMU `pfa-wan`, `pfa-lan`, `pfa-dmz` séparent les segments. Le trafic sortant du port DMZ de pfSense est recopié vers le capteur avec `tc mirred`. Les accès SSH des deux VM Ubuntu sont liés à localhost sur le VPS (22221 et 22222). Les mots de passe et clés sont propres à cette installation et restent hors Git.

PostgreSQL 14 utilise le schéma du dépôt. Grafana 13.0.2 a importé le dashboard avec une nouvelle datasource : les dix requêtes ont retourné HTTP 200. Shuffle a importé le modèle puis exécuté un workflow réel avec ses workers. La chaîne reconstruite comprend trois actions : PATCH de l'alias pfSense, POST d'application du pare-feu, POST vers un récepteur d'incidents PostgreSQL. Le récepteur [`fresh_incident_receiver.py`](../scripts/fresh_incident_receiver.py) contrôle un token, l'IPv4 et le SID puis utilise une requête SQL paramétrée. Son environnement et son token doivent être provisionnés localement ; il n'est pas accessible depuis Internet. Les accès REST pfSense utilisent son certificat autosigné sur le LAN isolé.

Le bootstrap [`fresh-lab-bootstrap.php`](../pfsense/fresh-lab-bootstrap.php) initialise les trois interfaces, l'alias et les règles NAT/filtrage d'une **nouvelle** installation ; il remplace les règles et ne doit pas être appliqué au pare-feu existant. Ajouter ensuite la règle DMZ autorisant uniquement Snort vers Shuffle TCP/3001, installer le paquet REST API 2.4.3 adapté à pfSense 2.7.2 et provisionner les identifiants. Ce fichier est un élément de reconstruction, pas un installateur complet automatisé.

Le test public a ouvert temporairement TCP/18081 sur le VPS, exclusivement pour l'adresse publique du PC. Une DNAT sans SNAT d'entrée conduit vers pfSense WAN TCP/80, puis vers la cible DMZ. Une seule requête HTTP avec une signature SQL a produit SID 1003, une exécution Shuffle FINISHED avec trois actions SUCCESS/HTTP 200, et un nouvel incident contenant la même adresse source que le PC. Le cycle observé est HTTP 200, blocage (HTTP 000/expiration), puis HTTP 200 après suppression de l'adresse dans l'alias. La redirection publique et le serveur HTTP de bootstrap ont ensuite été supprimés/arrêtés. Bagage est resté HTTP 200.

Les VM et données reconstruites sont conservées. Les conteneurs principaux ont une politique de redémarrage et le récepteur d'incidents est activé dans systemd. Le redémarrage complet du VPS et la restauration automatique des bridges/QEMU sont maintenant validés ; les unités publiées dans scripts/ovh assurent ce démarrage. Ne pas interpréter cette validation comme une exposition permanente ou un déploiement de production. Aucun nouveau courriel n'a été envoyé : la preuve Gmail demeure celle du laboratoire initial.

Preuves : [chaîne publique](preuves/fresh-public-chain-summary.json), [PostgreSQL et Grafana](preuves/fresh-data-summary.json), [premier test Shuffle](preuves/fresh-shuffle-summary.json). Les champs `full_lab_reconstruction: false` des deux derniers résumés décrivent leur étape individuelle antérieure ; la preuve de chaîne publique complète ces contrôles.

Sources des systèmes : [Canonical](https://cloud-images.ubuntu.com/releases/jammy/release-20261004/), [Netgate](https://atxfiles.netgate.com/mirror/downloads/), [Metasploitable2 officiel](https://sourceforge.net/projects/metasploitable/files/Metasploitable2/), [REST API pfSense](https://pfrest.org/INSTALL_AND_CONFIG/).
## Vérification finale du redémarrage — 8 octobre 2026

Trois redémarrages réels du VPS ont permis de détecter puis corriger les permissions KVM non persistantes et l'adresse Swarm initialement liée à un conteneur. Les deux VM Ubuntu avaient aussi des routes temporaires : elles ont été remplacées par Netplan. Les unités systemd attendent le réseau ; le récepteur PostgreSQL reprend son démarrage si Docker n'est pas encore prêt. Le coordinateur Orborus est relancé par l'unité de stack. Docker Swarm annonce désormais l'adresse fixe `172.30.251.10`, conformément à la [méthode de configuration Shuffle](https://github.com/Shuffle/shuffle-docs/blob/master/docs/troubleshooting.md).

Au dernier redémarrage, les quatre VM, les trois bridges, le miroir de trafic et les composants sont revenus automatiquement. Bagage est revenu HTTP 200. Les deux incidents antérieurs, le workflow et le dashboard étaient conservés. Les dix requêtes Grafana ont réussi. Une nouvelle requête publique bornée a ensuite produit SID 1003, trois actions Shuffle SUCCESS/HTTP 200 et l'incident n° 3 : total PostgreSQL 2 → 3. Le cycle HTTP 200 → blocage/expiration → HTTP 200 a été reproduit. L'horodatage de la nouvelle alerte est postérieur au démarrage de l'hôte et sa source correspond à celle du PC. Le port temporaire est fermé et le laboratoire reste démarré. Aucun nouveau courriel n'a été envoyé.

Preuves finales : [hôte et réseaux](preuves/reboot-host-summary.json), [composants, données et Grafana](preuves/reboot-component-health.json), [chaîne publique après redémarrage](preuves/reboot-public-chain-summary.json). Les scripts et unités sont dans [scripts/ovh](../scripts/ovh/README.md). Ils gèrent les systèmes déjà reconstruits ; ils ne constituent pas une installation complète sans intervention depuis des disques vierges. La phase d'initialisation des applications prend quelques minutes : un processus QEMU actif ne suffit pas à déclarer Shuffle disponible.
