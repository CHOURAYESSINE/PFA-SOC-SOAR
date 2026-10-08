# Essai de restauration isolée Metasploitable2 — 8 octobre 2026

- Source : sauvegarde indépendante Metasploitable-cl1.vmdk, non utilisée par la cible active.
- Contrôle VMware avant copie : Disk chain is consistent.
- Copie locale dans un dossier de validation séparé ; aucune modification du disque de production.
- Configuration issue du modèle public, carte réseau désactivée (ethernet0.present = FALSE).
- Démarrage VMware réussi ; la copie apparaît dans la liste des VM en fonctionnement et son disque est lu par le contrôleur SCSI.
- L'accès à l'invité et la capture de console n'ont pas abouti : le démarrage complet du système et ses services ne sont donc pas attestés.
- Copie de test arrêtée ; contrôle du disque après l'essai : Disk chain is consistent.

Ce résultat valide la cohérence du disque et son ouverture par VMware. Il ne valide ni une reconstruction sur système vierge ni le fonctionnement applicatif de la copie restaurée. La cible Metasploitable2 de production reste distincte.