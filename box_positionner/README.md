# Box positionner

Outil web pour dessiner des zones (boîtes) sur une image et exporter un JSON de positionnement (coordonnées en %), avec support parent/enfant.

## split-layouts.js

Script pour découper un **JSON complet** (export de l’outil) en **plusieurs JSON “un niveau”** : un fichier par boîte non feuille, contenant uniquement ses **enfants directs** avec coordonnées **relatives au parent**. Pratique pour alimenter des composants (ex. React Native) qui reçoivent chacun leur layout en props.

### Usage

```bash
node split-layouts.js <fichier-complet.json> [--out <dossier>] [--root <nom>]
```

- **`fichier-complet.json`** : export du box-positionner (tableau de boîtes avec `id`, `parentId`, `xPct`, `yPct`, `wPct`, `hPct`, optionnel `name`).
- **`--out <dossier>`** : dossier de sortie (défaut : `layouts/` à côté du fichier d’entrée).
- **`--root <nom>`** : en plus, génère `<nom>_layout.json` avec les boîtes **racine** (`parentId === null`), pour le niveau écran.

### Fichiers générés

- Pour chaque boîte qui a au moins un enfant : **`<nom-boite>_layout.json`** (nom normalisé : minuscules, espaces → tirets, caractères spéciaux retirés). Si la boîte n’a pas de `name`, le fichier s’appelle **`box-<id>_layout.json`**.
- Chaque fichier contient un **tableau** d’objets : les enfants directs de la boîte, avec **un seul niveau** et des coordonnées **en % du parent** (`xPct`, `yPct`, `wPct`, `hPct`), plus `id` et éventuellement `name` (pas de `parentId` dans ces JSON). Le script réutilise les positions relatives déjà exportées par l’outil (`parent.xPct`, etc.) ; si elles sont absentes, il les recalcule à partir des absolues.

### Exemple

JSON complet avec une racine "profile" (id 1), une racine "characteristics" (id 2), et des enfants sous "profile" (id 3, 4) :

```bash
node split-layouts.js ecran-complet.json --out ./layouts --root screen
```

Génère par exemple :

- **`screen_layout.json`** : les deux boîtes racine (profile, characteristics) en % de l’écran.
- **`profile_layout.json`** : les boîtes d’id 3 et 4, en % de la boîte "profile".
- **`characteristics_layout.json`** : (si cette boîte a des enfants) ses enfants en % d’elle.

Chaque composant peut alors charger uniquement son fichier (`screen_layout.json`, `profile_layout.json`, etc.) et le recevoir en props.

---

## LayoutView (React Native)

Composant réutilisable pour positionner des sous-composants selon un layout (JSON généré par l’outil ou par `split-layouts`).

### Idée

- Un **conteneur** déclare le layout qu’il utilise (`layout={...}` ou **`layoutKey="..."`** pour le récupérer depuis le contexte).
- Chaque **sous-composant** indique dans quelle boîte il doit être placé avec **`layoutBoxId`** (id numérique) ou **`layoutBoxName`** (nom de la boîte).

Pour **ne pas importer le JSON à chaque niveau** : enregistre tous les layouts une fois avec **LayoutProvider**, puis utilise **`layoutKey`** dans chaque LayoutView. Le composant récupère lui‑même le layout dans le contexte.

### API

**LayoutView**

| Prop | Description |
|------|-------------|
| `layout` | Tableau de boîtes (ex. contenu d’un `*_layout.json`). Optionnel si `layoutKey` est utilisé. |
| `layoutKey` | Clé pour récupérer le layout depuis le `LayoutProvider` (évite d’importer le JSON ici). |
| `style` | Style optionnel du conteneur (par défaut : `position: relative`, 100% × 100%). |
| `children` | Enfants avec **`layoutBoxId`** et/ou **`layoutBoxName`** pour être positionnés. |

**LayoutProvider** (optionnel) : enregistre les layouts une fois (ex. à la racine). Props : `layouts` = objet `{ clé: tableau }`, ex. `{ screen: require('./layouts/screen_layout.json'), profile: require('./layouts/profile_layout.json') }`.

- **`layoutBoxId`** : id de la boîte dans le layout (number).
- **`layoutBoxName`** : nom de la boîte dans le layout (string).

Un enfant sans `layoutBoxId` ni `layoutBoxName` est rendu tel quel.

### Exemple avec LayoutProvider (sans importer le JSON à chaque niveau)

```jsx
const { LayoutView, LayoutProvider } = require('./box_positionner/LayoutView');

// Une seule fois : enregistrer tous les layouts (ex. à la racine)
const layouts = {
  screen: require('./layouts/screen_layout.json'),
  profile: require('./layouts/profile_layout.json'),
  characteristics: require('./layouts/characteristics_layout.json'),
};

function App() {
  return (
    <LayoutProvider layouts={layouts}>
      <Screen />
    </LayoutProvider>
  );
}

function Screen() {
  return (
    <LayoutView layoutKey="screen" style={{ flex: 1 }}>
      <ProfileView layoutBoxName="profile" />
      <CharacteristicsView layoutBoxName="characteristics" />
    </LayoutView>
  );
}

function ProfileView() {
  return (
    <LayoutView layoutKey="profile">
      <Avatar layoutBoxName="avatar" />
      <Name layoutBoxName="name" />
    </LayoutView>
  );
}
```

- **LayoutProvider** : enregistre les JSON une fois (clés `screen`, `profile`, `characteristics`).
- **LayoutView layoutKey="screen"** : récupère le layout dans le contexte, pas d’import dans le composant.
- **LayoutView layoutKey="profile"** : idem pour ProfileView ; les sous-composants ont `layoutBoxName="avatar"` / `"name"`.

### Intégration dans ton projet

- Copie **`LayoutView.js`** dans ton projet React Native (ou garde-le dans `box_positionner` et importe depuis ce chemin).
- **Sans importer le JSON à chaque niveau** : enveloppe l’app (ou une branche) avec **LayoutProvider** et passe `layouts={{ screen: require('./layouts/screen_layout.json'), ... }}`. Dans chaque composant utilise **`layoutKey="screen"`** (ou la clé correspondante) : LayoutView récupère lui‑même le layout dans le contexte.
- Tu peux aussi continuer à passer **`layout={require('./layouts/xxx_layout.json')}`** ou **`layout={array}`** si tu préfères.
- Le conteneur `LayoutView` a `width: 100%`, `height: 100%` ; donne-lui une taille (ex. parent avec `flex: 1`) pour que les % fonctionnent correctement.
