# UE-AD-A1-REST — Application Microservices de Réservation de Cinéma

Projet d'architecture distribuée basé sur 4 microservices REST indépendants développés en Python (Flask) et sécurisés par authentification JWT.

---

## Architecture du projet

| Service | Dossier | Port | URL locale | Rôle |
| :--- | :--- | :---: | :--- | :--- |
| **Movie** | `movie/` | `3200` | `http://localhost:3200` | Gestion du catalogue de films |
| **Booking** | `booking/` | `3201` | `http://localhost:3201` | Gestion des réservations de séances par utilisateur |
| **Schedule** | `schedule/` | `3202` | `http://localhost:3202` | Gestion de la programmation des films par date |
| **User** | `user/` | `3203` | `http://localhost:3203` | Gestion des utilisateurs et connexion |
| **Utils** | `utils/jwt.py` |  |  | Création et vérification des tokens JWT |

### Communication inter-services
* **Booking (`3201`)** interroge **Movie (`3200`)** et **Schedule (`3202`)** lors d'un `POST /bookings` afin de vérifier que le film existe et qu'il est bien programmé à la date demandée.
* **Schedule (`3202`)** interroge **Movie (`3200`)** lors de l'ajout d'une séance (`POST /times/` ou `POST /times/<date>/movies`) pour valider l'existence des films.

---

## Comment lancer le projet

### Option 1 : En local avec Python (recommandé pour le développement)

1. Cloner le dépôt et installer les dépendances :
   ```bash
   git clone [https://github.com/chharlote/UE-AD-A1-REST.git](https://github.com/chharlote/UE-AD-A1-REST.git)
   cd UE-AD-A1-REST
   python -m venv .venv
   source .venv/bin/activate        # Sur Windows : .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Démarrer les 4 microservices** (ouvrir **4 terminaux** à la racine du projet) :

   > ⚠️ Chaque service charge son fichier `./databases/*.json` depuis son propre dossier et importe `jwt.py` depuis `utils/`. Il faut donc se placer dans le répertoire du service et définir `PYTHONPATH=../utils`.

   * **Linux / macOS :**
     ```bash
     # Terminal 1 — Movie Service (port 3200)
     cd movie && PYTHONPATH=../utils python movie.py

     # Terminal 2 — Booking Service (port 3201)
     cd booking && PYTHONPATH=../utils python booking.py

     # Terminal 3 — Schedule Service (port 3202)
     cd schedule && PYTHONPATH=../utils python schedule.py

     # Terminal 4 — User Service (port 3203)
     cd user && PYTHONPATH=../utils python user.py
     ```

   * **Windows (PowerShell) :**
     ```powershell
     # Terminal 1
     cd movie; $env:PYTHONPATH="../utils"; python movie.py

     # Terminal 2
     cd booking; $env:PYTHONPATH="../utils"; python booking.py

     # Terminal 3
     cd schedule; $env:PYTHONPATH="../utils"; python schedule.py

     # Terminal 4
     cd user; $env:PYTHONPATH="../utils"; python user.py
     ```

### Option 2 : Avec Docker Compose

1. Cloner le dépôt :
```bash
   git clone [https://github.com/chharlote/UE-AD-A1-REST.git](https://github.com/chharlote/UE-AD-A1-REST.git)
```

2. Lancer les conteneurs Docker Compose :
```bash
docker compose up --build
```
Les 4 conteneurs sont exposés sur les ports `3200`, `3201`, `3202` et `3203`.

---

## Liens rapides & Documentation interactive (Swagger)

Une fois les services démarrés, vous pouvez accéder directement aux interfaces suivantes dans votre navigateur :

* **Swagger UI — Movie Service :** [http://localhost:3200/docs](http://localhost:3200/docs)
* **Swagger UI — Schedule Service :** [http://localhost:3202/docs](http://localhost:3202/docs) 

* **Accueil Movie :** [http://localhost:3200/](http://localhost:3200/)
* **Accueil Booking :** [http://localhost:3201/](http://localhost:3201/)
* **Accueil Schedule :** [http://localhost:3202/](http://localhost:3202/)
* **Accueil User :** [http://localhost:3203/](http://localhost:3203/)

---

## Authentification (JWT)

La majorité des routes exige un jeton **JWT** valide pendant **1 heure**, à transmettre dans l'en-tête HTTP de chaque requête :

```http
Authorization: Bearer <VOTRE_TOKEN_JWT>
```

### Comptes pré-enregistrés pour tester (`user/databases/users.json`)
L'authentification via `POST /login` s'effectue avec l'`id` de l'utilisateur :

| Identifiant (`id`) | Nom | Rôle (`admin`) | Droits |
| :--- | :--- | :---: | :--- |
| `pam_beesly` | Pam Beesly | `true` | **Administrateur** (accès complet en lecture et écriture) |
| `chris_rivers` | Chris Rivers | `false` | **Utilisateur standard** (accès lecture) |

---

## Liste complète des routes

### 1. User Service (`http://localhost:3203`)

| Méthode | Route | Accès | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/` | Public | Page d'accueil du service |
| `POST` | `/login` | Public | Génère un token JWT pour un utilisateur | 
| `GET` | `/users` |  Admin | Liste tous les utilisateurs | 
| `POST` | `/users` |  Admin | Crée un nouvel utilisateur | 
| `PUT` | `/users` | Token | Modifie `name` et `last_active` d'un utilisateur | 

---

### 2. Movie Service (`http://localhost:3200`)

| Méthode | Route | Accès | Description | 
| :--- | :--- | :---: | :--- | 
| `GET` | `/` | Public | Page d'accueil du service 
| `GET` | `/docs` | Public | Documentation interactive Swagger UI 
| `GET` | `/openapi.yaml` | Public | Spécification OpenAPI 3.0.3 
| `GET` | `/movies` | Token | Liste les films (filtres optionnels) 
| `GET` | `/movies/<movieid>` | Token | Récupère un film par son ID 
| `POST` | `/movies` | Admin | Ajoute un film (UUID généré auto.)
| `PUT` | `/movies/<movieid>` | Admin | Met à jour un film existant 
| `DELETE` | `/movies/<movieid>` | Admin | Supprime un film 

---

### 3. Schedule Service (`http://localhost:3202`)

| Méthode | Route | Accès | Description | 
| :--- | :--- | :---: | :--- | 
| `GET` | `/` | Public | Page d'accueil du service 
| `GET` | `/docs` | Public | Documentation interactive Swagger UI 
| `GET` | `/openapi.yaml` | Public | Spécification OpenAPI 3.0.3 
| `GET` | `/json` | Token | Liste toute la programmation 
| `GET` | `/timesbydate` | Token | Programmation pour une date donnée
| `POST` | `/times/` | Admin | Crée une programmation pour une date 
| `POST` | `/times/<date>/movies` | Admin | Ajoute des films à une date existante 
| `DELETE` | `/times/<date>/<movie_id>` | Admin | Retire un film d'une date programmée 
| `DELETE` | `/times/<date>` | Admin | Supprime toute la programmation d'une date 

---

### 4. Booking Service (`http://localhost:3201`)

| Méthode | Route | Accès | Description |
| :--- | :--- | :---: | :--- | 
| `GET` | `/` | Public | Page d'accueil du service |
| `GET` | `/bookings` | Token  | Réservations de l'utilisateur connecté (ou **toutes** si Admin) 
| `POST` | `/bookings` | Token | Réserve un film à une date donnée 
| `DELETE` | `/bookings` | Token | Annule une réservation de l'utilisateur connecté
| `DELETE` | `/bookings/<user_id>` | Admin | Supprime toutes les réservations d'un utilisateur

---