# État actuel des validations — 8 octobre 2026

| Vérification | État |
|---|---|
| Tests automatisés du dépôt | 3 réussis |
| Règles Snort publiques, PCAP synthétique isolé | 15 SID sur 15 observés ; cas témoin sans alerte |
| Détection réelle des règles sur LAN → DMZ | 15 SID sur 15 observés avec trafic borné ; signatures et seuils, sans compromission |
| Scan Nmap réel et réponse automatique | Deux exécutions réussies, +2 incidents, blocage puis rétablissement |
| Détection et réponse réelle LAN → DMZ | Validées : HTTP 200 → blocage → HTTP 200 après nettoyage |
| Détection SQL et réponse réelle WAN privé → DMZ | Validées : alerte, workflow, blocage et nouvel incident |
| Lecture PostgreSQL et 10 requêtes Grafana | Validées |
| Import dashboard Grafana et structure Shuffle | Validé ; modèle Shuffle encore à paramétrer sur une nouvelle instance |
| Schéma SQL dans une structure neuve temporaire | Création, insertion et lecture validées, transaction annulée |
| Gmail | Envoi Google HTTP 200 ; exactement un courriel de test trouvé dans les éléments envoyés |
| Route Internet de Shuffle | Service enabled et active ; retour automatique confirmé après redémarrage de shuffle_grafana |
| Fonctionnement après redémarrage Snort et Shuffle | Services, route et chaîne de blocage validés |
| Sauvegardes VM | 4 disques et références contrôlés ; 3 chaînes VMDK cohérentes, cible active verrouillée |
| Restauration isolée Metasploitable2 | Démarrage, connexion et réponse web locale confirmés ; sauvegarde préconfigurée |
| Internet public entrant vers le laboratoire | Non testé ; le WAN validé est un réseau privé |
| Reconstruction complète sur des VM vierges | Non testée ; les imports de composants ne constituent pas cette validation |

Les preuves et méthodes figurent dans [VALIDATION.md](VALIDATION.md) et [preuves/](preuves/). Les anciennes sections de VALIDATION.md décrivent les problèmes rencontrés avant leur réparation ; elles ne représentent pas l'état final.

Les configurations VM sont publiées. Les disques, mots de passe et jetons restent locaux. Une installation sur un autre PC nécessite les disques ou l'installation des systèmes et le paramétrage décrit dans [IMPORT.md](IMPORT.md) et [RECONSTRUCTION.md](RECONSTRUCTION.md).
Voir [les scénarios du rapport et leur portée exacte](SCENARIOS-PFA.md). L'accès public et la reconstruction sur systèmes vierges sont des vérifications supplémentaires, distinctes des scénarios du rapport.
