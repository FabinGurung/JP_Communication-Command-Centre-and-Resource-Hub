# Human file navigation

The human guide is a single HTML file in the existing Drive guide slot. Its
original Markdown edition is retained in the navigation archive. The file opens
directly in a browser after download; Google Drive does not execute HTML as a
hosted application. `files/` is the public, empty browser-local reader. A user can
choose the saved HTML there; DOMParser reads only its data block and never runs
code from the selected file. No private inventory or spreadsheet cells are
committed to GitHub, uploaded by the reader, or saved in browser storage.

The private guide links to original file IDs. It contains derived file-navigation
metadata, not additional working Google Sheets. Folder diagrams are generated
from those same parent IDs. SVG is the default accessible view. The optional
Three.js 0.186.1 view fetches the pinned library only after selection and has an
SVG-renderer fallback when WebGL is unavailable. Positions represent an abstract folder layout, not GIS or building
geometry. The guide describes inventory freshness explicitly; a complete scan
does not mean every folder has completed human-navigation review.

Current authorization excludes `98_INTAKE_STAGING`, which the owner is editing.
This work does not read, rename, move or classify anything inside that branch.
The remaining previously selected branches are JP, AEC Knowledge and Private
Sensitive; work on other modules or their repositories is not implied.

Build source is in `tools/drive-navigator/`:

```sh
cd tools/drive-navigator
npm ci --ignore-scripts
npm run check
npm run build
cd ../..
python scripts/test_drive_navigator.py
python scripts/build_drive_navigator.py --inventory /private/inventory.jsonl --spec /private/navigation-spec.json --output /private/Start_Here_Files_and_Sheets.html
```

Private inputs and outputs must remain outside this public checkout. The builder
rejects duplicate IDs, disconnected paths, cycles and excluded staging input.
Only the empty application shell is admitted to the Pages artifact. TypeScript
is the maintained source; the browser executes its compiled JavaScript and CSS.
The existing Sheets → publishing Sheet → validated JSON → Actions → Pages
contract and its pending Google identity setup remain unchanged.
