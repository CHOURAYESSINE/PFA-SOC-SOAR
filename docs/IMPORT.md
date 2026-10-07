# Import des composants

## Shuffle

`shuffle/workflow.template.json` conserve les actions et l'enchaînement du workflow sauvegardé. Toutes les valeurs des paramètres et les authentifications ont été retirées ; ce modèle n'est pas immédiatement exécutable. Importer si la version de Shuffle l'accepte, sinon recréer les actions selon le JSON. Reconfigurer les applications, le webhook et les connexions dans votre instance.

1. HTTP PATCH pfSense : mettre à jour l'alias BLOCKED_IPS à partir de `$exec.blocked_ips`.
2. HTTP POST pfSense : appliquer le filtrage après la mise à jour.
3. HTTP POST Grafana : connexion à la source PostgreSQL et enregistrement d'un incident avec les champs du schéma SQL.
4. Gmail : destinataire et authentification à configurer dans Shuffle.

Confirmer les endpoints exacts selon la version de l'API pfSense installée. Activer la vérification TLS. Pour l'insertion SQL, utiliser des paramètres liés dans l'intégration PostgreSQL ; ne pas concaténer directement les valeurs reçues du webhook.

## Grafana et PostgreSQL

Créer une base et un utilisateur avec des droits limités, puis appliquer `postgresql/schema.sql`. Ce schéma est reconstruit à partir des requêtes disponibles, pas extrait de la base active. Créer la source PostgreSQL dans Grafana. Importer `grafana/dashboard.json`, puis remplacer les références de source de données sauvegardées par l'UID de votre source locale. Vérifier chaque panneau avec un incident de test.

## pfSense

`pfsense/blocked-ips.template.json` décrit l'alias et les règles de blocage retrouvés. Il ne remplace pas un export XML complet. Recréer l'alias et placer les règles de blocage avant les règles d'autorisation. Configurer séparément les interfaces et la translation NAT de la DMZ. Ne jamais restaurer ce JSON comme un fichier config.xml.

## Limites de vérification

Les fichiers JSON ont été contrôlés pour leur syntaxe et les identifiants privés connus ont été recherchés. Les VM étaient arrêtées pendant la préparation : aucun import, démarrage de service ou test de bout en bout n'est annoncé comme validé pour ces modèles.
