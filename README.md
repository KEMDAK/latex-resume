# Kareem Mokhtar - LaTeX Resume

A professional one-page resume built with LaTeX, featuring a green terminal aesthetic that matches [kareem-mokhtar.com](https://kareem-mokhtar.com).

## Project Structure

```
latex-resume/
├── resume.tex                    # Main document (imports all sections)
├── resume-class.cls              # Custom LaTeX class for styling
├── sections/
│   ├── personal-info.tex         # Name, contact details, links
│   ├── sidebar-content.tex       # Languages, skills, activities
│   ├── education.tex             # Education entries
│   ├── publications.tex          # Publications
│   └── experience.tex            # Work experience (including commented entries)
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

### Updating Personal Information
Edit `sections/personal-info.tex` to update:
- Name, job title
- Phone, email, website
- LinkedIn, GitHub

### Updating Experience
Edit `sections/experience.tex` to:
- Add new positions
- Modify existing entries
- Uncomment archived entries (eSEED, separate Meta roles)

### Updating Skills/Languages
Edit `sections/sidebar-content.tex` to modify:
- Languages and proficiency levels
- Technical and soft skills
- Extracurricular activities

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
