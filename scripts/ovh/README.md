# Démarrage du laboratoire reconstruit sur OVH

Ces fichiers gèrent uniquement les quatre disques déjà reconstruits dans `/home/ubuntu/pfa-rebuild`. Ils ne téléchargent ni ne réinstallent les systèmes. Hôte Ubuntu, KVM, utilisateur `ubuntu`, interface externe `ens3` et Docker sont requis. Les noms de réseaux `pfa-*` sont réservés à ce laboratoire.

Installer les trois scripts dans `/home/ubuntu/pfa-rebuild` avec permission 755, ajouter `ubuntu` au groupe `kvm`, copier les trois unités systemd dans `/etc/systemd/system`, puis exécuter `systemctl daemon-reload` et `systemctl enable --now pfa-lab.target`. Faire cette adoption seulement après arrêt propre des VM déjà lancées manuellement : le script refuse de lancer deux QEMU sur le même disque.

Les réseaux et le miroir de trafic sont créés automatiquement après le démarrage de Docker sur l'hôte. Les VM utilisent des sockets QMP locaux pour leur arrêt. La cible ancienne nécessite une commande SSH de mise hors tension avant la fermeture de QEMU : ses clés restent dans `vm_meta_access`, et son mot de passe sudo dans `metasploitable-sudo-private`, tous deux hors Git avec permission 600. Aucune clé ni aucun mot de passe n'est fourni dans ces scripts.

Dans les deux VM Ubuntu, provisionner des fichiers Netplan persistants pour `ens4` et sa route vers l'autre segment via pfSense. Snort : `172.30.252.102/24`, route `172.30.251.0/24 via 172.30.252.2`. Orchestration : `172.30.251.10/24`, route `172.30.252.0/24 via 172.30.251.2`. Les unités Snort/watcher attendent `network-online.target` et redémarrent en cas de panne.

L'unité `guest/pfa-components.service` appartient à la VM d'orchestration. Elle relance la stack Compose existante et son coordinateur Orborus. Initialiser Docker Swarm dans cette VM avec une **adresse stable de la VM**, `172.30.251.10:2377`, et non une adresse de conteneur. La réinitialisation d'un Swarm existant supprime ses services éphémères : ce n'est pas une opération de démarrage ordinaire et elle ne doit jamais viser le Docker de l'hôte Bagage. Le récepteur PostgreSQL attend le réseau et Docker, avec reprises espacées de dix secondes.

`verify_components.py` vérifie le workflow existant, les données PostgreSQL et les dix requêtes Grafana sans envoyer de courriel. Il lit les identifiants depuis les fichiers privés de la VM et ne les imprime pas. Il ne remplace pas le test réel de détection/blocage, décrit dans `docs/RECONSTRUCTION.md`.

Le démarrage automatique n'ouvre aucun port public vers Metasploitable2, Shuffle, Grafana ou pfSense. Les redirections publiques de validation restent temporaires et limitées à une source explicitement autorisée. Ne pas exposer la cible vulnérable ou les interfaces d'administration.

Les empreintes des six images réellement exécutées sont conservées dans runtime-image-lock.json. Les balises de la stack existante ne sont pas mises à jour automatiquement pendant ces validations. Le script verify_host.py compare le démarrage avec pre-final-reboot-boot-id.txt, à enregistrer sur le VPS avant le redémarrage à contrôler.
