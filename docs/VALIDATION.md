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

## Vérification des requêtes du dashboard

Les dix requêtes SQL du dashboard publié ont été exécutées contre la source PostgreSQL du laboratoire via l'API Grafana. Toutes ont retourné un statut 200 sans erreur : total des incidents, IP uniques bloquées, dernière alerte, alertes High, chronologie, types d'attaques, IP sources, incidents récents, actions et sévérités. Le test couvre une période d'un an et les données existantes. Il ne prouve pas l'arrivée d'une nouvelle alerte.

L'accès invité VMware reste refusé sans authentification Linux, et VMware Tools ne fournit pas les adresses. Le test de détection Snort et de blocage automatique demeure en attente d'une session Linux accessible.

## Réparation du watcher et détection réelle

La configuration Snort a été validée dans la VM (Snort 2.9.15.1). Après remise en marche du réseau et redémarrage, Snort et snort-shuffle-watcher sont actifs. Le watcher du laboratoire a été sauvegardé puis corrigé pour transmettre directement vers le webhook Shuffle sur son interface DMZ. Le frontend Shuffle répond HTTP 200 depuis Snort.

Un test ICMP réel a produit de nouvelles alertes dans le journal Snort. Les adresses des composants du laboratoire sont désormais exclues du blocage dans le watcher actif. Le test a confirmé trois entrées de journal « ignored infrastructure » pour la source du capteur : aucune transmission de ces alertes ne doit être interprétée comme un blocage validé.

Le script public utilise PROTECTED_IPS (liste séparée par espaces) pour configurer ces exclusions sans imposer le plan d'adressage privé. Nettoyer également la liste blocked_ips.txt existante avant remise en service. La réception effective du webhook, l'enregistrement d'un nouvel incident et le blocage d'une machine de test distincte restent à vérifier.

## Tentative de validation de l'orchestration

L'ancien workflow est présent dans la liste mais son chargement individuel renvoie HTTP 400 (« Failed finding workflow »). Les tentatives de modification ont été refusées ; aucune suspension de Gmail n'a été appliquée à ce workflow. Une copie distincte « Validation SOC sans notification » a été créée avec trois actions HTTP et sans action Gmail. Cette copie se charge correctement.

Un événement synthétique utilisant une IP réservée à la documentation a été soumis à cette copie en conservant les entrées existantes de l'alias. Shuffle a accepté l'exécution, mais celle-ci est restée EXECUTING avec zéro résultat d'action. Une lecture ultérieure de l'alias pfSense a confirmé que l'IP de test n'y figurait pas. L'exécution en attente a ensuite été annulée.

Ce test révèle un problème d'exécution Shuffle à diagnostiquer dans les conteneurs/workers. Il ne valide ni un nouveau blocage ni un nouvel enregistrement PostgreSQL. L'accès Linux à shuffle_grafana est nécessaire pour consulter les conteneurs et leurs journaux. La copie de test est conservée pour reprendre la validation après réparation.
