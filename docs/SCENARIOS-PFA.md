# Validation des scénarios du rapport PFA — 8 octobre 2026

Le rapport décrit une plateforme SOC/SOAR en environnement virtualisé contrôlé : détection Snort, automatisation Shuffle, blocage pfSense, stockage PostgreSQL et visualisation Grafana. Il décrit une adresse WAN privée attaquée depuis le réseau domestique. Il ne fait pas de la publication sur Internet ni d'une réinstallation sur systèmes vierges une condition de réussite de ces scénarios.

## Détection réelle des 15 règles

Le trafic est généré depuis Kali 10.1.1.107 vers Metasploitable2 10.1.2.100 à travers pfSense, sur les deux segments LAN/DMZ. Pendant cette couverture, le watcher est arrêté puis remis en service : la mesure porte sur la détection, pas sur 15 exécutions de réponse ni sur des notifications email.

| Scénario | Stimulus borné | SID observés |
|---|---|---|
| Scan SYN Nmap | 100 ports, débit maximum 100 paquets/s, une seule cible | 1001020, 1001 |
| ICMP | 20 requêtes espacées de 0,1 s | 100001, 1000002, 1001010 |
| Seuil FTP/SSH/Telnet | 8/8/5 connexions TCP | 1001030, 1001031, 1002 |
| Seuil HTTP | 40 connexions TCP | 1001040 |
| Motifs SQL | OR encodé, OR simple et UNION SELECT | 1003, 1001041, 1004 |
| Signature sqlmap | User-Agent contenant sqlmap | 1005 |
| Signature XSS | Paramètre contenant `<script>` | 1001042 |
| Signature commande | Paramètre contenant `/bin/sh` | 1001043 |

Les six requêtes web renvoient HTTP 200. Les 15 SID apparaissent dans les nouvelles alertes capturées, séparées des historiques. Les connexions répétées vérifient les seuils TCP des règles dites « brute force » : elles ne testent aucun mot de passe. Le test sqlmap utilise sa signature, sans lancer l'outil sqlmap. XSS et injection de commande sont des motifs de détection, sans preuve d'exploitation ou d'exécution sur la cible.

Preuves : [trafic généré](preuves/pfa-live-families-result.txt), [alertes nouvelles](preuves/pfa-live-families-alerts.txt). Le générateur limité aux connexions et requêtes web figure dans tests/generate_live_signature_traffic.py ; le scan et l'ICMP ont été lancés séparément dans Kali.

## Réponse automatique à un scan Nmap réel

Un deuxième scan a été effectué avec le watcher actif et l'action Gmail temporairement retirée afin de respecter l'autorisation d'un seul courriel de test déjà envoyé.

- Avant : HTTP 200.
- Deux exécutions observées : FINISHED, trois actions SUCCESS chacune.
- Incidents pour la source : 4 avant, 6 après (+2).
- Après détection : HTTP 000, expiration curl 28.
- Après nettoyage de l'alias et de l'état de test : HTTP 200, curl 0.
- Workflow original restauré, y compris son action Gmail.

Preuves : [résumé de la chaîne](preuves/nmap-chain-summary.json), [scan](preuves/nmap-chain-pfa-kali-nmap-trigger.txt), [blocage](preuves/nmap-chain-pfa-kali-after.txt), [rétablissement](preuves/nmap-chain-pfa-kali-restored.txt).

## Vérifications supplémentaires distinctes

Le test Internet public entrant reste non réalisé : le modem USB valide une sortie Internet, sans fournir un point d'entrée public redirigé vers pfSense. La reconstruction complète sur systèmes vierges reste non réalisée ; seules les importations des composants et la restauration isolée de Metasploitable2 ont été vérifiées. Ces limites ne doivent pas être confondues avec les scénarios fonctionnels validés ci-dessus.