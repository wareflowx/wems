# Guide de Tests Manuels - Wareflow EMS

## Avant de Commencer

**Prérequis**:
1. Base de données propre ou de test
2. Fichiers de test Excel disponibles dans `tests/fixtures/`
3. Python 3.10+ avec toutes les dépendances installées

**Lancement de l'application**:
```bash
cd C:\Users\dpereira\Documents\github\wareflow-ems
python -m src.main
```

---

## Test 1: Interface Globale et Navigation

### Objectif
Vérifier que l'application se lance correctement et que la navigation fonctionne.

### Scénario 1.1 - Démarrage de l'application
- [ ] L'application démarre sans erreur
- [ ] La fenêtre principale s'affiche avec le titre "Wareflow EMS"
- [ ] Les 3 onglets sont visibles : Employés, Alertes, Import
- [ ] L'onglet par défaut est "Employés"

### Scénario 1.2 - Navigation entre les vues
- [ ] Clic sur "Alertes" → La vue des alertes s'affiche
- [ ] Clic sur "Import" → La vue d'import s'affiche
- [ ] Clic sur "Employés" → Retour à la liste des employés
- [ ] La transition entre les vues est fluide

### Scénario 1.3 - Interface responsive
- [ ] Redimensionner la fenêtre → Le contenu s'adapte
- [ ] Les barres de défilement fonctionnent si nécessaire
- [ ] Le texte reste lisible

**Résultat attendu**: Tous les tests passent sans crash ni erreur visuelle

---

## Test 2: Gestion des Employés (CRUD de Base)

### Objectif
Vérifier les opérations CRUD sur les employés.

### Scénario 2.1 - Création d'un employé
1. Cliquez sur le bouton "+ Ajouter" (ou bouton "+")
2. Remplissez le formulaire :
   - **Nom**: Dupont
   - **Prénom**: Jean
   - **Email**: jean.dupont@test.com
   - **Téléphone**: 06 12 34 56 78
   - **ID externe**: TEST-001
   - **Statut**: Actif
   - **Zone de travail**: Zone A
   - **Rôle**: Cariste
   - **Type de contrat**: CDI
   - **Date d'entrée**: 15/01/2025
3. Cliquez sur "Sauvegarder"

**Vérifications**:
- [ ] L'employé apparaît dans la liste
- [ ] Les données sont correctement affichées
- [ ] Un message de succès s'affiche (console ou UI)
- [ ] Le nom complet est "Dupont Jean"

### Scénario 2.2 - Modification d'un employé
1. Sélectionnez l'employé créé dans le scénario 2.1
2. Cliquez sur "Modifier" (ou double-cliquez sur l'employé)
3. Changez le **Rôle**: Magasinier
4. Changez le **Statut**: Inactif
5. Cliquez sur "Sauvegarder"

**Vérifications**:
- [ ] Les modifications sont enregistrées
- [ ] La liste mise à jour affiche les nouvelles valeurs
- [ ] L'icône/statut visuel reflète le changement (si applicable)

### Scénario 2.3 - Suppression d'un employé
1. Créez un employé de test : TEST-002
2. Sélectionnez-le dans la liste
3. Cliquez sur "Supprimer"
4. Confirmez la suppression

**Vérifications**:
- [ ] L'employé disparaît de la liste
- [ ] Un message de confirmation s'affiche
- [ ] Le comptage du nombre d'employés est mis à jour

### Scénario 2.4 - Validation des champs
1. Cliquez sur "+ Ajouter"
2. Essayez de sauvegarder avec des champs vides

**Vérifications**:
- [ ] Les champs requis affichent une erreur
- [ ] La sauvegarde est bloquée tant que les champs requis sont vides
- [ ] Le message d'erreur est clair

---

## Test 3: Recherche et Filtrage (Fonctionnalités de Base)

### Objectif
Vérifier que la recherche et le filtrage fonctionnent correctement.

### Scénario 3.1 - Recherche par nom
1. Créez 3 employés avec des noms différents :
   - Dupont Jean
   - Martin Marie
   - Bernard Pierre
2. Dans la barre de recherche, tapez "Dupont"

**Vérifications**:
- [ ] Seul "Dupont Jean" apparaît dans les résultats
- [ ] La recherche est insensible à la casse (testez "dupont")
- [ ] La recherche par prénom fonctionne ("Jean")

### Scénario 3.2 - Recherche partielle
1. Tapez "Mar" dans la recherche

**Vérifications**:
- [ ] "Martin Marie" apparaît dans les résultats
- [ ] Les autres employés n'apparaissent pas

### Scénario 3.3 - Liste vide
1. Tapez "xyzw" dans la recherche (nom inexistant)

**Vérifications**:
- [ ] Un message "Aucun employé trouvé" s'affiche
- [ ] La liste est vide
- [ ] Pas de crash ni d'erreur

---

## Test 4: Détail Employé et Onglets

### Objectif
Vérifier l'affichage détaillé d'un employé avec tous les onglets.

### Scénario 4.1 - Affichage du détail
1. Sélectionnez un employé
2. Cliquez sur "Voir détail" ou double-cliquez

**Vérifications**:
- [ ] La vue de détail s'ouvre avec les 4 onglets
- [ ] L'onglet "Informations" est actif par défaut
- [ ] Toutes les informations de l'employé sont affichées
- [ ] Les données sont cohérentes avec la liste

### Scénario 4.2 - Onglet CACES
1. Cliquez sur l'onglet "CACES"

**Vérifications**:
- [ ] La liste des CACES s'affiche (vide si aucun CACES)
- [ ] Le bouton "+ Ajouter" est visible
- [ ] Les colonnes sont : Type, Date complétion, Date expiration, Document

### Scénario 4.3 - Onglet Visites Médicales
1. Cliquez sur l'onglet "Visites Médicales"

**Vérifications**:
- [ ] La liste des visites s'affiche
- [ ] Le bouton "+ Ajouter" est visible
- [ ] Les colonnes sont : Type, Date, Résultat, Expiration

### Scénario 4.4 - Onglet Formations
1. Cliquez sur l'onglet "Formations"

**Vérifications**:
- [ ] La liste des formations en ligne s'affiche
- [ ] Les informations sont cohérentes

### Scénario 4.5 - Bouton Retour
1. Cliquez sur le bouton "Retour"

**Vérifications**:
- [ ] Retour à la liste des employés
- [ ] Les données sont rafraîchies si modifiées

---

## Test 5: Gestion des CACES (Phase 4.5)

### Objectif
Vérifier la gestion complète des certifications CACES.

### Prérequis
Avoir un employé créé (ex: TEST-001)

### Scénario 5.1 - Ajout d'un CACES
1. Allez dans le détail de l'employé TEST-001
2. Cliquez sur l'onglet "CACES"
3. Cliquez sur "+ Ajouter"
4. Remplissez le formulaire :
   - **Type**: R489-1A
   - **Date de complétion**: 15/01/2024
   - **Document**: (optionnel) C:\temp\caces_test.pdf
5. Observez la "Date d'expiration calculée"

**Vérifications**:
- [ ] L'expiration est automatiquement calculée (15/01/2029 pour R489-1A)
- [ ] Le bouton "Parcourir..." fonctionne pour sélectionner un document
- [ ] Après sauvegarde, le CACES apparaît dans la liste
- [ ] Les données sont correctement formatées

### Scénario 5.2 - Modification d'un CACES
1. Sélectionnez le CACES créé
2. Cliquez sur "Modifier"
3. Changez le **Type**: R489-5
4. Changez la **Date de complétion**: 01/01/2023
5. Vérifiez la nouvelle expiration

**Vérifications**:
- [ ] L'expiration est recalculée (01/01/2033 pour R489-5 = 10 ans)
- [ ] Les modifications sont sauvegardées
- [ ] La liste est mise à jour

### Scénario 5.3 - Suppression d'un CACES
1. Sélectionnez un CACES
2. Cliquez sur "Supprimer"
3. Confirmez

**Vérifications**:
- [ ] Le CACES est supprimé de la liste
- [ ] La confirmation est demandée avant suppression
- [ ] Pas de crash ni d'erreur

### Scénario 5.4 - Validation du formulaire CACES
1. Cliquez sur "+ Ajouter" un CACES
2. Essayez de sauvegarder sans remplir les champs

**Vérifications**:
- [ ] Une erreur s'affiche pour les champs requis
- [ ] La sauvegarde est bloquée
- [ ] Le message d'erreur est clair

### Scénario 5.5 - Calcul automatique de l'expiration
Testez différents types de CACES :
- R489-1A → 5 ans
- R489-1B → 5 ans
- R489-3 → 5 ans
- R489-4 → 5 ans
- R489-5 → 10 ans

**Vérifications**:
- [ ] Chaque type calcule correctement l'expiration
- [ ] L'aperçu se met à jour en temps réel

---

## Test 6: Gestion des Visites Médicales (Phase 4.5)

### Objectif
Vérifier la gestion complète des visites médicales.

### Prérequis
Avoir un employé créé (ex: TEST-001)

### Scénario 6.1 - Ajout d'une visite médicale
1. Allez dans le détail de l'employé TEST-001
2. Cliquez sur l'onglet "Visites Médicales"
3. Cliquez sur "+ Ajouter"
4. Remplissez le formulaire :
   - **Type**: Visite d'embauche
   - **Date**: 15/01/2025
   - **Résultat**: Apte
   - **Document**: (optionnel)

**Vérifications**:
- [ ] L'expiration est automatiquement calculée (15/01/2027)
- [ ] Les labels sont en français
- [ ] Le formulaire est clair et facile à utiliser
- [ ] Après sauvegarde, la visite apparaît dans la liste

### Scénario 6.2 - Modification d'une visite
1. Sélectionnez une visite médicale
2. Cliquez sur "Modifier"
3. Changez le **Résultat**: Apte avec restrictions
4. Changez la **Date**: 01/01/2024

**Vérifications**:
- [ ] L'expiration est recalculée (01/01/2026)
- [ ] Les modifications sont sauvegardées

### Scénario 6.3 - Types de visite et expiration
Testez différents types :
- Visite d'embauche → 2 ans
- Visite périodique → 2 ans
- Visite de reprise → 1 an

**Vérifications**:
- [ ] Chaque type calcule correctement l'expiration
- [ ] Les labels français sont corrects

### Scénario 6.4 - Résultats de visite
Testez tous les résultats :
- Apte
- Inapte
- Apte avec restrictions

**Vérifications**:
- [ ] Tous les résultats sont disponibles en dropdown
- [ ] La conversion en anglais fonctionne correctement

---

## Test 7: Système d'Alertes (Phase 4)

### Objectif
Vérifier le système d'alertes pour les certifications et visites expirantes.

### Prérequis
- Employé avec CACES expirant dans moins de 90 jours
- Employé avec visite médicale expirée

### Scénario 7.1 - Affichage des alertes
1. Cliquez sur l'onglet "Alertes"

**Vérifications**:
- [ ] La vue des alertes s'affiche
- [ ] Les filtres sont disponibles (Type, Jours)
- [ ] Les alertes sont colorées selon l'urgence
- [ ] Le nombre total d'alertes est affiché

### Scénario 7.2 - Filtrage par type
1. Filtrez par "CACES"
2. Filtrez par "Visites médicales"
3. Filtrez par "Toutes"

**Vérifications**:
- [ ] Le filtre fonctionne correctement
- [ ] Seules les alertes du type sélectionné s'affichent
- [ ] Le comptage est mis à jour

### Scénario 7.3 - Filtrage par période
1. Filtrez par "30 jours"
2. Filtrez par "60 jours"
3. Filtrez par "90 jours"
4. Filtrez par "Toutes"

**Vérifications**:
- [ ] Les alertes sont correctement filtrées par urgence
- [ ] Les badges d'urgence correspondent (Critique, Avertissement, Info)

### Scénario 7.4 - Navigation depuis les alertes
1. Cliquez sur une alerte
2. Cliquez sur "Voir détail"

**Vérifications**:
- [ ] La vue de détail de l'employé s'ouvre
- [ ] Les onglets appropriés sont actifs (CACES ou Visites)
- [ ] La certification/visite correspondante est visible

### Scénario 7.5 - Pas d'alertes
1. Supprimez toutes les certifications et visites

**Vérifications**:
- [ ] Un message "Aucune alerte" s'affiche
- [ ] Pas de crash ni d'erreur

---

## Test 8: Import Excel (Phase 5)

### Objectif
Vérifier le flux complet d'import Excel.

### Scénario 8.1 - Téléchargement du template
1. Allez dans l'onglet "Import"
2. Cliquez sur "Télécharger le modèle"
3. Sauvegardez le fichier

**Vérifications**:
- [ ] Le fichier Excel est généré
- [ ] Le fichier contient 2 onglets : "Instructions" et "Data"
- [ ] L'onglet "Instructions" contient le guide d'utilisation
- [ ] L'onglet "Data" contient les en-têtes corrects
- [ ] Les colonnes requises sont marquées d'un astérisque (*)
- [ ] Les listes déroulantes fonctionnent (Status, Workspace, Role, Contract)

### Scénario 8.2 - Import avec fichier valide
1. Utilisez le fichier `tests/fixtures/valid_employees.xlsx`
2. Cliquez sur "Choisir un fichier Excel..."
3. Sélectionnez le fichier valide
4. Vérifiez l'aperçu
5. Cliquez sur "Importer"

**Vérifications**:
- [ ] L'aperçu affiche les 5 employés
- [ ] Les colonnes sont correctement détectées
- [ ] La barre de progression s'affiche pendant l'import
- [ ] Le message "Import terminé" s'affiche
- [ ] Les statistiques sont correctes (5 réussis, 0 échoués)
- [ ] Les employés apparaissent dans la liste des employés

### Scénario 8.3 - Import avec fichier invalide (colonne manquante)
1. Utilisez `tests/fixtures/invalid_missing_column.xlsx`
2. Sélectionnez le fichier
3. Vérifiez l'erreur

**Vérifications**:
- [ ] Une erreur de validation s'affiche
- [ ] Le message mentionne la colonne manquante "Entry Date"
- [ ] L'import n'est pas exécuté
- [ ] Le bouton "Importer" reste désactivé

### Scénario 8.4 - Import avec données invalides
1. Utilisez `tests/fixtures/invalid_data.xlsx`
2. Sélectionnez le fichier
3. Lancez l'import

**Vérifications**:
- [ ] L'aperçu détecte les problèmes
- [ ] L'import se lance mais échoue sur les lignes invalides
- [ ] Les erreurs détaillées s'affichent (ligne par ligne)
- [ ] Les lignes valides sont importées
- [ ] Le comptage est correct (X réussis, Y échoués)

### Scénario 8.5 - Import de fichier vide
1. Utilisez `tests/fixtures/empty_file.xlsx`
2. Sélectionnez le fichier
3. Vérifiez l'aperçu

**Vérifications**:
- [ ] L'aperçu indique 0 lignes de données
- [ ] Le bouton "Importer" fonctionne mais n'importe rien
- [ ] Pas de crash ni d'erreur

### Scénario 8.6 - Import de grand fichier
1. Utilisez `tests/fixtures/large_file.xlsx` (100 lignes)
2. Lancez l'import

**Vérifications**:
- [ ] La barre de progression se met à jour
- [ ] L'import se termine en temps raisonnable (< 10 secondes)
- [ ] Les 100 employés sont importés
- [ ] Le comptage est correct

### Scénario 8.7 - Format de date
1. Créez un fichier Excel avec les dates aux formats :
   - DD/MM/YYYY (ex: 15/01/2025)
   - YYYY-MM-DD (ex: 2025-01-15)

**Vérifications**:
- [ ] Les deux formats sont acceptés
- [ ] Les dates sont correctement importées
- [ ] Le format français est prioritaire

---

## Test 9: Gestion des Erreurs et Cas Limites

### Objectif
Vérifier que l'application gère correctement les erreurs.

### Scénario 9.1 - ID externe en double
1. Créez un employé avec ID: TEST-DUPLICATE
2. Utilisez l'import Excel avec le même ID

**Vérifications**:
- [ ] L'erreur de duplication est détectée
- [ ] Le message d'erreur mentionne l'ID dupliqué
- [ ] L'import continue pour les autres lignes

### Scénario 9.2 - Date future
1. Essayez de créer/importer un employé avec une date d'entrée dans le futur (ex: 2030)

**Vérifications**:
- [ ] Une erreur de validation s'affiche
- [ ] Le message indique que la date ne peut pas être dans le futur
- [ ] La création/import est bloqué

### Scénario 9.3 - Date trop ancienne
1. Essayez une date d'entrée avant 2000 (ex: 1980)

**Vérifications**:
- [ ] Une erreur de validation s'affiche
- [ ] Le message indique que la date semble trop ancienne

### Scénario 9.4 - Email invalide
1. Créez un employé avec email: "pas-un-email"

**Vérifications**:
- [ ] Un avertissement s'affiche (pas une erreur bloquante)
- [ ] L'email est mis à None

### Scénario 9.5 - Valeurs d'énumération invalides
1. Essayez d'importer avec:
   - Workspace: "Zone Inexistante"
   - Role: "Role Inconnu"
   - Contract: "Type Invalide"

**Vérifications**:
- [ ] Des erreurs de validation s'affichent
- [ ] Les valeurs valides sont suggérées dans le message
- [ ] L'import échoue gracieusement

---

## Test 10: Performance et Stabilité

### Objectif
Vérifier que l'application reste stable avec beaucoup de données.

### Scénario 10.1 - Import en masse
1. Importez le fichier `large_file.xlsx` (100 employés)
2. Naviguez dans la liste

**Vérifications**:
- [ ] La liste se charge rapidement
- [ ] Le défilement est fluide
- [ ] La recherche reste rapide
- [ ] Pas de lag ni freeze

### Scénario 10.2 - Opérations répétées
1. Créez 10 employés
2. Modifiez-les tous
3. Supprimez-les tous

**Vérifications**:
- [ ] Aucune fuite de mémoire
- [ ] L'application reste responsive
- [ ] Pas d'accumulation d'erreurs

### Scénario 10.3 - Navigation rapide
1. Alternez rapidement entre les vues (Employés ↔ Alertes ↔ Import)

**Vérifications**:
- [ ] Les transitions sont fluides
- [ ] Pas de crash ni d'erreur
- [ ] L'état de chaque vue est préservé

---

## Test 11: Tests d'Intégration

### Objectif
Vérifier que les fonctionnalités travaillent ensemble.

### Scénario 11.1 - Flux complet : Création → CACES → Alerte
1. Créez un employé avec une date d'entrée ancienne (ex: 01/01/2020)
2. Ajoutez un CACES avec une date d'expiration proche (ex: dans 30 jours)
3. Allez dans l'onglet "Alertes"

**Vérifications**:
- [ ] L'alerte pour le CACES expirant apparaît
- [ ] Le niveau d'urgence est correct (Critique si < 30 jours)
- [ ] La navigation vers l'employé fonctionne

### Scénario 11.2 - Flux complet : Import → CACES → Export
1. Importez des employés via Excel
2. Ajoutez des CACES à plusieurs employés
3. Vérifiez les alertes générées

**Vérifications**:
- [ ] Les employés importés ont les CACES corrects
- [ ] Les alertes sont générées automatiquement
- [ ] Tout est cohérent

### Scénario 11.3 - Mise à jour en cascade
1. Modifiez un CACES (changez la date)
2. Rafraîchissez les alertes

**Vérifications**:
- [ ] Les alertes sont mises à jour
- [ ] L'urgence change si nécessaire

---

## Test 12: Utilisabilité et Expérience Utilisateur

### Objectif
Vérifier que l'application est facile à utiliser.

### Scénario 12.1 - Cohérence visuelle
- [ ] Les couleurs sont cohérentes dans toute l'application
- [ ] Les boutons ont le même style
- [ ] Les polices sont uniformes
- [ ] L'espacement est régulier

### Scénario 12.2 - Messages d'erreur
- [ ] Les messages sont en français
- [ ] Les erreurs sont claires et actionnables
- [ ] Les couleurs d'erreur sont cohérentes (rouge)
- [ ] Les avertissements sont orange/jaune

### Scénario 12.3 - Facilité d'utilisation
- [ ] Les boutons sont bien placés
- [ ] Les raccourcis clavier fonctionnent (si implémentés)
- [ ] La souris permet toutes les interactions
- [ ] Le défilement est intuitif

### Scénario 12.4 - Accessibilité
- [ ] Le contraste des couleurs est suffisant
- [ ] Le texte est lisible
- [ ] Les boutons sont assez grands
- [ ] Les zones de clic sont claires

---

## Checklist Récapitulative

### Fonctionnalités Core
- [ ] Création d'employé
- [ ] Modification d'employé
- [ ] Suppression d'employé
- [ ] Recherche d'employé
- [ ] Affichage détail employé

### CACES et Visites Médicales
- [ ] Ajout CACES avec calcul auto expiration
- [ ] Modification CACES
- [ ] Suppression CACES
- [ ] Ajout visite médicale avec calcul auto expiration
- [ ] Modification visite médicale
- [ ] Suppression visite médicale

### Alertes
- [ ] Affichage des alertes
- [ ] Filtrage par type
- [ ] Filtrage par urgence
- [ ] Navigation vers le détail

### Import Excel
- [ ] Téléchargement template
- [ ] Import fichier valide
- [ ] Gestion des erreurs
- [ ] Barre de progression
- [ ] Affichage des résultats

### Stabilité
- [ ] Pas de crash lors de la navigation
- [ ] Gestion correcte des erreurs
- [ ] Performance avec 100+ employés
- [ ] Nettoyage des ressources

---

## Résultats des Tests

**Date**: ___________

**Testeur**: ___________

**Version**: ___________

| Test | Résultat | Notes |
|------|----------|-------|
| Interface Globale | ☐ Pass / ☐ Fail | |
| CRUD Employés | ☐ Pass / ☐ Fail | |
| Recherche | ☐ Pass / ☐ Fail | |
| Détail Employé | ☐ Pass / ☐ Fail | |
| CACES | ☐ Pass / ☐ Fail | |
| Visites Médicales | ☐ Pass / ☐ Fail | |
| Alertes | ☐ Pass / ☐ Fail | |
| Import Excel | ☐ Pass / ☐ Fail | |
| Gestion Erreurs | ☐ Pass / ☐ Fail | |
| Performance | ☐ Pass / ☐ Fail | |
| Intégration | ☐ Pass / ☐ Fail | |
| Utilisabilité | ☐ Pass / ☐ Fail | |

**Taux de réussite**: _____ / 12

**Bugs trouvés**:
1.
2.
3.

**Suggestions d'amélioration**:
1.
2.
3.

---

## Prochaines Étapes

Si tous les tests passent :
- ✅ Prêt pour la Phase 6
- Documentez les bugs mineurs trouvés
- Planifiez les améliorations pour plus tard

Si des tests échouent :
- Priorisez les bugs critiques
- Corrigez avant de passer à la Phase 6
- Relancez les tests après corrections
