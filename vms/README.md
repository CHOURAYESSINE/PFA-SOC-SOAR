# Machines virtuelles VMware

Les fichiers VMX sont des définitions anonymisées issues de la sauvegarde locale G:\backup_final. Ils conservent les ressources, les contrôleurs et les segments réseau du laboratoire. Les UUID, adresses MAC et chemins personnels ont été retirés. VMware pourra générer de nouveaux identifiants.

## Réutiliser les sauvegardes

1. Cloner ce dépôt.
2. Copier chaque disque VMDK depuis sa sauvegarde locale dans le dossier VM correspondant, à côté du fichier VMX. Le manifeste indique les noms et tailles attendus.
3. Ouvrir le VMX dans VMware et vérifier les chemins de disque, les segments privés et les interfaces avant démarrage.
4. Pour les périphériques CD ou disquette non fournis, déconnecter le périphérique dans VMware.
5. Vérifier la capture du trafic et appliquer le guide de reconstruction.

Les VMDK ne sont pas présents sur GitHub. Les définitions ne suffisent pas à démarrer sans les disques. Les sauvegardes contiennent des systèmes configurés et peuvent inclure des secrets : ne pas les rendre publiques sans nettoyage. Aucun lien externe de téléchargement n'est créé dans ce dépôt.
