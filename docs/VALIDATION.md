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

## Validation après réparation OpenSearch

Les alias OpenSearch nécessaires ont été corrigés après sauvegarde des documents et contrôle du nombre d'identifiants uniques. Les index d'origine sont conservés. Le workflow original se charge désormais en HTTP 200.

Une branche provenant d'un déclencheur absent a été retirée de la copie de validation sans Gmail. La nouvelle exécution a terminé en FINISHED : mise à jour de l'alias pfSense, application du filtrage et insertion PostgreSQL toutes SUCCESS avec HTTP 200. Une lecture de l'alias a confirmé la présence de l'IP réservée au test. Une lecture PostgreSQL a confirmé un nouvel incident correspondant à cet événement synthétique.

L'IP de test a ensuite été retirée de l'alias, avec réapplication du filtrage en HTTP 200 et vérification de son absence. Les anciennes entrées sont conservées, ainsi que l'incident de validation. Aucune action Gmail n'était présente dans la copie testée.

La détection ICMP réelle dans Snort et l'orchestration synthétique ont été vérifiées séparément. Ce résultat ne prouve pas une attaque distante suivie d'un blocage effectif du trafic. L'import des modèles dans une instance vierge reste également non validé.

## Validation réelle de la chaîne — 8 octobre 2026

Le scénario utilise Kali (10.1.1.107) sur le LAN privé de pfSense et Metasploitable (10.1.2.100) dans la DMZ. L'interface de test Kali a été raccordée au segment LAN VMware et une route vers la DMZ a été ajoutée.

| Étape | Résultat observé |
|---|---|
| Accès HTTP initial à Metasploitable depuis Kali | HTTP 200 |
| Trafic ICMP de Kali vers Metasploitable | Nouvelles alertes Snort, SID 1000002 et 100001 |
| Exécution du workflow original, sans Gmail pendant le test | Deux exécutions FINISHED ; les trois actions HTTP sont SUCCESS |
| Mise à jour et application du filtrage pfSense | IP de Kali présente dans BLOCKED_IPS |
| Nouvelle connexion HTTP après blocage | HTTP 000, code curl 28 : expiration du délai |
| Lecture PostgreSQL par Grafana | Deux nouveaux incidents pour la source Kali dans les 15 dernières minutes |
| Nettoyage et nouvelle connexion HTTP | Alias initial restauré, HTTP 200, code curl 0 |

L'action Gmail et ses branches ont été temporairement retirées du workflow original pour ce test, puis restaurées. Aucun courriel de test n'a été envoyé. L'IP Kali a également été retirée du fichier de déduplication du watcher. Les anciennes entrées de l'alias ont été conservées.

Les sorties réellement recueillies sont conservées dans [preuves](preuves/). Les horodatages des journaux reflètent l'horloge de la VM, différente de celle du poste hôte ; ils n'ont pas été réécrits.

Le script watcher publié passe `bash -n`. Les règles Snort publiées ont été chargées dans une copie temporaire de la configuration de la VM : Snort 2.9.15.1 a confirmé « Snort successfully validated the configuration! ». Les trois tests automatisés du dépôt passent également.

Ce test valide le scénario LAN → DMZ du laboratoire et son blocage effectif. Il ne valide pas un scénario WAN/Internet, toutes les règles d'attaque, ni l'installation des modèles sur une instance vierge. Les modèles nécessitent toujours la configuration décrite dans IMPORT.md.
## Contrôles complémentaires — 8 octobre 2026

- **Services actuels** : Snort et le watcher répondent active ; le workflow original est lisible avec ses quatre actions et Grafana annonce database=ok.
- **Couverture des règles** : les 15 SID du fichier public local.rules ont été observés dans les alertes d'une instance Snort isolée, alimentée par un PCAP synthétique. Les cas couvrent ICMP, seuils ICMP/SYN/FTP/SSH/Telnet/HTTP, motifs SQL, SQLmap, XSS et commande shell. Voir preuves/snort-all-rules-alerts.txt et tests/generate_snort_rule_cases.py. Un cas témoin HTTP sans motif d'attaque, envoyé avec ACK depuis une source distincte, produit zéro alerte. Les dates du PCAP sont fixes. Ce test utilise -k none car les paquets générés n'ont pas de sommes de contrôle ; il teste les règles sans injecter ces paquets sur le réseau et sans transmettre leurs alertes au watcher. Il ne prouve pas une exploitation ni un blocage pour chaque attaque.
- **Schéma SQL sur structure neuve** : création d'un schéma temporaire, application du SQL publié, insertion d'un incident et lecture du compteur = 1. La transaction a été annulée par ROLLBACK, sans changer public.incidents.
- **Import Grafana** : copie du dashboard public importée avec un UID temporaire, statut success ; relecture de ses dix panneaux réussie. Seule cette copie a ensuite été supprimée. Les dix requêtes avaient déjà été exécutées avec succès dans le laboratoire.
- **Import Shuffle** : modèle public importé et relu avec quatre actions et un déclencheur arrêté. La copie est conservée sous le nom « PFA public template import validation - stopped ». Aucun endpoint ni identifiant n'a été ajouté et aucune exécution n'a été lancée. Cela valide l'import de la structure, pas l'exécution du modèle non paramétré.
- **Politique WAN** : lecture API réussie ; le blocage BLOCKED_IPS précède les autorisations WAN et une redirection WAN TCP/80 vers la cible DMZ existe. Le test HTTP vers 192.168.1.34 expire ; le poste hôte n'a aucune adresse sur ce réseau. Le test WAN réel reste non validé, en attente de connectivité. Ce réseau WAN privé ne constitue pas un test Internet.

Une reconstruction complète sur des VM vierges reste distincte des imports ci-dessus : elle nécessite les systèmes, applications, authentifications et interfaces décrits dans IMPORT.md et RECONSTRUCTION.md. Les notifications Gmail n'ont pas été testées par envoi.
## Validation WAN → DMZ — 8 octobre 2026

Le blocage de connectivité a été contourné en ajoutant une troisième interface bridgée à Kali, sans modifier pfSense. L'IP de test 192.168.1.200/24 permet de joindre le WAN privé 192.168.1.34 au niveau Ethernet malgré le sous-réseau différent du poste Windows. NetworkManager supprimait initialement cette adresse manuelle : l'interface de test a donc été temporairement placée hors de sa gestion. Les premiers délais d'expiration n'étaient pas des preuves de blocage.

Le scénario stabilisé a donné les résultats suivants :

| Contrôle | Résultat |
|---|---|
| HTTP vers le WAN, redirigé vers Metasploitable | 200 |
| Requête avec le motif or+1%3D1 | Alerte Snort SID 1003, source 192.168.1.200, cible 10.1.2.100:80 |
| Workflow original sans Gmail pendant le test | FINISHED, trois actions SUCCESS |
| Alias pfSense | Source de test présente dans BLOCKED_IPS |
| PostgreSQL | Un nouvel incident pour cette source dans les 15 dernières minutes |
| Nouvelle connexion HTTP après filtrage | 000, code curl 28 |
| Après restauration de l'alias initial | HTTP 200, code curl 0 |

L'entrée de déduplication de la source a été nettoyée et l'action Gmail du workflow a été restaurée. Aucun courriel n'a été envoyé. Voir preuves/wan-validation.json et les sorties pfa-wan-*.txt. Le cas qui était en attente est désormais validé pour le WAN privé du laboratoire ; il ne constitue pas un test depuis Internet public.
## Validation Gmail autorisée — 8 octobre 2026

Une copie distincte du workflow, sans déclencheur et avec uniquement l'action Gmail, a été créée pour adresser un courriel unique de test à l'adresse autorisée. Une seule exécution a été lancée. Le workflow de réponse réseau original n'a pas été modifié.

L'exécution a terminé avec une réponse applicative success=false : délai d'attente de 300 secondes. Le statut d'action SUCCESS affiché par Shuffle ne constitue donc pas une preuve d'envoi.

Diagnostic et réparation : la route par défaut de shuffle_grafana privilégiait pfSense et une ancienne passerelle WAN. Une route de priorité supérieure via le NAT VMware existant a été ajoutée après sauvegarde des routes. Les endpoints HTTPS Gmail et OAuth répondent désormais (404 attendu sur leur racine), ce qui valide DNS et accès HTTPS. Cette route ajoutée est active en mémoire ; sa persistance après redémarrage n'a pas été configurée.

La première vérification directe ne permettait pas de conclure : Shuffle masque les secrets retournés par son API d'administration. Une seconde vérification a été exécutée à travers l'application Gmail de Shuffle, avec l'authentification enregistrée et une recherche limitée au courriel de test autorisé. Cette action de lecture a terminé avec HTTP 401, UNAUTHENTICATED / invalid_token, dans la réponse réelle de Google. L'authentification doit donc être reconnectée dans Shuffle. Aucun envoi réussi ni réception n'est annoncé. Aucune nouvelle exécution d'envoi n'a été lancée pour éviter un doublon. Le test attend la reconnexion du compte.

Après la reprise utilisateur, aucune nouvelle authentification Gmail utilisable n'a été constatée. Le formulaire Authenticate Gmail a été ouvert : Client ID et Client Secret sont requis, et le bouton Authenticate reste désactivé tant qu'ils ne sont pas renseignés. Le test de lecture ne renvoie aucun contenu de courriel, seulement l'erreur d'authentification. Aucun second envoi n'a été lancé.

## Gmail réparé et envoi vérifié — 8 octobre 2026

Après réparation de l'accès Internet de shuffle_grafana, les anciennes connexions disposant d'un renouvellement OAuth ont été testées par une recherche ciblée du courriel de validation, sans envoi. L'une d'elles a répondu HTTP 200 avec zéro message correspondant. Elle a été sélectionnée dans le workflow de test à une seule action.

Le courriel unique autorisé a ensuite été envoyé : workflow FINISHED, action SUCCESS et réponse Google HTTP 200 avec id, threadId et labelIds. Une nouvelle recherche ciblée dans les éléments envoyés a répondu HTTP 200 et trouvé exactement un message correspondant. L'envoi est donc confirmé ; la réception dans la boîte du destinataire n'a pas été consultée. Il y a eu deux tentatives au total, dont la première avait expiré avant réparation, et un seul message de test confirmé.

La même authentification fonctionnelle a été sélectionnée pour l'action Gmail du workflow original après sauvegarde de celui-ci. Ses quatre actions, branches, paramètres et destinataires existants ont été conservés. Le workflow original n'a pas été exécuté pour cette modification.

La correction de route est désormais installée comme service systemd pfa-internet-route, enabled et active. L'accès HTTPS Google répond après activation. Le redémarrage complet de la VM n'a pas été testé. Le modèle du service est publié dans systemd/ ; adapter la passerelle et l'interface avant utilisation sur un autre poste. Les identifiants OAuth, secrets et journaux privés restent hors du dépôt.
## Fonctionnement après redémarrage vérifié — 8 octobre 2026

Les VM Snort et shuffle_grafana ont été redémarrées proprement. Le changement de leur boot_id a été vérifié. Snort et le watcher sont revenus active, avec l'adresse du capteur conservée.

Le premier démarrage de shuffle_grafana a révélé un retard provoqué par la reconnexion DHCP d'une ancienne interface ens34, sans serveur DHCP accessible. Après sauvegarde des profils NetworkManager, son profil a été placé en autoconnect=no. Les interfaces LAN/DMZ/NAT utiles ont été conservées. Un second redémarrage complet de shuffle_grafana a confirmé le retour automatique de Docker, Grafana, du service de route et des cinq conteneurs actifs. La route NAT de priorité 50 est présente et Google répond en HTTPS. Grafana annonce database=ok.

La chaîne WAN privée a ensuite été rejouée : HTTP 200 initial, nouvelle alerte SQL SID 1003, exécution FINISHED avec trois actions SUCCESS, blocage HTTP 000/code curl 28 et compteur PostgreSQL passé de 1 à 2 pour la source de test. L'orchestration a pris plus que les cinq secondes de la première vérification : le blocage a été confirmé après la fin effective du workflow. L'alias a été restauré et l'accès est revenu à HTTP 200. Gmail a été temporairement retiré pour ce test puis restauré avec son authentification réparée ; aucun nouveau courriel n'a été envoyé.

Voir preuves/postboot-validation.json et les sorties associées. Cette validation couvre le redémarrage des deux VM applicatives critiques ; pfSense, Kali et Metasploitable n'ont pas été redémarrées dans ce scénario.

## Vérification des sauvegardes de reconstruction

Le contrôle scripts/check_vm_backups.py confirme, pour les quatre VM : présence des disques locaux, taille conforme au manifeste et référence disque VMX correspondante. Les lecteurs CD sans disque publié ont été désactivés dans les définitions publiques afin de ne pas dépendre d'un média absent.

VMware vdiskmanager -e confirme la cohérence des chaînes des sauvegardes pfSense, Shuffle/Grafana et Snort. Le disque Metasploitable est utilisé par la VM cible active : le verrou empêche ce contrôle hors ligne. La tentative d'arrêt gracieux sans VMware Tools n'a pas abouti ; seule la requête de gestion bloquée a été annulée, la VM a été conservée en fonctionnement. Ce verrou ne permet pas de conclure à une corruption.

Les contrôles de sauvegarde ne prouvent pas une réinstallation complète sur des OS vierges. Aucun ISO d'installation complet n'a été identifié dans les sauvegardes examinées ; le poste dispose d'environ 2,9 Go de RAM libre, insuffisants pour démarrer en parallèle un second laboratoire aux ressources publiées. Le test Internet public reste en attente d'une adresse publique ou d'un domaine redirigé vers pfSense.
## Essai de restauration isolée Metasploitable2 — 8 octobre 2026

Voir [la preuve et ses limites](preuves/restauration-metasploitable.md). Une copie indépendante a été ouverte par VMware sans réseau ; l'état des services invités reste à vérifier. Aucun disque de VM n'est publié.


### Restauration Metasploitable2 : vérification du service web

La console puis la capture fournie confirment le démarrage, la connexion et le contenu web local de la copie restaurée. Voir [la preuve actualisée](preuves/restauration-metasploitable.md). Le test de reconstruction complète sur systèmes vierges reste distinct.


## Nouvelle validation entre deux segments LAN

Le scénario interne a été relancé avec succès : HTTP 200, alertes Snort, trois actions réussies, deux nouveaux incidents, blocage puis HTTP 200 après nettoyage. Voir [l'architecture et les preuves](DEUX-SEGMENTS.md).


## Sortie Internet par modem USB Android — 8 octobre 2026

Windows détecte le modem Samsung USB RNDIS ; le Wi-Fi est déconnecté. Le PC répond au contrôle HTTPS Microsoft avec HTTP 200. Shuffle atteignait initialement des routes internes prioritaires et échouait en HTTPS. La route via le NAT VMware a été rétablie puis ajoutée au profil NetworkManager actif d'ens33. Après réapplication du profil, la route NAT est prioritaire et Gmail HTTPS renvoie 404 sur sa racine (réponse du serveur, pas un envoi de courriel). Docker, Grafana et le service de route sont actifs. Aucun courriel supplémentaire n'a été envoyé.

Preuve : [sortie-internet-usb-shuffle.txt](preuves/sortie-internet-usb-shuffle.txt). Cette validation porte sur la sortie Internet de Shuffle par le PC et son modem USB. Elle ne valide pas un accès public entrant ni une installation sur systèmes vierges. Le profil conserve ses adresses de laboratoire ; les deux segments LAN ne sont pas remplacés par le réseau mobile.

## Scénarios complémentaires du rapport PFA

Les 15 SID ont été observés sur trafic réel borné entre les deux segments. Un scan Nmap séparé a également validé la chaîne de réponse avec deux nouveaux incidents et un blocage effectif. Voir [méthode, preuves et limites](SCENARIOS-PFA.md).


## Test depuis le VPS OVH par tunnel SSH — 8 octobre 2026

Une requête SQL de test a été lancée depuis le VPS vers un port temporaire lié uniquement à son adresse loopback, puis transportée par SSH vers Kali et la cible DMZ à travers pfSense. Aucune cible vulnérable n'a été ouverte publiquement. Snort voit la source LAN de Kali (10.1.1.107), pas l'adresse publique du VPS : ce test valide un initiateur distant et la chaîne LAN/DMZ, pas un filtrage WAN public conservant la source Internet.

Résultats : HTTP 200 avant ; workflow FINISHED avec trois actions SUCCESS ; incidents de la source 6 → 7 ; HTTP 000 et expiration après blocage ; HTTP 200 après rétablissement. Gmail était temporairement désactivé et le workflow original a été restauré. Le tunnel, sa clé temporaire et sa route ont été retirés. Le service Bagage du VPS répond HTTP 200 avant et après le test.

Preuves : [exécution et incident](preuves/ovh-tunnel-summary.json), [requête](preuves/ovh-tunnel-trigger.txt), [blocage distant](preuves/ovh-tunnel-blocked.txt), [rétablissement et Bagage](preuves/ovh-tunnel-restored.txt).

## Reconstruction du capteur sur une VM neuve — 8 octobre 2026

Une VM KVM séparée a été créée sur OVH depuis l'image officielle Ubuntu 22.04.5 LTS publiée le 4 octobre 2026. Son SHA-256 a été comparé au manifeste officiel. Aucun disque de sauvegarde ni configuration privée du capteur existant n'a été importé. Ressources : 2 vCPU, 1536 Mo, disque qcow2 de 12 Go ; SSH lié exclusivement à 127.0.0.1:22221 sur l'hôte. La VM a été arrêtée après validation, ses fichiers sont conservés dans /home/ubuntu/pfa-rebuild sur le VPS.

Snort 2.9.15.1 a été installé depuis les paquets Ubuntu. La configuration minimale et les règles viennent du dépôt. Validation snort -T réussie ; 15 SID sur 15 observés à la lecture du PCAP synthétique ; aucun événement pour la source témoin 10.1.1.90. Les checksums sont désactivés uniquement pour ce PCAP artificiel. Bagage répond toujours HTTP 200 après arrêt de la VM.

Cette preuve couvre une reconstruction neuve du capteur ; elle ne remplace pas une reconstruction complète pfSense + Shuffle/PostgreSQL/Grafana + cible. Le test de la chaîne opérationnelle demeure celui du laboratoire existant.

Preuves : [résumé](preuves/fresh-snort-summary.json), [sortie Snort et OS](preuves/fresh-snort-proof.txt). Scripts : scripts/create_fresh_snort_vm.sh et scripts/validate_fresh_snort_vm.sh. Ils sont spécifiques à un hôte Ubuntu avec KVM et utilisent /home/ubuntu/pfa-rebuild ; le premier installe les outils QEMU et refuse d'écraser un disque déjà présent.

Sources : [image Canonical](https://cloud-images.ubuntu.com/releases/jammy/release-20261004/), [paquet Snort Ubuntu](https://packages.ubuntu.com/jammy/snort).
