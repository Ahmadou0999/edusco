# 🧪 Test Complet Edusco - Guide d'Utilisation

## 🎯 **Objectif**
Ce guide vous permet de tester l'ensemble de l'application Edusco en suivant un scénario complet d'une année académique.

## 📚 **Documentation Disponible**

### **1. Documentation Complète**
- **Fichier :** `DOCUMENTATION_COMPLETE.md`
- **Contenu :** Explication complète du système, architecture, rôles, processus
- **Usage :** Comprendre le fonctionnement théorique

### **2. Guide de Test Complet**
- **Fichier :** `GUIDE_TEST_COMPLET.md`
- **Contenu :** Étapes détaillées pour tester toutes les fonctionnalités
- **Usage :** Suivre le test étape par étape

### **3. Scénario de Test Détaillé**
- **Fichier :** `SCENARIO_TEST_DETAILLE.md`
- **Contenu :** Données concrètes, personnages, résultats attendus
- **Usage :** Avoir des données réalistes pour le test

## 🚀 **Démarrage Rapide**

### **Prérequis**
```bash
# Vérifier que l'application fonctionne
python app.py
```

### **Accès aux Interfaces**
```
Admin : http://localhost:5000/admin
Enseignant : http://localhost:5000/enseignant
Étudiant : http://localhost:5000/etudiant
```

### **Comptes de Test**
```
Admin Principal : admin@edusco.com / admin123
Enseignant Responsable : ousmane.ba@edusco.com / enseignant123
Étudiant Test : moussa.diop@edusco.com / etudiant123
```

## 📋 **Plan de Test Recommandé**

### **Phase 1 : Configuration (30 min)**
1. Lire `DOCUMENTATION_COMPLETE.md` pour comprendre le système
2. Suivre `GUIDE_TEST_COMPLET.md` - Étapes 1 à 4
3. Utiliser les données de `SCENARIO_TEST_DETAILLE.md`

### **Phase 2 : Activité Pédagogique (45 min)**
1. Suivre `GUIDE_TEST_COMPLET.md` - Étapes 5 à 7
2. Saisir toutes les notes avec les données fournies
3. Valider et délibérer

### **Phase 3 : Consultation (15 min)**
1. Suivre `GUIDE_TEST_COMPLET.md` - Étapes 8 à 11
2. Tester tous les rôles
3. Vérifier les résultats

## 🎬 **Scénario de Test Principal**

### **Contexte**
- **Département :** DSTTR (Génie Informatique, Télécoms et Réseaux)
- **Niveau :** 1ère année
- **Groupes :** DSTTR1A et DSTTR1B
- **Période :** Semestre 1 (2023-2024)

### **Personnages**
- **5 Enseignants** avec rôles différents
- **8 Étudiants** avec profils variés
- **1 Admin** pour la coordination

### **Résultats Attendus**
- **Groupe A :** 75% de réussite (3 admis, 1 rattrapage)
- **Groupe B :** 0% de réussite (1 rattrapage, 1 redoublement, 2 exclusions)

## 🔧 **Dépannage**

### **Problèmes Courants**
1. **Erreur de connexion** → Vérifier les comptes de test
2. **Données manquantes** → Suivre le guide étape par étape
3. **Calculs incorrects** → Vérifier les coefficients et formules
4. **Interface bloquée** → Rafraîchir la page

### **Vérifications**
```bash
# Vérifier la base de données
python -c "from app import app; from app.models.academique import *; print('Années:', AnneeAcademique.query.count())"

# Vérifier les routes
python -c "from app import app; print('Routes disponibles:', len(app.url_map.iter_rules()))"
```

## 📊 **Validation des Résultats**

### **Points de Contrôle**
- [ ] Année académique créée et active
- [ ] Tous les enseignants connectés
- [ ] Toutes les notes saisies
- [ ] Délibération effectuée
- [ ] Bulletins consultables
- [ ] Rapports générés

### **Métriques de Succès**
- **Fonctionnel :** 100% des fonctionnalités testées
- **Performance :** Temps de réponse < 3 secondes
- **Données :** Calculs exacts selon les formules
- **Interface :** Navigation fluide et intuitive

## 📞 **Support**

### **En cas de problème**
1. Vérifier les logs de l'application
2. Consulter la documentation
3. Reprendre depuis la dernière étape réussie
4. Vérifier la cohérence des données

### **Ressources**
- **Documentation :** Fichiers .md fournis
- **Code source :** Commentaires dans le code
- **Base de données :** Schéma dans les modèles

## 🎉 **Succès du Test**

À la fin du test, vous devriez avoir :
- ✅ Une compréhension complète du système
- ✅ Testé toutes les fonctionnalités principales
- ✅ Validé le processus de délibération
- ✅ Vérifié la cohérence des données
- ✅ Confirmé la qualité de l'interface

**Temps total estimé : 2-3 heures**

---

*Guide créé pour faciliter le test complet d'Edusco* 