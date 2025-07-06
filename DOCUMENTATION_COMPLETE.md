# 📚 Documentation Complète - Edusco

## 🎓 **Système de Gestion Académique**

### **Vue d'ensemble**
Edusco est un système de gestion académique complet permettant la gestion des années académiques, semestres, unités d'enseignement, matières, groupes, étudiants, enseignants et de toutes les activités pédagogiques associées.

---

## 🏗️ **Architecture Académique**

### **Structure Hiérarchique**
```
Année Académique (ex: 2023-2024)
├── Semestre 1
│   ├── UE101 : Mathématiques Fondamentales
│   │   ├── Matière 1 : Algèbre linéaire
│   │   ├── Matière 2 : Calcul différentiel
│   │   └── Matière 3 : Probabilités
│   ├── UE102 : Physique Générale
│   └── UE103 : Informatique de Base
└── Semestre 2
    ├── UE201 : Mathématiques Appliquées
    └── UE202 : Électronique Numérique
```

### **Organisation par Groupes**
```
Département : Génie Informatique, Télécoms et Réseaux (DSTTR)

1ère Année (DSTTR1)
├── Groupe A (DSTTR1A) - 30 étudiants
├── Groupe B (DSTTR1B) - 30 étudiants  
└── Groupe C (DSTTR1C) - 30 étudiants

2ème Année (DSTTR2)
├── Groupe A (DSTTR2A) - 28 étudiants
├── Groupe B (DSTTR2B) - 28 étudiants
└── Groupe C (DSTTR2C) - 28 étudiants
```

---

## 👥 **Rôles et Responsabilités**

### **1. Administrateur**
- **Gestion des années académiques** : Création, activation, modification
- **Gestion des semestres** : Création, activation, modification
- **Gestion des UEs** : Création, modification, suppression
- **Gestion des matières** : Création, assignation d'enseignants
- **Gestion des groupes** : Création, assignation d'enseignants responsables
- **Gestion des utilisateurs** : Création de comptes admin, enseignant, étudiant
- **Gestion des étudiants** : Inscription, modification, suppression
- **Gestion des enseignants** : Création, modification, statut
- **Validation des notes** : Contrôle et validation des saisies
- **Délibérations** : Organisation et présidence des délibérations
- **Rapports** : Génération de statistiques et rapports

### **2. Enseignant par Matière**
- **Saisie des notes** : TP, examens, moyennes
- **Gestion des absences** : Saisie et suivi
- **Consultation** : Résultats de ses groupes
- **Rapports** : Statistiques de ses matières

### **3. Enseignant Responsable de Groupe**
- **Coordination pédagogique** : Suivi global du groupe
- **Validation des notes** : Vérification et validation
- **Gestion administrative** : Inscriptions, absences
- **Référent étudiant** : Accompagnement et conseil
- **Préparation délibération** : Analyse des résultats

### **4. Étudiant**
- **Consultation des notes** : Bulletin de notes
- **Emploi du temps** : Planning des cours
- **Absences** : Consultation de son assiduité
- **Notifications** : Alertes et informations

---

## 📊 **Système de Notes et Évaluation**

### **Structure des Notes**
```
Matière : Algorithmique (UE103)
├── Note TP : 15/20 (coefficient 0.4)
├── Note Examen : 14/20 (coefficient 0.6)
└── Moyenne : 14.4/20

UE : Informatique de Base
├── Algorithmique : 14.4/20 (coefficient 1.0)
├── Programmation C : 16.2/20 (coefficient 1.0)
└── Structures de données : 15.8/20 (coefficient 1.0)
Moyenne UE : 15.47/20
```

### **Processus de Validation**
1. **Saisie** : Enseignant saisit les notes
2. **Validation** : Enseignant responsable valide
3. **Contrôle** : Administrateur vérifie
4. **Publication** : Notes disponibles aux étudiants

---

## 🎯 **Délibération**

### **Processus Complet**
```
1. Saisie des Notes
   ├── Chaque enseignant saisit ses notes
   ├── Validation par l'enseignant responsable
   └── Contrôle administratif

2. Calcul Automatique
   ├── Moyennes par matière
   ├── Moyennes par UE
   ├── Moyenne générale
   └── Crédits obtenus

3. Commission de Délibération
   ├── Présidence : Administrateur
   ├── Membres : Enseignants responsables
   ├── Analyse des résultats
   └── Décisions

4. Décisions Possibles
   ├── Admis (moyenne ≥ 10/20)
   ├── Admis avec rattrapage
   ├── Redoublement
   └── Exclusion

5. Publication
   ├── Bulletins de notes
   ├── Notification aux étudiants
   └── Archivage
```

---

## 🔄 **Flux de Données**

### **1. Configuration Initiale (Admin)**
```
Année Académique → Semestres → UEs → Matières → Groupes → Utilisateurs
```

### **2. Assignation (Admin)**
```
Enseignants → Matières
Enseignants Responsables → Groupes
Étudiants → Groupes
```

### **3. Activité Pédagogique**
```
Enseignants → Saisie notes/absences
Enseignants Responsables → Validation
Admin → Contrôle et délibération
Étudiants → Consultation résultats
```

---

## 💻 **Fonctionnalités Techniques**

### **Interface Administrateur**
- Dashboard avec statistiques
- Gestion complète des entités académiques
- Validation et contrôle des données
- Rapports et exports

### **Interface Enseignant**
- Saisie des notes et absences
- Consultation des résultats
- Gestion de ses groupes (si responsable)

### **Interface Étudiant**
- Consultation du bulletin
- Emploi du temps
- Suivi des absences

### **Sécurité**
- Authentification par rôle
- Contrôle d'accès
- Validation des données
- Audit des actions

---

## 📈 **Avantages du Système**

### **Pour l'Administration**
- **Centralisation** : Toutes les données au même endroit
- **Automatisation** : Calculs automatiques des moyennes
- **Contrôle** : Validation à chaque étape
- **Rapports** : Statistiques détaillées

### **Pour les Enseignants**
- **Simplicité** : Interface intuitive pour la saisie
- **Efficacité** : Calculs automatiques
- **Suivi** : Vision claire des résultats

### **Pour les Étudiants**
- **Transparence** : Accès direct aux résultats
- **Réactivité** : Résultats en temps réel
- **Historique** : Conservation des données

---

## 🔧 **Configuration et Déploiement**

### **Prérequis**
- Python 3.8+
- Flask
- SQLAlchemy
- Base de données (SQLite/PostgreSQL)

### **Installation**
```bash
pip install -r requirements.txt
python app.py
```

### **Configuration**
- Variables d'environnement
- Base de données
- Sécurité

---

## 📞 **Support et Maintenance**

### **Documentation**
- Guide utilisateur
- Guide administrateur
- API documentation

### **Maintenance**
- Sauvegardes régulières
- Mises à jour de sécurité
- Optimisation des performances

---

*Documentation créée pour Edusco - Système de Gestion Académique* 