<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interface Averis</title>
    <style>
        :root {
            --bg-color: #0f0f0f;
            --sidebar-color: #1a1a1a;
            --accent-color: #007bff;
            --text-color: #ffffff;
            --card-bg: #252525;
        }

        body {
            font-family: 'Segoe UI', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        /* --- SÉLECTION DE COMPTE (3 OPTIONS) --- */
        #account-selection {
            position: fixed;
            inset: 0;
            background: var(--bg-color);
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 30px;
            z-index: 1000;
        }

        .account-card {
            background: var(--card-bg);
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            width: 200px;
            cursor: pointer;
            transition: transform 0.3s, border 0.3s;
            border: 2px solid transparent;
        }

        .account-card:hover {
            transform: translateY(-10px);
            border-color: var(--accent-color);
        }

        .account-card i { font-size: 50px; margin-bottom: 15px; display: block; }

        /* --- LAYOUT PRINCIPAL --- */
        .sidebar {
            width: 250px;
            background: var(--sidebar-color);
            display: flex;
            flex-direction: column;
            padding: 20px;
            border-right: 1px solid #333;
        }

        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        /* --- TABS / ONGLETS --- */
        .tabs-container {
            display: flex;
            background: #111;
            padding: 10px 20px;
            gap: 10px;
        }

        .tab-btn {
            background: #333;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            transition: 0.2s;
        }

        .tab-btn.active {
            background: var(--accent-color);
        }

        .view-content {
            padding: 30px;
            display: none;
        }

        .view-content.active {
            display: block;
        }

        .hidden { display: none !important; }
    </style>
</head>
<body>

    <div id="account-selection">
        <div class="account-card" onclick="selectProfile('Administrateur')">
            <i>👤</i>
            <h3>Administrateur</h3>
        </div>
        <div class="account-card" onclick="selectProfile('Utilisateur')">
            <i>👥</i>
            <h3>Utilisateur</h3>
        </div>
        <div class="account-card" onclick="selectProfile('Invité')">
            <i>🌐</i>
            <h3>Invité</h3>
        </div>
    </div>

    <nav class="sidebar">
        <h2>AVERIS</h2>
        <hr style="width:100%; border: 0.5px solid #333;">
        <p>Solde : <span id="balance">Moune2010</span></p> <div style="margin-top: auto;">
            <button onclick="location.reload()" style="width:100%; padding:10px; cursor:pointer;">Déconnexion</button>
        </div>
    </nav>

    <main class="main-content">
        <div class="tabs-container">
            <button class="tab-btn active" onclick="showTab('dashboard')">Tableau de bord</button>
            <button class="tab-btn" onclick="showTab('settings')">Paramètres</button>
            <button class="tab-btn" onclick="showTab('logs')">Changelog</button>
        </div>

        <div id="dashboard" class="view-content active">
            <h1>Bienvenue</h1>
            <p id="profile-info"></p>
        </div>

        <div id="settings" class="view-content">
            <h1>Paramètres</h1>
            <p>Ici, vous pouvez configurer vos préférences.</p>
        </div>

        <div id="logs" class="view-content">
            <h1>Dernières mises à jour</h1>
            <ul id="changelog-list">
                <li>Correction mineure de l'interface utilisateur.</li>
                <li>Optimisation de la base de données.</li>
            </ul>
        </div>
    </main>

    <script>
        function selectProfile(type) {
            // Cacher l'écran de sélection
            document.getElementById('account-selection').classList.add('hidden');
            
            // Date de création automatique (Règle du 08/02/2026)
            const creationDate = new Date().toLocaleDateString('fr-FR');
            
            document.getElementById('profile-info').innerHTML = `
                <strong>Profil :</strong> ${type}<br>
                <strong>Date de création :</strong> ${creationDate}
            `;
            
            console.log(`Profil ${type} chargé avec succès le ${creationDate}.`);
        }

        function showTab(tabId) {
            // Gestion de l'affichage des onglets
            document.querySelectorAll('.view-content').forEach(view => {
                view.classList.remove('active');
            });
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });

            document.getElementById(tabId).classList.add('active');
            event.currentTarget.classList.add('active');
        }
    </script>
</body>
</html>
