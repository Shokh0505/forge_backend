# 🚀 Forge

**Ever wanted to take on a challenge, but didn’t?**  
**Tried to find others to join you, but couldn’t?**

**Forge** is your space to **create challenges**, **track progress**, and **connect with like-minded people** who want to grow, grind, and build — together.

---

## Features

-   🛠️ Create challenges with timelines
-   📊 Track progress of participants
-   💬 Chat with others in the challenge
-   🌱 Build a community with shared interests

---

## Tech Stack

-   Frontend: **Next.js**
-   Backend: **Django**
-   Communication: **REST API**
-   Styling: Your call (Tailwind, CSS, etc.)

---

## Getting Started

> _All commands assume a **Linux** environment. If you’re on Windows (👀), find the equivalents — or better yet, **switch to Linux**._

---

👉 Looking for the frontend? [Check out forge_frontend](https://github.com/Shokh0505/forge_frontend)

---

### Setup Project Directory

```bash
mkdir forge
cd forge
```

### Frontend Setup

1. **Clone the frontend repo and install dependencies:**

```bash
git clone https://github.com/Shokh0505/forge_frontend.git
cd forge_frontend
npm install
```

2. Create a .env file in the root (where package.json is):

```bash
touch .env
```

3. Add the following environment variables:

```bash
BACKEND_API_URL="http://127.0.0.1:8000/"
NEXT_PUBLIC_FRONTEND_URL="http://localhost:3000/"
```

### Backend setup

1. Go back to the main directory and clone the backend:

```bash
cd ..
git clone https://github.com/Shokh0505/forge_backend.git
cd forge_backend
```

2. (Optional but recommended) Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

3. Install the dependencies

```bash
pip install -r requirements.txt
```

4. Generate a Django secret key:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

5. Navigate into the backend directory and create a .env file:

```bash
cd backend
touch .env
```

6. Add your secret key to the .env:

```bash
DJANGO_SECRET_KEY=your_generated_key_here
```

### Running the app

-   Backend

```bash
python manage.py migrate
python manage.py runserver
```

-   Frontend

```bash
cd ../../forge_frontend
npm run dev
```

### ✅ You're Good to Go

Open your browser and visit:

```bash
http://localhost:3000
```

You should see the Forge app running. You're now ready to create and join challenges!
