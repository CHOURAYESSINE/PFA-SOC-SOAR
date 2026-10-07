# Validation de publication — 7 octobre 2026

Commande : `python tests/test_repository.py`.

| Contrôle exécuté | Résultat |
|---|---|
| Lecture des fichiers JSON | Réussi |
| Identifiants et branches du workflow | Réussi |
| Transmission HTTP du relais vers un serveur local de test | Réussi |
| Conservation du contenu JSON transmis | Réussi |
| Rejet d'un message JSON invalide sans transmission | Réussi |
| Compilation syntaxique du relais Python | Réussi |

Trois cas de test automatisés ont réussi. Le serveur destinataire de ce test est local : ce résultat ne valide pas Shuffle, pfSense ou PostgreSQL.

## Laboratoire

Les VM pfSense, Snort et shuffle_grafana ont été démarrées. VMware Tools ne répondait pas dans les deux VM Ubuntu. Les anciennes adresses Shuffle et Grafana étaient inaccessibles depuis Windows. Les imports des modèles, la validation Snort et la chaîne complète restent non vérifiés, en attente d'accès aux sessions Linux et des adresses actuelles.

Les fichiers comportant CONFIGURE_* sont des modèles à paramétrer, pas des configurations prêtes à exécuter. Aucun résultat historique n'est présenté comme une nouvelle validation.

## Réseau rétabli et services vérifiés

L'adaptateur VMware VMnet8 a été réinstallé via l'outil VMware vnetlib64 après sauvegarde des fichiers de configuration réseau. Son état est Up. Les adaptateurs VMnet1 et VMnet2 restent absents ; ils n'ont pas été réinitialisés.

Contrôles réalisés après réparation :

- Shuffle : HTTP 200 sur l'interface du laboratoire.
- Grafana : endpoint de santé accessible, database=ok.
- Grafana : accès authentifié aux deux sources PostgreSQL.
- PostgreSQL : requête de lecture `SELECT count(*) FROM public.incidents` réussie via chacune des deux sources, avec 16 incidents existants.
- Les trois tests automatisés du dépôt réussissent encore après ajout des définitions VMware.

Ces résultats valident le retour de l'accès réseau Windows vers Shuffle/Grafana et la lecture PostgreSQL. Ils ne valident pas une nouvelle attaque, la capture Snort, l'exécution du workflow ou un nouveau blocage pfSense. VMware Tools reste indisponible dans les VM Ubuntu ; l'accès aux sessions Linux est encore nécessaire pour ces vérifications et pour tester les imports des modèles anonymisés.
