#!/usr/bin/env python3
"""
generate.py — regenerate resume sources from resume.yaml (single source of truth).

Usage:
    python3 scripts/generate.py [--website-repo PATH] [--check]

Outputs:
    sections/*.tex                                   (in this repo)
    <website-repo>/client/src/data/resume.ts
    <website-repo>/client/index.html                 (meta descriptions only)

With --check, exits non-zero if any generated file differs from what's on disk
(without writing anything). Useful for local verification before pushing.
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# LaTeX helpers
# ---------------------------------------------------------------------------

BANNER = "%" + "-" * 88


def banner(title: str) -> str:
    return f"{BANNER}\n%\t {title}\n{BANNER}\n"


def tex_escape(s: str) -> str:
    """Escape LaTeX special characters in plain-text strings."""
    return (
        s.replace("\\", "\\textbackslash{}")
        .replace("{", "\\{")
        .replace("}", "\\}")
        .replace("$", "\\$")
        .replace("&", "\\&")
        .replace("#", "\\#")
        .replace("_", "\\_")
        .replace("%", "\\%")
        .replace("~", "\\textasciitilde{}")
        .replace("^", "\\textasciicircum{}")
    )


# ---------------------------------------------------------------------------
# sections/*.tex
# ---------------------------------------------------------------------------

def gen_personal_info(p: dict) -> str:
    lines = [
        banner("PERSONAL INFORMATION"),
        f"\\cvname{{{p['name']}}}",
        f"\\cvjobtitle{{{p['job_title_tex']}}}",
        f"\\cvlinkedin{{{p['linkedin']}}}",
        f"\\cvgithub{{{p['github']}}}",
        f"\\cvnumberphone{{{p['phone']}}}",
        f"\\cvsite{{{p['site']}}}",
        f"\\cvmail{{{p['email']}}}",
        "",
    ]
    return "\n".join(lines)


def gen_education(entries: list) -> str:
    out = [banner("EDUCATION"), "\\section{Education}", "\\begin{twenty}"]
    for e in entries:
        degree_line = f"{e['degree_short']}, {e.get('field_tex', e['field'])}{e.get('extra_tex', '')}"
        item = [
            "    \\twentyitem",
            f"        {{{e.get('start_tex', e['start'])}}}",
            f"        {{{e['end']}}}",
            "        {\\href{%s}{%s}}" % (e.get("school_url_tex", e["school_url"]),
                                         e.get("school_tex", e["school"])),
            "        {}",
            f"        {{{degree_line}}}",
        ]
        if e.get("trailing_break_tex", True):
            item.append("        {\\\\}")
        out.append("\n".join(item))
    out.append("\\end{twenty}")
    out.append("")
    return "\n".join(out)


def gen_publications(pubs: list) -> str:
    out = [banner("PUBLICATIONS"), "\\section{Publications}"]
    for p in pubs:
        out.append(
            "\\href{%s}{\\textbf{%s}, %s. \"%s.\" %s.}"
            % (p["url"], p["first_author"], p["other_authors"], p["title"], p["venue"])
        )
    out.append("")
    return "\n".join(out)


def _tex_entry_block(e: dict) -> str:
    """Render one \\twentyitem experience entry (LaTeX rendering)."""
    lat = e.get("latex", {}) or {}
    title = e.get("title_tex") or tex_escape(e["title"])
    company = e.get("company_tex") or tex_escape(e["company"])
    url = e.get("company_url_tex") or e.get("company_url", "")
    bullets = e.get("bullets_tex") or lat.get("bullets")
    if bullets is None:
        bullets = [tex_escape(b) for b in e.get("bullets", [])]
    # Entry banners keep the same 89-char line width: 4 spaces + % + 84 dashes.
    entry_banner = "    %" + "-" * 84
    lines = [
        entry_banner,
        f"    % {e['tex_comment']}",
        entry_banner,
        "    \\twentyitem",
        f"        {{{e['start']}}}",
        f"        {{{e['end']}}}",
        f"        {{{title}}}",
        "        {\\large\\textbf{\\href{%s}{%s}}}" % (url, company),
        "        {",
        "            \\begin{itemize}",
    ]
    lines += [f"                \\item {b}" for b in bullets]
    lines += [
        "            \\end{itemize}",
        "        }",
        "        {\\\\}",
    ]
    return "\n".join(lines)


def gen_experience(entries: list) -> str:
    # Preserve yaml order; web-excluded entries sit inline where defined.
    tex_entries = [e for e in entries
                   if (e.get("web") or {}).get("exclude") or not (e.get("latex") or {}).get("exclude")]
    out = [banner("EXPERIENCE"), "\\section{Experience}", "\\begin{twenty}"]
    out.append("\n\n".join(_tex_entry_block(e) for e in tex_entries))
    out.append("\\end{twenty}")
    out.append("")
    return "\n".join(out)


def gen_sidebar(d: dict) -> str:
    out = [banner("SIDEBAR CONTENT: Languages, Skills, Activities")]
    # Languages
    out.append("% Command for printing spoken languages")
    out.append("\\newcommand\\languages{")
    out.append("\\begin{itemize}[leftmargin=5mm]")
    for lang in d["languages"]:
        out.append(
            "    \\item \\makebox[2.9cm]{%s\\hfill} %s"
            % (lang["name"], lang["level"])
        )
    out.append("\\end{itemize}")
    out.append("}")
    out.append("")
    # Skills
    out.append("% Command for printing skills")
    out.append("\\newcommand\\skills{")
    out.append("\\begin{itemize}[leftmargin=5mm]")
    for skill in d["skills_sidebar"]:
        out.append(f"    \\item {skill}")
    out.append("    \\item Programming Languages:")
    out.append("    \\begin{itemize}")
    for group, items in d["programming_languages_sidebar"].items():
        joined = ", ".join(items)
        out.append(
            "        \\item \\makebox[2cm]{%s\\hfill} (\\textbf{%s})" % (group, joined)
        )
    out.append("    \\end{itemize}")
    out.append("\\end{itemize}")
    out.append("}")
    out.append("")
    # Activities
    out.append("% Command for printing extracurricular activities")
    out.append("\\newcommand\\activities {")
    out.append("    \\begin{itemize}[leftmargin=5mm]")
    for act in d["activities"]:
        if "bullets" in act:
            out.append(f"        \\item \\textbf{{{act['title']}}} ")
            out.append("        \\begin{itemize}")
            for b in act["bullets"]:
                out.append(f"            \\item {b}")
            out.append("        \\end{itemize}")
        else:
            out.append(f"        \\item \\textbf{{{act['title']}}} {act['text']}")
    out.append("    \\end{itemize}")
    out.append("}")
    out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# resume.ts
# ---------------------------------------------------------------------------

TS_HEADER = (
    "/**\n"
    " * Resume Data\n"
    " * \n"
    " * Centralized file containing all resume content:\n"
    " * - Professional experience\n"
    " * - Volunteer experience\n"
    " * - Teaching experience\n"
    " * - Education\n"
    " * - Skills\n"
    " * - Languages\n"
    " * - Certifications\n"
    " * \n"
    " * This separation allows easy updates to content without touching component logic.\n"
    " */\n"
    "\n"
    "import {\n"
    "  TimelineItem,\n"
    "  EducationItem,\n"
    "  SkillGroup,\n"
    "  Language,\n"
    "  Certification\n"
    "} from '@/types';"
)


def ts_str(s: str) -> str:
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def _timeline_entry(e: dict) -> str:
    lines = ["  {"]
    lines.append(f"    title: {ts_str(e['title'])},")
    lines.append(f"    company: {ts_str(e['company'])},")
    if e.get("company_url"):
        lines.append(f"    companyUrl: {ts_str(e['company_url'])},")
    lines.append(f"    startDate: {ts_str(e['start'])},")
    lines.append(f"    endDate: {ts_str(e['end'])},")
    if e.get("location"):
        lines.append(f"    location: {ts_str(e['location'])},")
    lines.append("    description: [")
    for b in e["bullets"]:
        lines.append(f"      {ts_str(b)},")
    lines[-1] = lines[-1].rstrip(",")  # no trailing comma after the last bullet
    lines.append("    ],")
    if e.get("type"):
        lines.append(f"    type: {ts_str(e['type'])},")
    if e.get("is_current"):
        lines.append("    isCurrent: true")
    # strip trailing comma of last property line when no isCurrent
    if not e.get("is_current"):
        lines[-1] = lines[-1].rstrip(",")
    lines.append("  },")
    return "\n".join(lines)


def _timeline_section(title: str, const: str, entries: list) -> str:
    out = [
        "/**",
        f" * {title}",
        " * Sorted in descending order (most recent first)",
        " */",
        f"export const {const}: TimelineItem[] = [",
    ]
    out += [_timeline_entry(e) for e in entries]
    # remove trailing comma of the last entry
    out[-1] = out[-1].rstrip(",")
    out.append("];")
    return "\n".join(out)


def gen_resume_ts(d: dict) -> str:
    parts = [TS_HEADER]
    parts.append(_timeline_section("Professional Experience", "professionalExperience",
                                  [e for e in d["experience"] if not (e.get("web") or {}).get("exclude")]))
    parts.append(_timeline_section("Volunteer Experience", "volunteerExperience", d["volunteer"]))
    parts.append(_timeline_section("Teaching Experience", "teachingExperience", d["teaching"]))

    # Education
    edu = ["/**", " * Education", " * Sorted in descending order (most recent first)", " */",
           "export const education: EducationItem[] = ["]
    entries = []
    for e in d["education"]:
        entries.append("\n".join([
            "  {",
            f"    degree: {ts_str(e['degree'])},",
            f"    school: {ts_str(e['school'])},",
            f"    schoolUrl: {ts_str(e['school_url'])},",
            f"    field: {ts_str(e['field'])},",
            f"    startDate: {ts_str(e['start'])},",
            f"    endDate: {ts_str(e['end'])}",
            "  },",
        ]))
    entries[-1] = entries[-1].rstrip(",")
    edu += entries
    edu.append("];")
    parts.append("\n".join(edu))

    # Skills
    sk = ["/**", " * Skills organized by category",
          " * Each skill includes an optional URL to its official website", " */",
          "export const skills: SkillGroup[] = ["]
    groups = []
    for g in d["skills"]:
        items = []
        for it in g["items"]:
            if it.get("url"):
                items.append(f"      {{ name: {ts_str(it['name'])}, url: {ts_str(it['url'])} }},")
            else:
                items.append(f"      {{ name: {ts_str(it['name'])} }},")
        items[-1] = items[-1].rstrip(",")
        groups.append("\n".join(
            ["  {", f"    category: {ts_str(g['category'])},", "    items: ["]
            + items + ["    ]", "  },"]
        ))
    groups[-1] = groups[-1].rstrip(",")
    sk += groups
    sk.append("];")
    parts.append("\n".join(sk))

    # Languages
    lg = ["/**", " * Languages", " */", "export const languages: Language[] = ["]
    lentries = []
    for lang in d["languages"]:
        lentries.append("\n".join([
            "  {",
            f"    name: {ts_str(lang['name'])},",
            f"    level: {ts_str(lang['level_ts'])}",
            "  },",
        ]))
    lentries[-1] = lentries[-1].rstrip(",")
    lg += lentries
    lg.append("];")
    parts.append("\n".join(lg))

    # Certifications
    ce = ["/**", " * Certifications and Achievements", " */",
          "export const certifications: Certification[] = ["]
    centries = []
    for c in d["certifications"]:
        centries.append("\n".join([
            "  {",
            f"    name: {ts_str(c['name'])},",
            f"    issuer: {ts_str(c['issuer'])},",
            f"    issuerUrl: {ts_str(c['issuer_url'])},",
            f"    date: {ts_str(c['date'])}",
            "  },",
        ]))
    centries[-1] = centries[-1].rstrip(",")
    ce += centries
    ce.append("];")
    parts.append("\n".join(ce))

    return "\n\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# projects.ts (website project portfolio)
# ---------------------------------------------------------------------------

def _project_entry(p: dict) -> str:
    lines = [
        "  {",
        f"    name: {ts_str(p['name'])},",
        f"    description: {ts_str(p['description'])},",
        f"    technologies: [{', '.join(ts_str(t) for t in p['technologies'])}],",
    ]
    if p.get("project_url"):
        lines.append(f"    projectUrl: {ts_str(p['project_url'])},")
    lines.append("  },")
    return "\n".join(lines)


def gen_projects_ts(projects: list) -> str:
    n = len(projects)
    out = [
        "/**",
        " * Personal Projects Data",
        " * ",
        f" * Contains all {n} personal projects from LinkedIn profile with descriptions, technologies, and links",
        " * All projects are from LinkedIn profile with real descriptions and links where available",
        " */",
        "",
        "export interface Project {",
        "  /** Project name/title */",
        "  name: string;",
        "  /** Project description */",
        "  description: string;",
        "  /** Array of technologies used */",
        "  technologies: string[];",
        "  /** Optional project URL (GitHub, demo, or app store) */",
        "  projectUrl?: string;",
        "}",
        "",
        "/**",
        " * Personal Projects",
        f" * All {n} projects from LinkedIn profile, sorted by date (newest first)",
        " */",
        "export const projects: Project[] = [",
    ]
    out += [_project_entry(p) for p in projects]
    out.append("];")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# index.html meta descriptions
# ---------------------------------------------------------------------------

def sync_index_html(html_path: Path, meta: dict) -> str:
    """Replace the 5 resume-derived meta descriptions; assert exactly 1 hit each."""
    text = html_path.read_text()
    # (pattern, new content). Group 1/2 are the structural wrapper, kept as-is.
    subs = [
        (r'(<meta name="description" content=")[^"]*(")', meta["description"]),
        (r'(<meta property="og:description" content=")[^"]*(")', meta["og_description"]),
        (r'(<meta name="twitter:description" content=")[^"]*(")', meta["twitter_description"]),
        (r'("description": ")Senior Software Engineer at Meta with expertise[^"]*(")',
         meta["jsonld_person_description"]),
        (r'("description": ")Interactive resume and portfolio[^"]*(")',
         meta["jsonld_website_description"]),
    ]
    for pattern, new_value in subs:
        new_text, n = re.subn(
            pattern, lambda m: m.group(1) + new_value + m.group(2), text, count=1
        )
        if n != 1:
            raise SystemExit(f"ERROR: pattern {pattern!r} matched {n} times in {html_path}")
        text = new_text
    return text


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--website-repo", default="../personal-resume-website",
                    help="Path to the personal-resume-website checkout")
    ap.add_argument("--check", action="store_true",
                    help="Verify generated files match disk; write nothing")
    args = ap.parse_args()

    website_repo = (REPO_ROOT / args.website_repo).resolve()
    data = yaml.safe_load((REPO_ROOT / "resume.yaml").read_text())

    outputs = {
        REPO_ROOT / "sections" / "personal-info.tex": gen_personal_info(data["personal"]),
        REPO_ROOT / "sections" / "education.tex": gen_education(data["education"]),
        REPO_ROOT / "sections" / "publications.tex": gen_publications(data["publications"]),
        REPO_ROOT / "sections" / "experience.tex": gen_experience(data["experience"]),
        REPO_ROOT / "sections" / "sidebar-content.tex": gen_sidebar(data),
        website_repo / "client" / "src" / "data" / "resume.ts": gen_resume_ts(data),
        website_repo / "client" / "src" / "data" / "projects.ts": gen_projects_ts(data["projects"]),
        website_repo / "client" / "index.html":
            sync_index_html(website_repo / "client" / "index.html", data["site_meta"]),
    }

    if args.check:
        bad = [str(p) for p, content in outputs.items()
               if not p.exists() or p.read_text() != content]
        if bad:
            print("OUT OF DATE:")
            print("\n".join(f"  {p}" for p in bad))
            return 1
        print(f"OK: all {len(outputs)} generated files are up to date.")
        return 0

    for path, content in outputs.items():
        path.write_text(content)
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
