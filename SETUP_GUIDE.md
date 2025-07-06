# 🚀 Guide de Configuration - Edusco

## 📋 Prérequis pour le Développeur Distant

### ✅ Vérifications Système
- [ ] WSL2 installé et configuré
- [ ] MySQL Workbench installé
- [ ] Python 3.8+ installé
- [ ] Git installé
- [ ] VS Code installé (recommandé)

### 🔧 Configuration WSL2
```bash
# Vérifier la version de WSL
wsl --version

# Mettre à jour WSL
wsl --update

# Redémarrer WSL
wsl --shutdown
```

## 🗄️ Configuration MySQL

### 1. Installation MySQL sur WSL2
```bash
# Mettre à jour les paquets
sudo apt update

# Installer MySQL
sudo apt install mysql-server

# Démarrer MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# Sécuriser l'installation
sudo mysql_secure_installation
```

### 2. Configuration MySQL Workbench

#### Créer la connexion dans MySQL Workbench :
1. **Hostname** : `localhost` ou `127.0.0.1`
2. **Port** : `3306`
3. **Username** : `root` (puis créer un utilisateur spécifique)
4. **Password** : [mot de passe root]

#### Créer la base de données et l'utilisateur :
```sql
-- Se connecter en tant que root
mysql -u root -p

-- Créer la base de données
CREATE DATABASE edusco_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Créer l'utilisateur
CREATE USER 'edusco_user'@'localhost' IDENTIFIED BY 'votre_mot_de_passe_securise';

-- Accorder les privilèges
GRANT ALL PRIVILEGES ON edusco_db.* TO 'edusco_user'@'localhost';
FLUSH PRIVILEGES;

-- Vérifier
SHOW DATABASES;
SELECT User, Host FROM mysql.user;
```

## 🐍 Configuration Python

### 1. Vérifier Python
```bash
python3 --version
pip3 --version
```

### 2. Installer les outils nécessaires
```bash
# Installer pip si nécessaire
sudo apt install python3-pip

# Installer venv
sudo apt install python3-venv

# Installer les dépendances système
sudo apt install python3-dev default-libmysqlclient-dev build-essential
```

## 📦 Installation du Projet

### 1. Cloner le projet
```bash
# Dans WSL2
cd ~
git clone <URL_DU_REPO_EDUSCO>
cd edusco
```

### 2. Créer l'environnement virtuel
```bash
# Créer l'environnement
python3 -m venv edusco_env

# Activer l'environnement
source edusco_env/bin/activate

# Vérifier l'activation
which python
which pip
```

### 3. Installer les dépendances
```bash
# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt
```

### 4. Configuration des variables d'environnement
```bash
# Copier le fichier d'exemple
cp env_example.txt .env

# Éditer le fichier .env
nano .env
```

#### Contenu du fichier `.env` :
```env
# Configuration de la base de données
DATABASE_URL=mysql+pymysql://edusco_user:votre_mot_de_passe@localhost/edusco_db

# Configuration Flask
SECRET_KEY=votre_cle_secrete_tres_longue_et_complexe_ici
FLASK_ENV=development
FLASK_DEBUG=True

# Configuration email (optionnel)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=votre_email@gmail.com
MAIL_PASSWORD=votre_mot_de_passe_app
```

## 🗄️ Initialisation de la Base de Données

### 1. Créer les tables
```bash
# Activer l'environnement virtuel
source edusco_env/bin/activate

# Initialiser les migrations
flask db upgrade
```

### 2. Initialiser les données de base
```bash
# Exécuter le script d'initialisation
python scripts/initialiser_db.py
```

### 3. Créer les comptes utilisateurs
```bash
# Créer les comptes de test
python scripts/creer_comptes_utilisateurs.py
```

## 🏃‍♂️ Lancement de l'Application

### 1. Vérifications préalables
```bash
# Vérifier que MySQL est démarré
sudo systemctl status mysql

# Vérifier la connexion à la base
mysql -u edusco_user -p edusco_db -e "SELECT 1;"
```

### 2. Lancer l'application
```bash
# Activer l'environnement virtuel
source edusco_env/bin/activate

# Lancer l'application
python app.py
```

### 3. Accéder à l'application
- **URL** : http://127.0.0.1:5001
- **Compte Admin** : admin@edusco.com / admin123

## 🔧 Configuration VS Code

### 1. Installer les extensions recommandées
- **Python** (Microsoft)
- **Python Extension Pack**
- **MySQL** (cweijan)
- **GitLens**

### 2. Configuration du workspace
Créer un fichier `.vscode/settings.json` :
```json
{
    "python.defaultInterpreterPath": "./edusco_env/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "files.associations": {
        "*.html": "html",
        "*.css": "css",
        "*.js": "javascript"
    }
}
```

### 3. Configuration du debugger
Créer un fichier `.vscode/launch.json` :
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "app.py",
                "FLASK_ENV": "development"
            },
            "args": [
                "run",
                "--no-debugger",
                "--no-reload",
                "--host=127.0.0.1",
                "--port=5001"
            ],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```

## 🐛 Dépannage Courant

### Problème de connexion MySQL
```bash
# Vérifier le statut MySQL
sudo systemctl status mysql

# Redémarrer MySQL
sudo systemctl restart mysql

# Vérifier les logs
sudo tail -f /var/log/mysql/error.log
```

### Problème de dépendances Python
```bash
# Réinstaller les dépendances
pip install --force-reinstall -r requirements.txt

# Installer les dépendances système manquantes
sudo apt install python3-dev default-libmysqlclient-dev
```

### Problème de migrations
```bash
# Réinitialiser les migrations
flask db stamp head
flask db migrate
flask db upgrade
```

### Problème de permissions
```bash
# Donner les permissions sur le dossier
chmod -R 755 .
chmod -R 777 app/static/uploads
```

## 📊 Vérification de l'Installation

### 1. Tests de base
```bash
# Test de connexion à la base
python -c "from app import db; print('Connexion DB OK')"

# Test des modèles
python -c "from app.models import *; print('Modèles OK')"

# Test des services
python -c "from app.services import *; print('Services OK')"
```

### 2. Tests fonctionnels
- [ ] Accès à l'application : http://127.0.0.1:5001
- [ ] Connexion admin : admin@edusco.com / admin123
- [ ] Connexion enseignant : ousmane.ba@edusco.com / enseignant123
- [ ] Connexion étudiant : etudiant@edusco.com / etudiant123

## 🔄 Workflow de Développement

### 1. Démarrage quotidien
```bash
# Ouvrir WSL2
wsl

# Aller dans le projet
cd ~/edusco

# Activer l'environnement
source edusco_env/bin/activate

# Démarrer MySQL
sudo systemctl start mysql

# Lancer l'application
python app.py
```

### 2. Commandes utiles
```bash
# Voir les logs en temps réel
tail -f app.log

# Redémarrer l'application
pkill -f "python app.py"
python app.py

# Vider le cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -delete
```

## 📞 Support

En cas de problème :
1. Vérifier les logs : `tail -f app.log`
2. Vérifier la base de données : `mysql -u edusco_user -p edusco_db`
3. Consulter le README.md principal
4. Contacter l'équipe de développement

---

**🎯 Objectif** : Avoir une installation fonctionnelle d'Edusco en moins de 30 minutes ! 