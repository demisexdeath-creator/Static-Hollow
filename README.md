# Static Hollow: the official website

The official website and wiki for **Static Hollow**, the creepypasta horror mod for Minecraft 26.3 by Death.
Plain HTML, CSS and a little JavaScript. No server, no build step needed to view or host it.

Written against mod version **1.63.3** (Fabric and Forge), from the mod's own README, language
file and source code.

## Look at it

Open `index.html` in a browser. Everything works straight from the folder, including search
and the fonts.

## Put it online with GitHub Pages (free)

1. Create a new repository on GitHub (for example `static-hollow-wiki`).
2. Upload everything in this folder to the root of the repository (drag the files and folders
   into "Add file > Upload files", or push with git).
3. In the repository, go to **Settings > Pages**. Under "Build and deployment", choose
   **Deploy from a branch**, branch `main`, folder `/ (root)`, and save.
4. After a minute the site is live at `https://<your-username>.github.io/<repository-name>/`.

The `_build` folder is skipped by GitHub Pages automatically (folders starting with `_` aren't
published), so it stays private to you.

One detail: GitHub Pages shows `404.html` for any missing page. Its links assume the site sits at
the top of the domain. If your site lives at `.../<repository-name>/`, open `404.html` and add
`<base href="/<repository-name>/">` right after `<head>` so its links and styles work from any
depth.

Other free hosts work the same way: Netlify, Cloudflare Pages, Neocities. Upload the folder.

The quickest of those: go to https://app.netlify.com/drop and drag this folder onto the page. It's
online in seconds at an address like `static-hollow.netlify.app` (make a free account to keep it
and pick the name).

### Your own address

For an address like `statichollow.com`, buy the domain from any registrar (around 10 to 15 USD a
year), then:

- **GitHub Pages:** Settings > Pages > Custom domain, type the domain and save. At your
  registrar, point the domain at GitHub as its instructions show (a `CNAME` record for `www`, and
  four `A` records for the bare domain). Tick "Enforce HTTPS" once it appears.
- **Netlify:** Domain management > Add a domain, then follow the DNS steps it shows.

With a custom domain the site sits at the top of the domain, so `404.html` works as it is.

## Fill in the TODOs

The public site shows only what the mod's files confirm. Anything they didn't settle (CurseForge
links, chapter names one to four, a few drop rates, screenshots still missing...) has a TODO note
in the page sources, and the public build hides those notes. Every one is listed, page by page,
in `_build/TODO.md`.

To see the notes on the pages while you work, build with `python3 _build/build.py --drafts`.
That shows them as amber boxes and adds a `todo.html` page listing them all. Build without
`--drafts` again before you upload, so visitors don't see them.

You can edit the site two ways. Pick one:

- **Edit the HTML pages directly.** Simple. The sidebar is repeated in every page, so a new
  sidebar link means editing each page.
- **Edit the sources and rebuild.** The page contents live in `_build/src/` (one fragment per
  page, with a small header of title, subtitle and description). Change them, then run
  `python3 _build/build.py` from this folder. It rewrites every page with the shared sidebar
  and top bar, and regenerates the search index and `_build/TODO.md`. It overwrites the HTML
  pages, so don't mix this with editing the pages by hand. The sidebar and chapter list are set
  at the top of `_build/build.py`.

CSS, JavaScript and images live in `assets/` and are edited there directly either way.

## Adding screenshots

The pages already use 21 of your CurseForge screenshots (in `assets/img/shots/`, scaled to
1280 pixels wide). A few pages still have "NO SIGNAL" test-card placeholders where a screenshot
belongs. Put images in `assets/img/shots/` and replace the placeholder with:

```html
<figure class="figure figure--shot">
  <img src="../assets/img/shots/your-screenshot.jpg" alt="What it shows" width="1280" height="720">
  <figcaption>Caption.</figcaption>
</figure>
```

(Use `assets/...` without `../` on pages in the top folder.)

## What's where

```
index.html            Home (the main-menu scene is rebuilt from the mod's own title layers)
story/                Story overview and one page per chapter (1 to 8)
entities/             Bestiary and case files for the bosses and major creatures
places/               Every location, plus pages for the major ones
items/                Items and blocks
lore/                 Notes and books (word for word), tapes and broadcasts, the Watcher's lines
advancements.html     Every advancement
music.html            The soundtrack: every track and when it plays
survival.html         Cold, thirst, seasons and the rest of the world's systems
install.html, faq.html, credits.html
404.html              "Signal lost"
assets/css            style.css (the theme), fonts.css (embedded fonts)
assets/js             site.js (menu, search, home scene), search-index.js (generated)
assets/fonts          The font files and their licences (SIL Open Font License)
assets/img            The mod's menu layers, item textures, cover art and screenshots
_build/               Page sources, the build script and TODO.md (not needed to view the site)
```

## Credits

Static Hollow is by Death. Art on this site (the menu layers, item textures, cover and screenshots)
is the mod's own. Fonts: Big Shoulders Display, Spectral and Courier Prime, all under the SIL Open
Font License. Not an official Minecraft product; not approved by or associated with Mojang or
Microsoft.
