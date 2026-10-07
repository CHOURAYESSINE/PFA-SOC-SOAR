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
