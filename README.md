# Edusco - Plateforme de Gestion d'Institut Supérieur

Edusco est une application web Flask moderne pour la gestion complète d'un institut supérieur. Elle permet de gérer les années académiques, semestres, unités d'enseignement, matières, étudiants, enseignants, groupes et bien plus encore.

## 🚀 Fonctionnalités

### Gestion Académique
- **Années académiques** : Création et gestion des années d'études
- **Semestres** : Organisation des périodes d'enseignement
- **Unités d'enseignement** : Gestion des UEs avec crédits et coefficients
- **Matières** : Cours individuels avec volume horaire et enseignants
- **Groupes** : Organisation des étudiants par UE

### Gestion des Personnes
- **Étudiants** : Inscription, gestion des profils et statuts
- **Enseignants** : Gestion du personnel enseignant avec spécialités
- **Utilisateurs** : Système d'authentification et rôles

### Fonctionnalités Pédagogiques
- **Inscriptions** : Attribution des étudiants aux groupes
- **Notes** : Système de notation (préparé)
- **Absences** : Suivi des présences (préparé)
- **Emplois du temps** : Planning des cours (préparé)
- **Délibérations** : Processus d'évaluation (préparé)

## 🛠️ Technologies Utilisées

- **Backend** : Flask 2.3.3
- **Base de données** : MySQL avec SQLAlchemy
- **Authentification** : Flask-Login
- **Formulaires** : Flask-WTF avec WTForms
- **Interface** : Bootstrap 4 + AdminLTE
- **Migration** : Flask-Migrate avec Alembic
- **Sécurité** : Flask-Bcrypt pour le hachage des mots de passe

## 📋 Prérequis

- Python 3.8+
- MySQL 5.7+ ou MariaDB 10.2+
- pip (gestionnaire de paquets Python)

## 🚀 Installation

### 1. Cloner le repository
```bash
git clone <url-du-repository>
cd edusco
```

### 2. Créer un environnement virtuel
```bash
python -m venv edusco_env
```

### 3. Activer l'environnement virtuel

**Windows :**
```bash
edusco_env\Scripts\activate
```

**Linux/Mac :**
```bash
source edusco_env/bin/activate
```

### 4. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 5. Configuration de l'environnement

Créer un fichier `.env` à la racine du projet :
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=votre_cle_secrete_tres_longue_et_complexe
DATABASE_URL=mysql://utilisateur:mot_de_passe@localhost/edusco_db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=votre_email@gmail.com
MAIL_PASSWORD=votre_mot_de_passe_app
```

### 6. Configuration de la base de données

Créer une base de données MySQL :
```sql
CREATE DATABASE edusco_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'edusco_user'@'localhost' IDENTIFIED BY 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON edusco_db.* TO 'edusco_user'@'localhost';
FLUSH PRIVILEGES;
```

### 7. Initialiser la base de données
```bash
python scripts/initialiser_db.py
```

### 8. Lancer l'application
```bash
python app.py
```

L'application sera accessible à l'adresse : http://localhost:5000

## 👤 Identifiants par défaut

- **Email** : admin@edusco.com
- **Mot de passe** : admin123

⚠️ **Important** : Changez ces identifiants après la première connexion !

## 📁 Structure du Projet

```
edusco/
├── app/                          # Application principale
│   ├── __init__.py              # Configuration Flask
│   ├── config.py                # Configuration de l'app
│   ├── extensions.py            # Extensions Flask
│   ├── blueprints/              # Modules de l'application
│   │   ├── admin/              # Interface d'administration
│   │   ├── authentification/   # Gestion des connexions
│   │   ├── enseignant/         # Interface enseignants
│   │   └── principal/          # Interface publique
│   ├── models/                 # Modèles de données
│   │   ├── academique.py       # Modèles académiques
│   │   ├── pedagogique.py      # Modèles pédagogiques
│   │   └── utilisateur.py      # Modèles utilisateurs
│   ├── services/               # Logique métier
│   │   ├── academique.py       # Services académiques
│   │   └── authentification.py # Services d'auth
│   ├── forms/                  # Formulaires WTForms
│   ├── templates/              # Templates Jinja2
│   ├── static/                 # Fichiers statiques
│   └── utils/                  # Utilitaires
├── scripts/                    # Scripts utilitaires
├── tests/                      # Tests unitaires
├── requirements.txt            # Dépendances Python
├── app.py                      # Point d'entrée
└── README.md                   # Documentation
```

## 🔧 Configuration

### Variables d'environnement

| Variable | Description | Exemple |
|----------|-------------|---------|
| `FLASK_APP` | Application Flask | `app.py` |
| `FLASK_ENV` | Environnement | `development` ou `production` |
| `SECRET_KEY` | Clé secrète Flask | Chaîne aléatoire longue |
| `DATABASE_URL` | URL de la base de données | `mysql://user:pass@localhost/db` |
| `MAIL_SERVER` | Serveur SMTP | `smtp.gmail.com` |
| `MAIL_PORT` | Port SMTP | `587` |
| `MAIL_USE_TLS` | Utiliser TLS | `True` |
| `MAIL_USERNAME` | Email SMTP | `user@gmail.com` |
| `MAIL_PASSWORD` | Mot de passe SMTP | `app_password` |

### Configuration de la base de données

L'application utilise MySQL avec les paramètres suivants :
- **Encodage** : UTF-8
- **Collation** : utf8mb4_unicode_ci
- **Moteur** : InnoDB

## 🎯 Utilisation

### Interface d'Administration

1. **Connexion** : Utilisez les identifiants par défaut
2. **Années académiques** : Créez et gérez les années d'études
3. **Semestres** : Organisez les périodes d'enseignement
4. **Unités d'enseignement** : Définissez les UEs avec crédits
5. **Matières** : Créez les cours et assignez les enseignants
6. **Étudiants** : Inscrivez et gérez les étudiants
7. **Enseignants** : Gérez le personnel enseignant
8. **Groupes** : Organisez les étudiants par UE

### Workflow Typique

1. Créer une année académique
2. Créer les semestres
3. Créer les unités d'enseignement
4. Créer les matières et assigner les enseignants
5. Créer les groupes
6. Inscrire les étudiants
7. Assigner les étudiants aux groupes

## 🔒 Sécurité

- **Authentification** : Système de connexion sécurisé
- **Autorisation** : Gestion des rôles et permissions
- **Validation** : Validation côté serveur et client
- **Hachage** : Mots de passe hachés avec Bcrypt
- **CSRF** : Protection CSRF sur tous les formulaires

## 🧪 Tests

Pour exécuter les tests :
```bash
python -m pytest tests/
```

## 📊 Base de Données

### Tables Principales

- **annees_academiques** : Années d'études
- **semestres** : Périodes d'enseignement
- **unites_enseignement** : UEs avec crédits
- **matieres** : Cours individuels
- **etudiants** : Données des étudiants
- **enseignants** : Données des enseignants
- **groupes** : Groupes d'étudiants
- **inscriptions_groupes** : Inscriptions étudiants-groupes
- **utilisateurs** : Comptes utilisateurs

## 🚀 Déploiement

### Production

1. **Serveur** : Utilisez un serveur WSGI comme Gunicorn
2. **Base de données** : MySQL en production
3. **Proxy** : Nginx comme proxy inverse
4. **SSL** : Certificat SSL pour HTTPS
5. **Backup** : Sauvegardes régulières de la base de données

### Exemple avec Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 🤝 Contribution

1. Fork le projet
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Pour toute question ou problème :
- Ouvrez une issue sur GitHub
- Consultez la documentation
- Contactez l'équipe de développement

## 🔄 Mises à jour

### Migration de base de données
```bash
flask db upgrade
```

### Mise à jour des dépendances
```bash
pip install -r requirements.txt --upgrade
```

---

**Edusco** - Une solution complète pour la gestion d'institut supérieur 🎓 