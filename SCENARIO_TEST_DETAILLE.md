# 🎬 Scénario de Test Détaillé - Edusco

## 🎯 **Scénario : Année Académique 2023-2024 - DSTTR**

### **Contexte**
Test complet d'une année académique pour le département "Génie Informatique, Télécoms et Réseaux" (DSTTR) avec 3 groupes de 1ère année.

---

## 👥 **Personnages et Données de Test**

### **Administrateurs**
```
Admin Principal
- Email: admin@edusco.com
- Mot de passe: admin123
- Rôle: Administrateur principal

Admin Secondaire  
- Email: admin2@edusco.com
- Mot de passe: admin123
- Rôle: Administrateur secondaire
```

### **Enseignants**
```
Dr. Ousmane Ba (Enseignant Responsable)
- Email: ousmane.ba@edusco.com
- Mot de passe: enseignant123
- Matricule: ENS001
- Spécialité: Mathématiques
- Grade: Maître Assistant
- Matières: Algèbre linéaire, Calcul différentiel
- Responsable: Groupe A (toutes UEs)

M. Alioune Ndiaye
- Email: alioune.ndiaye@edusco.com
- Mot de passe: enseignant123
- Matricule: ENS002
- Spécialité: Informatique
- Grade: Assistant
- Matières: Algorithmique, Programmation C
- Responsable: Groupe B (toutes UEs)

M. Fatou Sall
- Email: fatou.sall@edusco.com
- Mot de passe: enseignant123
- Matricule: ENS003
- Spécialité: Physique
- Grade: Assistant
- Matières: Mécanique, Électricité

M. Mamadou Diallo
- Email: mamadou.diallo@edusco.com
- Mot de passe: enseignant123
- Matricule: ENS004
- Spécialité: Informatique
- Grade: Assistant
- Matières: Structures de données, Programmation C

M. Khady Diagne
- Email: khady.diagne@edusco.com
- Mot de passe: enseignant123
- Matricule: ENS005
- Spécialité: Mathématiques
- Grade: Assistant
- Matières: Probabilités
```

### **Étudiants**
```
Groupe A (DSTTR1A) - 4 étudiants
├── Moussa Diop
│   - Email: moussa.diop@edusco.com
│   - Mot de passe: etudiant123
│   - Matricule: 2023-001
│   - Profil: Bon étudiant, régulier
├── Fatou Diallo
│   - Email: fatou.diallo@edusco.com
│   - Mot de passe: etudiant123
│   - Matricule: 2023-002
│   - Profil: Excellente étudiante
├── Modou Fall
│   - Email: modou.fall@edusco.com
│   - Mot de passe: etudiant123
│   - Matricule: 2023-003
│   - Profil: Étudiant en difficulté
└── Aissatou Ba
    - Email: aissatou.ba@edusco.com
    - Mot de passe: etudiant123
    - Matricule: 2023-004
    - Profil: Étudiante moyenne

Groupe B (DSTTR1B) - 4 étudiants
├── Ibrahima Sow
│   - Email: ibrahima.sow@edusco.com
│   - Mot de passe: etudiant123
│   - Matricule: 2023-005
├── Khady Ndiaye
│   - Email: khady.ndiaye@edusco.com
│   - Mot de passe: etudiant123
│   - Matricule: 2023-006
├── Ousmane Diallo
│   - Email: ousmane.diallo@edusco.com
│   - Mot de passe: etudiant123
│   - Matricule: 2023-007
└── Aminata Fall
│   - Email: aminata.fall@edusco.com
│   - Mot de passe: etudiant123
│   - Matricule: 2023-008
```

---

## 📚 **Structure Académique**

### **Année Académique**
```
Nom: 2023-2024
Date début: 01/09/2023
Date fin: 31/08/2024
Statut: Active
```

### **Semestres**
```
Semestre 1
- Nom: Semestre 1
- Code: S1
- Date début: 01/09/2023
- Date fin: 31/01/2024
- Statut: Actif

Semestre 2
- Nom: Semestre 2  
- Code: S2
- Date début: 01/02/2024
- Date fin: 30/06/2024
- Statut: Inactif
```

### **Unités d'Enseignement (Semestre 1)**
```
UE101 - Mathématiques Fondamentales
- Code: UE101
- Nom: Mathématiques Fondamentales
- Crédits: 6
- Coefficient: 1.0
- Semestre: Semestre 1

UE102 - Physique Générale
- Code: UE102
- Nom: Physique Générale
- Crédits: 4
- Coefficient: 1.0
- Semestre: Semestre 1

UE103 - Informatique de Base
- Code: UE103
- Nom: Informatique de Base
- Crédits: 6
- Coefficient: 1.0
- Semestre: Semestre 1
```

### **Matières**
```
UE101 - Mathématiques Fondamentales
├── ALG101 - Algèbre linéaire
│   - Enseignant: Dr. Ousmane Ba
│   - Volume horaire: 30h
│   - Coefficient: 1.0
├── CAL101 - Calcul différentiel
│   - Enseignant: Dr. Ousmane Ba
│   - Volume horaire: 30h
│   - Coefficient: 1.0
└── PRO101 - Probabilités
    - Enseignant: M. Khady Diagne
    - Volume horaire: 20h
    - Coefficient: 1.0

UE102 - Physique Générale
├── MEC102 - Mécanique
│   - Enseignant: M. Fatou Sall
│   - Volume horaire: 25h
│   - Coefficient: 1.0
└── ELE102 - Électricité
    - Enseignant: M. Fatou Sall
    - Volume horaire: 25h
    - Coefficient: 1.0

UE103 - Informatique de Base
├── ALG103 - Algorithmique
│   - Enseignant: M. Alioune Ndiaye
│   - Volume horaire: 30h
│   - Coefficient: 1.0
├── PRO103 - Programmation C
│   - Enseignant: M. Mamadou Diallo
│   - Volume horaire: 30h
│   - Coefficient: 1.0
└── STR103 - Structures de données
    - Enseignant: M. Mamadou Diallo
    - Volume horaire: 25h
    - Coefficient: 1.0
```

### **Groupes**
```
Groupe A (DSTTR1A)
- Code: GA
- Nom: Groupe A - DSTTR1
- Capacité: 30 étudiants
- Enseignant responsable: Dr. Ousmane Ba
- Étudiants: 4 (Moussa, Fatou, Modou, Aissatou)

Groupe B (DSTTR1B)
- Code: GB
- Nom: Groupe B - DSTTR1
- Capacité: 30 étudiants
- Enseignant responsable: M. Alioune Ndiaye
- Étudiants: 4 (Ibrahima, Khady, Ousmane, Aminata)
```

---

## 📊 **Données de Notes de Test**

### **Groupe A - Notes Réalistes**

#### **Moussa Diop (Bon étudiant)**
```
UE101 - Mathématiques Fondamentales
├── Algèbre linéaire (Dr. Ousmane Ba)
│   ├── Note TP: 15/20
│   ├── Note Examen: 14/20
│   └── Moyenne: 14.5/20
├── Calcul différentiel (Dr. Ousmane Ba)
│   ├── Note TP: 16/20
│   ├── Note Examen: 13/20
│   └── Moyenne: 14.5/20
└── Probabilités (M. Khady Diagne)
    ├── Note TP: 12/20
    ├── Note Examen: 15/20
    └── Moyenne: 13.5/20
Moyenne UE101: 14.17/20

UE102 - Physique Générale
├── Mécanique (M. Fatou Sall)
│   ├── Note TP: 14/20
│   ├── Note Examen: 13/20
│   └── Moyenne: 13.5/20
└── Électricité (M. Fatou Sall)
    ├── Note TP: 15/20
    ├── Note Examen: 14/20
    └── Moyenne: 14.5/20
Moyenne UE102: 14.0/20

UE103 - Informatique de Base
├── Algorithmique (M. Alioune Ndiaye)
│   ├── Note TP: 18/20
│   ├── Note Examen: 16/20
│   └── Moyenne: 17.0/20
├── Programmation C (M. Mamadou Diallo)
│   ├── Note TP: 17/20
│   ├── Note Examen: 15/20
│   └── Moyenne: 16.0/20
└── Structures de données (M. Mamadou Diallo)
    ├── Note TP: 16/20
    ├── Note Examen: 14/20
    └── Moyenne: 15.0/20
Moyenne UE103: 16.0/20

MOYENNE GÉNÉRALE: 14.72/20 → ADMIS
```

#### **Fatou Diallo (Excellente étudiante)**
```
UE101: 16.33/20
UE102: 17.0/20
UE103: 18.0/20
MOYENNE GÉNÉRALE: 17.11/20 → ADMIS
```

#### **Modou Fall (Étudiant en difficulté)**
```
UE101: 8.17/20
UE102: 7.5/20
UE103: 9.0/20
MOYENNE GÉNÉRALE: 8.22/20 → RATTRAPAGE
```

#### **Aissatou Ba (Étudiante moyenne)**
```
UE101: 11.5/20
UE102: 10.5/20
UE103: 12.0/20
MOYENNE GÉNÉRALE: 11.33/20 → ADMIS
```

### **Groupe B - Notes Réalistes**

#### **Ibrahima Sow**
```
UE101: 9.5/20
UE102: 8.8/20
UE103: 10.2/20
MOYENNE GÉNÉRALE: 9.5/20 → RATTRAPAGE
```

#### **Khady Ndiaye**
```
UE101: 7.8/20
UE102: 6.5/20
UE103: 8.2/20
MOYENNE GÉNÉRALE: 7.5/20 → REDOUBLEMENT
```

#### **Ousmane Diallo**
```
UE101: 4.2/20
UE102: 3.8/20
UE103: 5.1/20
MOYENNE GÉNÉRALE: 4.37/20 → EXCLUSION
```

#### **Aminata Fall**
```
UE101: 3.8/20
UE102: 4.1/20
UE103: 3.5/20
MOYENNE GÉNÉRALE: 3.8/20 → EXCLUSION
```

---

## 🎯 **Résultats de Délibération Attendus**

### **Groupe A (DSTTR1A)**
```
✅ ADMIS (3 étudiants)
├── Moussa Diop: 14.72/20
├── Fatou Diallo: 17.11/20
└── Aissatou Ba: 11.33/20

⚠️ ADMIS AVEC RATTRAPAGE (1 étudiant)
└── Modou Fall: 8.22/20 (rattrapage UE101 et UE102)

Taux de réussite: 75%
```

### **Groupe B (DSTTR1B)**
```
✅ ADMIS (0 étudiant)

⚠️ ADMIS AVEC RATTRAPAGE (1 étudiant)
└── Ibrahima Sow: 9.5/20 (rattrapage UE101 et UE102)

❌ REDOUBLEMENT (1 étudiant)
└── Khady Ndiaye: 7.5/20

🚫 EXCLUSION (2 étudiants)
├── Ousmane Diallo: 4.37/20
└── Aminata Fall: 3.8/20

Taux de réussite: 0%
```

---

## 📋 **Étapes de Test Détaillées**

### **Phase 1 : Configuration (30 minutes)**
1. **Créer l'année académique 2023-2024**
2. **Créer les semestres S1 et S2**
3. **Créer les 3 UEs du semestre 1**
4. **Créer les 8 matières**
5. **Créer les comptes enseignants (5)**
6. **Créer les comptes étudiants (8)**
7. **Créer les 2 groupes**
8. **Assigner les enseignants aux matières**
9. **Assigner les enseignants responsables aux groupes**
10. **Inscrire les étudiants dans les groupes**

### **Phase 2 : Saisie des Notes (45 minutes)**
1. **Dr. Ousmane Ba** → Saisir notes Algèbre et Calcul (Groupe A)
2. **M. Alioune Ndiaye** → Saisir notes Algorithmique (Groupe A)
3. **M. Fatou Sall** → Saisir notes Mécanique et Électricité (Groupe A)
4. **M. Mamadou Diallo** → Saisir notes Programmation C et Structures (Groupe A)
5. **M. Khady Diagne** → Saisir notes Probabilités (Groupe A)
6. **Répéter pour le Groupe B** avec les notes fournies

### **Phase 3 : Validation et Délibération (30 minutes)**
1. **Dr. Ousmane Ba** → Valider notes Groupe A
2. **M. Alioune Ndiaye** → Valider notes Groupe B
3. **Admin** → Créer délibération Semestre 1
4. **Admin** → Analyser résultats automatiques
5. **Admin** → Valider délibération

### **Phase 4 : Consultation (15 minutes)**
1. **Étudiants** → Consulter leurs bulletins
2. **Enseignants** → Consulter résultats de leurs groupes
3. **Admin** → Générer rapports et statistiques

---

## ✅ **Critères de Validation**

### **Fonctionnel**
- [ ] Toutes les données sont créées correctement
- [ ] Les calculs de moyennes sont exacts
- [ ] Les délibérations fonctionnent
- [ ] Les bulletins s'affichent correctement

### **Interface**
- [ ] Navigation fluide entre les pages
- [ ] Formulaires fonctionnels
- [ ] Messages d'erreur/succès appropriés
- [ ] Responsive design

### **Données**
- [ ] Cohérence des données
- [ ] Intégrité des relations
- [ ] Calculs automatiques corrects
- [ ] Export des données

### **Sécurité**
- [ ] Contrôle d'accès par rôle
- [ ] Validation des données
- [ ] Protection contre les injections
- [ ] Gestion des sessions

---

*Scénario de test créé pour Edusco - Test complet avec données réalistes* 