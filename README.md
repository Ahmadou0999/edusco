# 🎓 Edusco - Plateforme de Gestion Académique

Une plateforme moderne de gestion académique pour les instituts d'enseignement supérieur, développée avec Flask et MySQL.

## 🚀 Fonctionnalités

- **Gestion des étudiants** : Inscription, suivi académique, bulletins
- **Gestion des enseignants** : Attribution des matières, saisie de notes
- **Gestion pédagogique** : Unités d'enseignement, groupes, emplois du temps
- **Validation des notes** : Système de validation par les administrateurs
- **Rapports et statistiques** : Analyses détaillées des performances
- **Interface moderne** : Design responsive avec AdminLTE

## 🛠️ Technologies Utilisées

- **Backend** : Flask (Python)
- **Base de données** : MySQL
- **Frontend** : HTML5, CSS3, JavaScript, Bootstrap 5, AdminLTE
- **Authentification** : Flask-Login, Flask-Bcrypt
- **ORM** : SQLAlchemy
- **Migration** : Alembic

## 📋 Prérequis

- Python 3.8+
- MySQL 8.0+
- Git
- WSL2 (Windows) ou Linux/Mac

## 🔧 Installation

### 1. Cloner le projet
```bash
git clone <URL_DU_REPO>
cd edusco
```

### 2. Créer l'environnement virtuel
```bash
python -m venv edusco_env
source edusco_env/bin/activate  # Linux/Mac
# ou
edusco_env\Scripts\activate     # Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration de la base de données

#### Créer la base de données MySQL
```sql
CREATE DATABASE edusco_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'edusco_user'@'localhost' IDENTIFIED BY 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON edusco_db.* TO 'edusco_user'@'localhost';
FLUSH PRIVILEGES;
```

#### Configurer les variables d'environnement
Créer un fichier `.env` à la racine du projet :
```env
# Configuration de la base de données
DATABASE_URL=mysql+pymysql://edusco_user:votre_mot_de_passe@localhost/edusco_db

# Configuration Flask
SECRET_KEY=votre_cle_secrete_tres_longue_et_complexe
FLASK_ENV=development
FLASK_DEBUG=True

# Configuration email (optionnel)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=votre_email@gmail.com
MAIL_PASSWORD=votre_mot_de_passe_app
```

### 5. Initialiser la base de données
```bash
# Créer les tables
flask db upgrade

# Initialiser les données de base
python scripts/initialiser_db.py
```

### 6. Créer les comptes utilisateurs
```bash
python scripts/creer_comptes_utilisateurs.py
```

## 🏃‍♂️ Lancement de l'application

```bash
# Activer l'environnement virtuel
source edusco_env/bin/activate  # Linux/Mac
# ou
edusco_env\Scripts\activate     # Windows

# Lancer l'application
python app.py
```

L'application sera accessible sur : http://127.0.0.1:5001

## 👥 Comptes de Test

### Administrateur
- **Email** : admin@edusco.com
- **Mot de passe** : admin123

### Enseignant
- **Email** : ousmane.ba@edusco.com
- **Mot de passe** : enseignant123

### Étudiant
- **Email** : etudiant@edusco.com
- **Mot de passe** : etudiant123

## 📁 Structure du Projet

```
edusco/
├── app/
│   ├── blueprints/          # Modules de l'application
│   ├── models/             # Modèles de données
│   ├── services/           # Logique métier
│   ├── templates/          # Templates HTML
│   ├── static/             # Fichiers statiques
│   └── forms/              # Formulaires
├── migrations/             # Migrations de base de données
├── scripts/                # Scripts utilitaires
├── tests/                  # Tests unitaires
├── requirements.txt        # Dépendances Python
├── app.py                  # Point d'entrée
└── README.md              # Ce fichier
```

## 🔄 Migrations de Base de Données

```bash
# Créer une nouvelle migration
flask db migrate -m "Description de la migration"

# Appliquer les migrations
flask db upgrade

# Revenir en arrière
flask db downgrade
```

## 🧪 Tests

```bash
# Lancer les tests
python -m pytest tests/

# Avec couverture
python -m pytest --cov=app tests/
```

## 📊 Fonctionnalités Principales

### Pour les Administrateurs
- Gestion des années académiques et semestres
- Gestion des étudiants et enseignants
- Validation des notes
- Génération de rapports
- Configuration du système

### Pour les Enseignants
- Saisie et validation des notes
- Gestion des absences
- Consultation des emplois du temps
- Génération de rapports pédagogiques

### Pour les Étudiants
- Consultation des notes et bulletins
- Emploi du temps personnel
- Historique des absences

## 🐛 Dépannage

### Problème de connexion à la base de données
1. Vérifier que MySQL est démarré
2. Vérifier les paramètres de connexion dans `.env`
3. Tester la connexion : `mysql -u edusco_user -p edusco_db`

### Problème de dépendances
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Problème de migrations
```bash
flask db stamp head
flask db migrate
flask db upgrade
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème :
- Créer une issue sur GitHub
- Contacter l'équipe de développement

---

**Développé avec ❤️ pour l'éducation** 