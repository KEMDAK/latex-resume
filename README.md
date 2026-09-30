# Kareem Mokhtar - LaTeX Resume

A professional one-page resume built with LaTeX, featuring a green terminal aesthetic that matches [kareem-mokhtar.com](https://kareem-mokhtar.com).

## Single source of truth

`resume.yaml` is the source of truth for all resume content. `scripts/generate.py`
generates the 5 files under `sections/` from it — **do not edit those `.tex`
files by hand**; your changes will be overwritten on the next generation.

The same generator also produces the website data
(`client/src/data/resume.ts` and the meta descriptions in `client/index.html`)
in the [personal-resume-website](https://github.com/KEMDAK/personal-resume-website)
repo. The only website content *not* covered is `client/src/data/projects.ts`
(the project portfolio), which is still edited manually.

**Workflow:** edit `resume.yaml` → run
`python3 scripts/generate.py --website-repo ../personal-resume-website`
(or just push — CI does it for you) → the `build-and-deploy` workflow compiles
both PDFs, copies them plus the website data into the website repo, and GitHub
Pages redeploys automatically.

Parked experience (real roles kept for future use, e.g. the separate Meta entries
and the eSEED internship) lives in `resume.yaml` as commented-out `latex_only`
entries — uncomment one and it is generated back into the PDF automatically.

## Project Structure

```
latex-resume/
├── resume.yaml                   # SOURCE OF TRUTH - all resume content lives here
├── scripts/
│   └── generate.py               # Generates sections/*.tex + website data from resume.yaml
├── resume.tex                    # Main document (imports all sections)
├── resume-class.cls              # Custom LaTeX class for styling
├── sections/                     # GENERATED - do not edit by hand
│   ├── personal-info.tex         # Name, contact details, links
│   ├── sidebar-content.tex       # Languages, skills, activities
│   ├── education.tex             # Education entries
│   ├── publications.tex          # Publications
│   └── experience.tex            # Work experience
├── fonts/
│   └── segoeuib.ttf              # Segoe UI Bold for headings
├── output/
│   └── resume.pdf                # Generated PDF
├── .gitignore                    # Git ignore rules
├── LICENSE.md                    # MIT License
└── README.md                     # This file
```

## Compilation

### Requirements
- XeLaTeX (TeX Live 2018 or later recommended)
- Required packages: fontspec, fontawesome, tikz, xcolor, textpos, hyperref, enumitem, smartdiagram

### Using Overleaf
1. Upload all files to Overleaf
2. Set compiler to **XeLaTeX**
3. Set main document to **resume.tex**
4. Compile

### Using Command Line
```bash
xelatex resume.tex
```

## Customization

> All resume content (personal info, experience, education, skills, languages,
> publications, volunteer/teaching, certifications) is edited in `resume.yaml`
> (see "Single source of truth" above), **not** in the `.tex` files directly.
> The PDF keeps a condensed one-page rendering while the website shows the full
> detail — the differences are intentional.

### Restoring parked experience
Uncomment the relevant `latex_only` entry in `resume.yaml` (e.g. eSEED, separate
Meta roles) and regenerate — it appears back in the PDF automatically.

### Color Scheme
The resume uses a green terminal aesthetic:
- **Sidebar (dark background)**: Bright green `#00ff00`
- **Main content (light background)**: Darker green `#00aa00`

To customize colors, edit `resume-class.cls` and modify:
- `sidegreen` - Bright green for sidebar elements
- `pblue` - Green for main content headings
- `sidecolor` - Sidebar background color

## Credits

This template is based on elements from several LaTeX resume templates:
1. [Carmine Spagnuolo's Twenty Seconds Curriculum Vitae](https://github.com/spagnuolocarmine/TwentySecondsCurriculumVitae-LaTex)
2. [Carmine Benedetto's Smart Fancy LaTeX CV](https://github.com/neoben/smart-fancy-latex-cv)
3. [Adrien Friggeri's Fancy CV](https://www.sharelatex.com/templates/52fb8c1f33621a613683ecad)

## License

MIT License - See [LICENSE.md](LICENSE.md) for details.
