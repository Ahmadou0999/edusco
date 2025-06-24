# 🎓 Edusco - Plateforme de Gestion d'Institut Supérieur

## 📋 Description

Edusco est une plateforme web moderne et complète pour la gestion administrative et pédagogique d'un institut supérieur. Développée avec Flask, elle offre une interface intuitive pour les administrateurs et enseignants.

## ✨ Fonctionnalités

### 🔐 Authentification et Rôles
- **Administrateur** : Accès complet à toutes les fonctionnalités
- **Enseignant** : Gestion de ses groupes, notes et absences

### 📚 Gestion Académique
- Gestion des étudiants et enseignants
- Unités d'enseignement et matières
- Années académiques et semestres
- Groupes pédagogiques

### 📊 Gestion Pédagogique
- Saisie de notes avec interface AJAX
- Gestion des absences et justifications
- Emplois du temps
- Délibérations et validation d'année

### 📈 Tableaux de Bord
- Statistiques en temps réel
- Graphiques et indicateurs
- Notifications et alertes

## 🛠️ Technologies Utilisées

- **Backend** : Flask 2.3.3
- **Base de données** : MySQL / SQLite
- **ORM** : SQLAlchemy avec Flask-SQLAlchemy
- **Authentification** : Flask-Login
- **Formulaires** : Flask-WTF / WTForms
- **Interface** : AdminLTE 3
- **Frontend** : HTML5, CSS3, JavaScript, AJAX

## 🚀 Installation

### Prérequis
- Python 3.8+
- MySQL (optionnel, SQLite par défaut)
- Git

### Étapes d'installation

1. **Cloner le repository**
```bash
git clone <url-du-repo>
cd edusco
```

2. **Créer l'environnement virtuel**
```bash
python -m venv edusco_env
```

3. **Activer l'environnement**
```bash
# Windows
edusco_env\Scripts\activate

# Linux/Mac
source edusco_env/bin/activate
```

4. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

5. **Configuration**
```bash
# Copier le fichier d'exemple
cp env_example.txt .env

# Éditer le fichier .env avec vos paramètres
```

6. **Initialiser la base de données**
```bash
flask db init
flask db migrate
flask db upgrade
```

7. **Lancer l'application**
```bash
python app.py
```

L'application sera accessible à l'adresse : `http://localhost:5000`

## 📁 Structure du Projet

```
edusco/
├── app/
│   ├── __init__.py              # Initialisation Flask
│   ├── config.py                # Configuration
│   ├── extensions.py            # Extensions Flask
│   ├── models/                  # Modèles de données
│   ├── services/                # Logique métier
│   ├── forms/                   # Formulaires
│   ├── blueprints/              # Modules fonctionnels
│   │   ├── admin/              # Administration
│   │   ├── enseignant/         # Interface enseignant
│   │   ├── authentification/   # Login/Logout
│   │   └── principal/          # Routes publiques
│   ├── templates/              # Templates HTML
│   ├── static/                 # CSS, JS, Images
│   └── utils/                  # Utilitaires
├── tests/                      # Tests unitaires
├── requirements.txt            # Dépendances
├── app.py                     # Point d'entrée
└── README.md                  # Documentation
```

## 🔧 Configuration

### Variables d'environnement (.env)

```env
# Application
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=votre_cle_secrete

# Base de données
DATABASE_URL=mysql://user:pass@localhost/edusco_db

# Email (optionnel)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=votre_email@gmail.com
MAIL_PASSWORD=votre_mot_de_passe_app
```

## 👥 Utilisateurs par Défaut

Après la première installation, un administrateur par défaut est créé :

- **Email** : admin@edusco.com
- **Mot de passe** : admin123

⚠️ **Important** : Changez ces identifiants après la première connexion !

## 🧪 Tests

```bash
# Lancer tous les tests
python -m pytest tests/

# Tests avec couverture
python -m pytest --cov=app tests/
```

## 📦 Déploiement

### Production avec Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Docker (optionnel)

```bash
docker build -t edusco .
docker run -p 5000:5000 edusco
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Contacter l'équipe de développement

## 🔄 Versions

- **v1.0.0** : Version initiale avec authentification et gestion de base
- **v1.1.0** : Ajout de la gestion pédagogique complète
- **v1.2.0** : Interface enseignant et délibérations

---

**Développé avec ❤️ pour la communauté éducative** 