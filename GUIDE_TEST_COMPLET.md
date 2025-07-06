# 🧪 Guide de Test Complet - Edusco

## 🎯 **Objectif**
Ce guide vous permettra de tester l'ensemble de l'application Edusco en suivant un scénario complet d'une année académique, avec toutes les parties prenantes (Admin, Enseignants, Étudiants).

---

## 📋 **Prérequis**
- Application Edusco installée et fonctionnelle
- Base de données initialisée
- Navigateur web moderne
- 2-3 heures de temps disponible

---

## 👥 **Personnages du Test**

### **Administrateurs**
- **Admin Principal** : admin@edusco.com / admin123
- **Admin Secondaire** : admin2@edusco.com / admin123

### **Enseignants**
- **Dr. Ousmane Ba** : ousmane.ba@edusco.com / enseignant123
- **M. Alioune Ndiaye** : alioune.ndiaye@edusco.com / enseignant123
- **M. Fatou Sall** : fatou.sall@edusco.com / enseignant123
- **M. Mamadou Diallo** : mamadou.diallo@edusco.com / enseignant123

### **Étudiants**
- **Moussa Diop** : moussa.diop@edusco.com / etudiant123
- **Fatou Diallo** : fatou.diallo@edusco.com / etudiant123
- **Modou Fall** : modou.fall@edusco.com / etudiant123
- **Aissatou Ba** : aissatou.ba@edusco.com / etudiant123

---

## 🚀 **ÉTAPE 1 : Configuration Initiale (Admin)**

### **Tâche 1.1 : Connexion Admin**
1. Ouvrir l'application Edusco
2. Se connecter avec : admin@edusco.com / admin123
3. Vérifier l'accès au dashboard administrateur

### **Tâche 1.2 : Créer l'Année Académique**
1. Aller dans "Années Académiques"
2. Cliquer sur "Nouvelle année académique"
3. Remplir :
   - Nom : "2023-2024"
   - Date début : 01/09/2023
   - Date fin : 31/08/2024
4. Sauvegarder
5. Activer l'année académique

### **Tâche 1.3 : Créer les Semestres**
1. Aller dans "Semestres"
2. Créer le Semestre 1 :
   - Nom : "Semestre 1"
   - Code : "S1"
   - Date début : 01/09/2023
   - Date fin : 31/01/2024
3. Créer le Semestre 2 :
   - Nom : "Semestre 2"
   - Code : "S2"
   - Date début : 01/02/2024
   - Date fin : 30/06/2024
4. Activer le Semestre 1

### **Tâche 1.4 : Créer les UEs du Semestre 1**
1. Aller dans "Unités d'enseignement"
2. Créer UE101 - Mathématiques Fondamentales :
   - Code : "UE101"
   - Nom : "Mathématiques Fondamentales"
   - Crédits : 6
   - Coefficient : 1.0
   - Semestre : Semestre 1
3. Créer UE102 - Physique Générale :
   - Code : "UE102"
   - Nom : "Physique Générale"
   - Crédits : 4
   - Coefficient : 1.0
   - Semestre : Semestre 1
4. Créer UE103 - Informatique de Base :
   - Code : "UE103"
   - Nom : "Informatique de Base"
   - Crédits : 6
   - Coefficient : 1.0
   - Semestre : Semestre 1

### **Tâche 1.5 : Créer les Matières**
1. Aller dans "Matières"
2. Pour UE101 - Mathématiques Fondamentales :
   - Créer "Algèbre linéaire" (code: ALG101)
   - Créer "Calcul différentiel" (code: CAL101)
   - Créer "Probabilités" (code: PRO101)
3. Pour UE102 - Physique Générale :
   - Créer "Mécanique" (code: MEC102)
   - Créer "Électricité" (code: ELE102)
4. Pour UE103 - Informatique de Base :
   - Créer "Algorithmique" (code: ALG103)
   - Créer "Programmation C" (code: PRO103)
   - Créer "Structures de données" (code: STR103)

---

## 👨‍🏫 **ÉTAPE 2 : Gestion des Enseignants (Admin)**

### **Tâche 2.1 : Créer les Comptes Enseignants**
1. Aller dans "Utilisateurs"
2. Créer le compte de Dr. Ousmane Ba :
   - Email : ousmane.ba@edusco.com
   - Mot de passe : enseignant123
   - Rôle : Enseignant
3. Créer le profil enseignant :
   - Matricule : ENS001
   - Nom : Ba
   - Prénom : Ousmane
   - Spécialité : Mathématiques
   - Grade : Maître Assistant
4. Répéter pour les autres enseignants

### **Tâche 2.2 : Assigner les Matières aux Enseignants**
1. Aller dans "Matières"
2. Assigner les matières :
   - Dr. Ousmane Ba → Algèbre linéaire, Calcul différentiel, Probabilités
   - M. Alioune Ndiaye → Algorithmique, Structures de données
   - M. Fatou Sall → Mécanique, Électricité
   - M. Mamadou Diallo → Programmation C

---

## 👥 **ÉTAPE 3 : Gestion des Groupes Génériques (Admin)**

### **📚 Nouvelle Logique Pédagogique**
> **Note importante** : Nous utilisons maintenant un système de **groupes génériques** qui permet une gestion plus flexible :
> - Les **groupes génériques** représentent les promotions d'étudiants
> - Chaque groupe générique peut être lié à plusieurs UEs
> - Les étudiants sont inscrits dans les groupes génériques, pas dans les UEs directement
> - Cette approche permet une meilleure organisation et une gestion plus efficace

### **Tâche 3.1 : Créer les Groupes Génériques**
1. Aller dans "Groupes Génériques"
2. Créer les groupes génériques pour les promotions :

   **Promotion 1A (1ère année Informatique - Groupe A) :**
   - **Groupe Générique 1A** (code: 1A-GEN, capacité: 30)
     - Nom: "1ère année Informatique - Groupe A"
     - Description: "Promotion 1A - 1ère année Informatique - Groupe A"
     - Enseignant responsable: Dr. Ousmane Ba

   **Promotion 1B (1ère année Informatique - Groupe B) :**
   - **Groupe Générique 1B** (code: 1B-GEN, capacité: 30)
     - Nom: "1ère année Informatique - Groupe B"
     - Description: "Promotion 1B - 1ère année Informatique - Groupe B"
     - Enseignant responsable: M. Alioune Ndiaye

### **Tâche 3.2 : Lier les Groupes Génériques aux UEs**
1. Pour chaque groupe générique, lier aux UEs du Semestre 1 :

   **Groupe Générique 1A :**
   - Lier à UE101 - Mathématiques Fondamentales
   - Lier à UE102 - Physique Générale
   - Lier à UE103 - Informatique de Base

   **Groupe Générique 1B :**
   - Lier à UE101 - Mathématiques Fondamentales
   - Lier à UE102 - Physique Générale
   - Lier à UE103 - Informatique de Base

2. **Vérification** : Chaque groupe générique est lié à toutes les UEs du semestre
3. **Logique** : Les étudiants d'une promotion suivent toutes les UEs ensemble

### **Tâche 3.3 : Assigner les Enseignants Responsables**
1. Assigner les enseignants responsables pour les groupes génériques :

   **Groupe Générique 1A :**
   - **Dr. Ousmane Ba** (Responsable principal)
     - Matières : Algèbre linéaire, Calcul différentiel, Probabilités
   - **M. Fatou Sall** (Responsable Physique)
     - Matières : Mécanique, Électricité
   - **M. Alioune Ndiaye** (Responsable Informatique)
     - Matières : Algorithmique, Structures de données

   **Groupe Générique 1B :**
   - **M. Alioune Ndiaye** (Responsable principal)
     - Matières : Algorithmique, Structures de données
   - **Dr. Ousmane Ba** (Responsable Mathématiques)
     - Matières : Algèbre linéaire, Calcul différentiel, Probabilités
   - **M. Mamadou Diallo** (Responsable Informatique)
     - Matières : Programmation C

2. **Vérification** : Chaque groupe générique a un enseignant responsable principal
3. **Logique** : Les enseignants peuvent être responsables de plusieurs groupes selon leur spécialité

### **Tâche 3.4 : Tester les Fonctionnalités Avancées des Groupes Génériques**
1. **Modifier un groupe générique :**
   - Aller dans "Modifier" pour le Groupe 1A-GEN
   - Changer la capacité à 35
   - Vérifier la validation en temps réel
   - Sauvegarder les modifications

2. **Consulter les statistiques :**
   - Vérifier le taux de remplissage
   - Consulter les UEs liées
   - Voir les actions rapides disponibles

3. **Tester la suppression (avec précaution) :**
   - Essayer de supprimer un groupe générique avec des étudiants
   - Vérifier que le système empêche la suppression
   - Tester la suppression d'un groupe vide

---

## 👨‍🎓 **ÉTAPE 4 : Gestion des Étudiants (Admin)**

### **Tâche 4.1 : Créer les Comptes Étudiants**
1. Aller dans "Étudiants"
2. Créer les comptes étudiants :
   - Moussa Diop (matricule: 2023-001)
   - Fatou Diallo (matricule: 2023-002)
   - Modou Fall (matricule: 2023-003)
   - Aissatou Ba (matricule: 2023-004)

### **Tâche 4.2 : Inscrire les Étudiants dans les Groupes Génériques**
1. Inscrire les étudiants dans les groupes génériques de leur promotion :

   **Promotion 1A :**
   - **Moussa Diop (2023-001)** → Inscrit dans :
     - Groupe Générique 1A (1A-GEN)
   - **Fatou Diallo (2023-002)** → Inscrit dans :
     - Groupe Générique 1A (1A-GEN)

   **Promotion 1B :**
   - **Modou Fall (2023-003)** → Inscrit dans :
     - Groupe Générique 1B (1B-GEN)
   - **Aissatou Ba (2023-004)** → Inscrit dans :
     - Groupe Générique 1B (1B-GEN)

2. **Vérification** : Chaque étudiant doit être inscrit dans 1 groupe générique
3. **Logique pédagogique** : Les étudiants d'un groupe générique suivent automatiquement toutes les UEs liées à ce groupe
4. **Avantage** : Simplification de la gestion - un seul groupe à gérer par promotion

---

## 📝 **ÉTAPE 5 : Saisie des Notes (Enseignants)**

### **Tâche 5.1 : Connexion Enseignant**
1. Se connecter avec : ousmane.ba@edusco.com / enseignant123
2. Vérifier l'accès au dashboard enseignant

### **Tâche 5.2 : Saisir les Notes - Dr. Ousmane Ba (Groupe Générique 1A)**
1. Aller dans "Notes"
2. Sélectionner "Algèbre linéaire"
3. Sélectionner "Groupe Générique 1A"
4. Saisir les notes :
   - Moussa Diop : TP=15, Examen=14
   - Fatou Diallo : TP=16, Examen=13
5. Sauvegarder

### **Tâche 5.3 : Saisir les Notes - M. Alioune Ndiaye (Groupe Générique 1A)**
1. Se connecter avec : alioune.ndiaye@edusco.com / enseignant123
2. Aller dans "Notes"
3. Sélectionner "Algorithmique"
4. Sélectionner "Groupe Générique 1A"
5. Saisir les notes :
   - Moussa Diop : TP=18, Examen=16
   - Fatou Diallo : TP=17, Examen=15
6. Sauvegarder

### **Tâche 5.4 : Saisir les Notes - M. Fatou Sall (Groupe Générique 1A)**
1. Se connecter avec : fatou.sall@edusco.com / enseignant123
2. Aller dans "Notes"
3. Sélectionner "Mécanique"
4. Sélectionner "Groupe Générique 1A"
5. Saisir les notes :
   - Moussa Diop : TP=14, Examen=12
   - Fatou Diallo : TP=15, Examen=13
6. Sauvegarder

### **Tâche 5.5 : Saisir les Notes - Groupe Générique 1B**
1. Répéter le processus pour le Groupe Générique 1B :
   - **Matières Mathématiques** : Modou Fall, Aissatou Ba
   - **Matières Physique** : Modou Fall, Aissatou Ba
   - **Matières Informatique** : Modou Fall, Aissatou Ba

### **Tâche 5.6 : Saisir les Notes - Autres Enseignants**
1. Répéter pour tous les enseignants et toutes les matières
2. Varier les notes pour tester différents scénarios
3. **Note** : Maintenant, les enseignants sélectionnent directement le groupe générique au lieu de groupes séparés par UE

---

## ✅ **ÉTAPE 6 : Validation des Notes (Enseignant Responsable)**

### **Tâche 6.1 : Validation par Dr. Ousmane Ba**
1. Se connecter avec : ousmane.ba@edusco.com / enseignant123
2. Aller dans "Validation des notes"
3. Vérifier toutes les notes du Groupe Générique 1A (matières mathématiques)
4. Valider les notes

### **Tâche 6.2 : Validation par M. Alioune Ndiaye**
1. Se connecter avec : alioune.ndiaye@edusco.com / enseignant123
2. Valider les notes du Groupe Générique 1A (matières informatique)
3. Valider les notes du Groupe Générique 1B (matières informatique)

### **Tâche 6.3 : Validation par M. Fatou Sall**
1. Se connecter avec : fatou.sall@edusco.com / enseignant123
2. Valider les notes du Groupe Générique 1A (matières physique)

### **Tâche 6.4 : Validation des Groupes Génériques 1B**
1. Valider les notes de tous les groupes génériques 1B par leurs enseignants respectifs
2. **Note** : Les enseignants valident maintenant par groupe générique, ce qui simplifie le processus

---

## 🎯 **ÉTAPE 7 : Délibération (Admin)**

### **Tâche 7.1 : Préparation de la Délibération**
1. Se connecter en tant qu'admin
2. Aller dans "Pédagogique" → "Délibérations"
3. Créer une nouvelle délibération :
   - Semestre : Semestre 1
   - Groupe : Groupe Générique 1A (ou Groupe Générique 1B)
   - Date : Date actuelle
4. **Note** : La délibération sera basée sur toutes les notes de l'étudiant dans toutes les UEs liées au groupe générique
5. **Avantage** : Une seule délibération par groupe générique au lieu de délibérations séparées par UE

### **Tâche 7.2 : Analyse des Résultats**
1. Consulter les résultats automatiques
2. Vérifier les moyennes calculées
3. Analyser les cas particuliers

### **Tâche 7.3 : Décisions de Délibération**
1. Prendre les décisions :
   - Admis (moyenne ≥ 10/20)
   - Admis avec rattrapage
   - Redoublement
   - Exclusion
2. Valider la délibération

---

## 📊 **ÉTAPE 8 : Consultation des Résultats (Étudiants)**

### **Tâche 8.1 : Connexion Étudiant**
1. Se connecter avec : moussa.diop@edusco.com / etudiant123
2. Vérifier l'accès au dashboard étudiant

### **Tâche 8.2 : Consultation du Bulletin**
1. Aller dans "Bulletin"
2. Vérifier l'affichage des notes
3. Vérifier les moyennes calculées
4. Vérifier la décision de délibération

### **Tâche 8.3 : Consultation par Autres Étudiants**
1. Tester avec les autres comptes étudiants
2. Vérifier les différents résultats

---

## 📈 **ÉTAPE 9 : Rapports et Statistiques (Admin)**

### **Tâche 9.1 : Statistiques Globales**
1. Se connecter en tant qu'admin
2. Aller dans "Statistiques"
3. Consulter les statistiques :
   - Effectifs par groupe
   - Taux de réussite
   - Moyennes par UE

### **Tâche 9.2 : Rapports de Performance**
1. Aller dans "Rapports" → "Performance"
2. Générer des rapports détaillés
3. Exporter les données

### **Tâche 9.3 : Rapports par Groupe**
1. Consulter les rapports par groupe
2. Analyser les performances
3. Identifier les points d'amélioration

---

## 🔄 **ÉTAPE 10 : Test des Nouvelles Fonctionnalités des Groupes Génériques**

### **Tâche 10.1 : Test de la Modification des Groupes Génériques**
1. **Modifier un groupe générique :**
   - Aller dans "Groupes Génériques" → "Modifier" pour le Groupe 1A-GEN
   - Changer la capacité de 30 à 35
   - Vérifier que la validation en temps réel fonctionne
   - Sauvegarder les modifications
   - Vérifier que les statistiques se mettent à jour

2. **Tester la validation des données :**
   - Essayer de mettre une capacité inférieure au nombre d'étudiants actuels
   - Vérifier que le système empêche cette action
   - Tester avec des caractères spéciaux dans le code
   - Vérifier la validation côté client et serveur

### **Tâche 10.2 : Test de la Suppression des Groupes Génériques**
1. **Tester la suppression d'un groupe avec des étudiants :**
   - Essayer de supprimer le Groupe Générique 1A
   - Vérifier que le système affiche un message d'erreur
   - Confirmer que le groupe n'est pas supprimé

2. **Tester la suppression d'un groupe vide :**
   - Créer un groupe générique de test sans étudiants
   - Essayer de le supprimer
   - Vérifier que la suppression fonctionne

3. **Vérifier les dépendances :**
   - Tester la suppression d'un groupe avec des notes
   - Tester la suppression d'un groupe avec des UEs liées
   - Vérifier que toutes les dépendances sont vérifiées

### **Tâche 10.3 : Test des Statistiques et Rapports**
1. **Consulter les statistiques en temps réel :**
   - Vérifier le taux de remplissage des groupes
   - Consulter le nombre d'étudiants par groupe
   - Vérifier l'affichage des UEs liées

2. **Tester les actions rapides :**
   - Utiliser le bouton "Lier à une UE"
   - Utiliser le bouton "Lier à toutes les UE"
   - Vérifier que les actions fonctionnent correctement

### **Tâche 10.4 : Test de la Gestion des Absences**
1. Enseignant saisit des absences pour un groupe générique
2. Vérifier le suivi des absences
3. Consulter les rapports d'assiduité

### **Tâche 10.5 : Test de l'Emploi du Temps**
1. Créer un emploi du temps pour les groupes génériques
2. Assigner les cours aux groupes génériques
3. Consulter l'emploi du temps

### **Tâche 10.6 : Test des Notifications**
1. Envoyer des notifications aux groupes génériques
2. Vérifier la réception
3. Tester les alertes

---

## ✅ **ÉTAPE 11 : Test des Fonctionnalités Avancées Générales**

### **Tâche 11.1 : Test de l'Interface d'Administration**
1. **Navigation et ergonomie :**
   - Tester la navigation entre les différentes sections
   - Vérifier la cohérence des interfaces
   - Tester la responsivité sur différents écrans

2. **Recherche et filtres :**
   - Tester la recherche dans les listes
   - Vérifier les filtres par statut, année, etc.
   - Tester l'export des données

3. **Gestion des erreurs :**
   - Tester les cas d'erreur (données invalides, etc.)
   - Vérifier les messages d'erreur
   - Tester la récupération après erreur

### **Tâche 11.2 : Test de Performance**
1. **Temps de réponse :**
   - Tester avec plusieurs utilisateurs simultanés
   - Vérifier les temps de chargement des pages
   - Tester les exports de gros volumes de données

2. **Optimisation :**
   - Vérifier l'utilisation de la mémoire
   - Tester la pagination des listes
   - Vérifier les requêtes de base de données

### **Tâche 11.3 : Test de Sécurité**
1. **Accès et permissions :**
   - Tester les accès non autorisés
   - Vérifier les permissions par rôle
   - Tester la déconnexion automatique

2. **Validation des données :**
   - Tester l'injection SQL
   - Vérifier la validation des formulaires
   - Tester les uploads de fichiers

---

## ✅ **ÉTAPE 12 : Validation Finale**

### **Tâche 12.1 : Vérification Complète**
1. Tester tous les rôles (Admin, Enseignant, Étudiant)
2. Vérifier toutes les fonctionnalités principales
3. Valider les calculs automatiques (moyennes, délibérations)
4. Tester les nouvelles fonctionnalités des groupes génériques

### **Tâche 12.2 : Test de Cohérence**
1. Vérifier la cohérence des données entre les modules
2. Tester les relations entre groupes génériques et UEs
3. Valider les calculs de notes et moyennes
4. Vérifier les rapports et statistiques

### **Tâche 12.3 : Test de Robustesse**
1. Tester avec des données extrêmes
2. Vérifier la gestion des cas limites
3. Tester la récupération après panne
4. Valider les sauvegardes et restaurations

---

## 📋 **Checklist de Validation**

### **Configuration Initiale**
- [ ] Année académique créée et activée
- [ ] Semestres créés et activés
- [ ] UEs créées pour chaque semestre
- [ ] Matières créées pour chaque UE
- [ ] Enseignants créés et assignés
- [ ] **Groupes génériques créés et liés aux UEs**
- [ ] Étudiants créés et inscrits dans les groupes génériques

### **Activité Pédagogique**
- [ ] Notes saisies par tous les enseignants
- [ ] Notes validées par les responsables
- [ ] Délibération effectuée
- [ ] Résultats publiés

### **Consultation**
- [ ] Étudiants peuvent consulter leurs bulletins
- [ ] Enseignants peuvent voir leurs résultats
- [ ] Admin peut générer des rapports

### **Fonctionnalités Avancées**
- [ ] **Gestion des groupes génériques fonctionnelle**
- [ ] **Modification et suppression des groupes génériques testées**
- [ ] **Statistiques et rapports des groupes génériques opérationnels**
- [ ] Gestion des absences fonctionnelle
- [ ] Emploi du temps opérationnel
- [ ] Notifications envoyées et reçues
- [ ] **Interface d'administration moderne et responsive**
- [ ] **Validation des données robuste**

---

## 🎉 **Résultat Attendu**

À la fin de ce test, vous devriez avoir :
- Une année académique complète configurée
- Des données réalistes de test
- Toutes les fonctionnalités validées
- Une compréhension complète du système

**Temps estimé : 2-3 heures**

---

*Guide de test créé pour Edusco - Test complet du système* 