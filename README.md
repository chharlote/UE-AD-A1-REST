# UE-AD-A1-REST — Application Microservices de Réservation de Cinéma

Projet d'architecture distribuée basé sur 4 microservices REST indépendants développés en Python (Flask) et sécurisés par authentification JWT.

---

## Auteurs

- Titouan NICOLAS 
- Charlotte GERME

## Architecture du projet

| Service | Dossier | Port | URL locale | Rôle |
| :--- | :--- | :---: | :--- | :--- |
| **Movie** | `movie/` | `3200` | `http://localhost:3200` | Gestion du catalogue de films |
| **Booking** | `booking/` | `3201` | `http://localhost:3201` | Gestion des réservations de séances par utilisateur |
| **Schedule** | `schedule/` | `3202` | `http://localhost:3202` | Gestion de la programmation des films par date |
| **User** | `user/` | `3203` | `http://localhost:3203` | Gestion des utilisateurs et connexion |
| **Utils** | `utils/jwt.py` |  |  | Création et vérification des tokens JWT |


## Comment lancer le projet

### Option 1 : En local avec Python - Mode développement

1. Cloner le dépôt et installer les dépendances :
   ```bash
   git clone [https://github.com/chharlote/UE-AD-A1-REST.git](https://github.com/chharlote/UE-AD-A1-REST.git)
   cd UE-AD-A1-REST
   python -m venv .venv
   source .venv/bin/activate        # Sur Windows : .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Démarrer les 4 microservices** (ouvrir **4 terminaux** à la racine du projet) :

   >  Se placer dans le dossier UE-AD-A1-REST et exécuter les commandes suivantes dans chaque terminal :

     ```bash
     # Terminal 1 — Movie Service (port 3200)
     py -m src.movie.movie

     # Terminal 2 — Booking Service (port 3201)
     py -m src.booking.booking

     # Terminal 3 — Schedule Service (port 3202)
     py -m src.schedule.schedule

     # Terminal 4 — User Service (port 3203)
     py -m src.user.user
     ```

### Option 2 : Avec Docker Compose - Mode production

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

Les routes exige un jeton **JWT** valide pendant **1 heure**, à transmettre dans l'en-tête HTTP de chaque requête :

```http
Authorization: Bearer <VOTRE_TOKEN_JWT>
```

### Comptes pré-enregistrés pour tester (`user/databases/users.json`)
L'authentification via `POST /login` s'effectue avec l'`id` de l'utilisateur :

| Identifiant (`id`) | Nom | Rôle (`admin`) | Droits |
| :--- | :--- | :---: | :--- |
| `pam_beesly` | Pam Beesly | `true` | **Administrateur** (accès complet en lecture et écriture) |
| `chris_rivers` | Chris Rivers | `false` | **Utilisateur standard** (accès lecture) |
