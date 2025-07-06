# Guide de Gestion des Utilisateurs - Edusco

## 📋 Vue d'ensemble

Le système Edusco utilise une architecture à **deux niveaux** pour la gestion des utilisateurs :

1. **Comptes utilisateurs** (authentification et rôles)
2. **Profils académiques** (données détaillées des enseignants/étudiants)

## 🔐 Niveau 1 : Gestion des Utilisateurs

### Menu : "Gestion des utilisateurs"

**Localisation :** `Admin > Gestion des utilisateurs`

**Fonctionnalités :**
- ✅ Créer des comptes utilisateurs avec rôles
- ✅ Gérer les permissions et accès
- ✅ Activer/désactiver des comptes
- ✅ Créer des profils académiques pour les utilisateurs existants

**Logique :**
- Un utilisateur peut avoir un rôle : `administrateur`, `enseignant`, `étudiant`
- Un utilisateur avec rôle `enseignant` peut avoir un profil enseignant associé
- Un utilisateur avec rôle `étudiant` peut avoir un profil étudiant associé

## 👨‍🏫 Niveau 2 : Gestion des Enseignants

### Menu : "Enseignants"

**Localisation :** `Admin > Enseignants`

**Fonctionnalités :**
- ✅ Créer des enseignants avec profil complet
- ✅ Création automatique du compte utilisateur associé
- ✅ Gestion des statuts (actif, inactif, retraite, démissionné)
- ✅ Modification des profils détaillés

**Logique :**
- Création d'un enseignant = Création automatique du compte utilisateur
- Mot de passe temporaire généré : `enseignant{matricule}`
- Lien automatique entre le profil enseignant et le compte utilisateur

## 👨‍🎓 Niveau 3 : Gestion des Étudiants

### Menu : "Étudiants"

**Localisation :** `Admin > Étudiants`

**Fonctionnalités :**
- ✅ Créer des étudiants avec profil complet
- ✅ Création automatique du compte utilisateur associé
- ✅ Gestion des inscriptions et groupes
- ✅ Modification des profils détaillés

**Logique :**
- Création d'un étudiant = Création automatique du compte utilisateur
- Mot de passe temporaire généré : `etudiant{matricule}`
- Lien automatique entre le profil étudiant et le compte utilisateur

## 🎯 Recommandations d'Utilisation

### Pour ajouter un enseignant :

**Option 1 (Recommandée) : Menu "Enseignants"**
```
Admin > Enseignants > "Nouvel enseignant"
```
- ✅ Crée automatiquement le profil enseignant ET le compte utilisateur
- ✅ Génère un mot de passe temporaire
- ✅ Interface dédiée avec tous les champs nécessaires

**Option 2 : Menu "Gestion des utilisateurs"**
```
Admin > Gestion des utilisateurs > "Créer un utilisateur" > Rôle "enseignant"
```
- ✅ Crée d'abord le compte utilisateur
- ⚠️ Nécessite ensuite de créer le profil enseignant séparément

### Pour ajouter un étudiant :

**Option 1 (Recommandée) : Menu "Étudiants"**
```
Admin > Étudiants > "Ajouter un étudiant"
```
- ✅ Crée automatiquement le profil étudiant ET le compte utilisateur
- ✅ Génère un mot de passe temporaire
- ✅ Interface dédiée avec tous les champs nécessaires

**Option 2 : Menu "Gestion des utilisateurs"**
```
Admin > Gestion des utilisateurs > "Créer un utilisateur" > Rôle "étudiant"
```
- ✅ Crée d'abord le compte utilisateur
- ⚠️ Nécessite ensuite de créer le profil étudiant séparément

## 🗑️ Suppression des Données

### Suppression individuelle

**Enseignants :**
- Menu "Enseignants" > Actions > Changer statut (inactif, retraite, démissionné)
- ⚠️ Pas de suppression définitive dans l'interface (pour préserver l'historique)

**Étudiants :**
- Menu "Étudiants" > Actions > Supprimer
- ✅ Supprime l'étudiant ET son compte utilisateur

**Utilisateurs :**
- Menu "Gestion des utilisateurs" > Actions > Supprimer
- ✅ Supprime l'utilisateur ET son profil académique

### Suppression en masse (Recommencer à zéro)

**Script automatique :**
```bash
python scripts/supprimer_donnees.py
```

**Ce script supprime :**
- ✅ Tous les enseignants et leurs comptes utilisateurs
- ✅ Tous les étudiants et leurs comptes utilisateurs
- ✅ Toutes les données pédagogiques (notes, absences, emplois du temps)
- ✅ Toutes les structures académiques (groupes, matières, UE, semestres, années)

**Vérification du statut :**
```bash
python scripts/supprimer_donnees.py --statut
```

## 🔄 Workflow Recommandé

### 1. Initialisation (première utilisation)
```bash
# Vérifier l'état actuel
python scripts/supprimer_donnees.py --statut

# Si nécessaire, nettoyer complètement
python scripts/supprimer_donnees.py
```

### 2. Création des structures académiques
1. Créer les années académiques
2. Créer les semestres
3. Créer les unités d'enseignement
4. Créer les matières

### 3. Création des enseignants
```
Admin > Enseignants > "Nouvel enseignant"
```
- Remplir tous les champs
- Le compte utilisateur est créé automatiquement
- Communiquer le mot de passe temporaire

### 4. Création des étudiants
```
Admin > Étudiants > "Ajouter un étudiant"
```
- Remplir tous les champs
- Le compte utilisateur est créé automatiquement
- Communiquer le mot de passe temporaire

### 5. Attribution des matières aux enseignants
```
Admin > Matières > Modifier > Assigner enseignant
```

### 6. Création des groupes
```
Admin > Groupes > "Créer un groupe"
```
- Assigner les étudiants
- Assigner l'enseignant responsable

## ⚠️ Points d'Attention

1. **Mots de passe temporaires :** Toujours communiquer aux utilisateurs
2. **Matricules uniques :** Vérifier qu'ils n'existent pas déjà
3. **Emails uniques :** Chaque utilisateur doit avoir un email unique
4. **Sauvegarde :** Toujours faire une sauvegarde avant suppression en masse
5. **Historique :** Les suppressions individuelles préservent l'historique

## 🆘 En cas de problème

1. **Erreur de matricule dupliqué :** Vérifier dans la liste des enseignants/étudiants
2. **Erreur d'email dupliqué :** Vérifier dans la gestion des utilisateurs
3. **Compte utilisateur manquant :** Utiliser le script `creer_comptes_utilisateurs.py`
4. **Données corrompues :** Utiliser le script `supprimer_donnees.py` pour recommencer

## 📞 Support

Pour toute question ou problème :
- Consulter les logs de l'application
- Vérifier les contraintes de la base de données
- Utiliser les scripts de diagnostic fournis 