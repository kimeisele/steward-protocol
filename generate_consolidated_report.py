import json
import os
from collections import defaultdict


def summarize_docstring(docstring, max_sentences=2):
    """
    Summarizes a docstring by taking the first few sentences.
    """
    if not docstring:
        return "Keine Beschreibung vorhanden."
    sentences = docstring.strip().split(".")
    if len(sentences) > max_sentences:
        return ".".join(sentences[:max_sentences]).strip() + "..."
    return docstring.strip()


def generate_consolidated_report(docstrings_data):
    """
    Generates a consolidated markdown report from the extracted docstrings data.
    """
    report_content = []

    total_files = len(docstrings_data)
    total_docstrings = 0
    module_docstrings_count = 0
    class_docstrings_count = 0
    function_docstrings_count = 0
    files_with_sparse_docstrings = []  # Files with less than 2 docstrings total

    module_summaries = {}  # file_path: summary
    class_summaries = defaultdict(list)  # theme: list of {name, summary, file_path}
    function_summaries = defaultdict(list)  # theme: list of {name, summary, file_path}

    for file_data in docstrings_data:
        relative_path = os.path.relpath(file_data["file_path"])

        file_ds_count = len(file_data["docstrings"])
        if file_ds_count < 2:  # Heuristic for sparse documentation
            files_with_sparse_docstrings.append(relative_path)

        total_docstrings += file_ds_count

        for ds in file_data["docstrings"]:
            summary = summarize_docstring(ds["docstring"])

            if ds["type"] == "module":
                module_docstrings_count += 1
                module_summaries[relative_path] = summary
            elif ds["type"] == "ClassDef":
                class_docstrings_count += 1
                # Simple grouping for now: use file's parent directory as a "theme"
                theme = os.path.dirname(relative_path).replace("/", "::") or "Root"
                class_summaries[theme].append({"name": ds["name"], "summary": summary, "file_path": relative_path})
            elif ds["type"] in ("FunctionDef", "AsyncFunctionDef"):
                function_docstrings_count += 1
                # Simple grouping for now: use file's parent directory as a "theme"
                theme = os.path.dirname(relative_path).replace("/", "::") or "Root"
                function_summaries[theme].append({"name": ds["name"], "summary": summary, "file_path": relative_path})

    report_content.append("# Docstring Analyse: Konsolidierter Bericht\n")
    report_content.append(
        "Dieser Bericht bietet eine konsolidierte Analyse der Docstrings aller Python-Skripte im Projekt, um die übergeordnete Architektur und Funktionalität zu verstehen.\n"
    )

    report_content.append("## 1. Projekt-Übersicht und Dokumentationsstatus\n")
    report_content.append(f"* **Gesamtzahl der analysierten Python-Dateien:** {total_files}\n")
    report_content.append(f"* **Gesamtzahl der Docstrings gefunden:** {total_docstrings}\n")

    # Calculate a simple "documented percentage"
    # This is a rough estimate and can be refined
    documented_elements = class_docstrings_count + function_docstrings_count
    total_possible_elements = 0
    for file_data in docstrings_data:
        # Assuming every file has potential for at least one module, one class, one function docstring
        total_possible_elements += (
            file_data["docstrings"].count({"type": "ClassDef"})
            + file_data["docstrings"].count({"type": "FunctionDef"})
            + file_data["docstrings"].count({"type": "AsyncFunctionDef"})
            + 1
        )

    # Simplified documentation metric: ratio of found docstrings to total files (not perfect, but an indicator)
    documentation_ratio = (total_docstrings / total_files) if total_files > 0 else 0
    report_content.append(
        f"* **Dokumentationsdichte (Durchschnittliche Docstrings pro Datei):** {documentation_ratio:.2f}\n"
    )

    if files_with_sparse_docstrings:
        report_content.append("* **Dateien mit unzureichender Dokumentation (weniger als 2 Docstrings):**\n")
        for f in files_with_sparse_docstrings:
            report_content.append(f"    * `{f}`\n")
    else:
        report_content.append("* **Alle Dateien scheinen eine grundlegende Dokumentation zu haben.**\n")

    report_content.append("\n## 2. Hauptmodule und deren Zwecke (Moduldokstrings)\n")
    if module_summaries:
        for path, summary in module_summaries.items():
            report_content.append(f"* `{path}`: {summary}\n")
    else:
        report_content.append("* Keine Moduldokstrings gefunden.\n")

    report_content.append("\n## 3. Identifizierte Kernkomponenten / Architektonische Muster (Klassen-Docstrings)\n")
    if class_summaries:
        for theme, classes in class_summaries.items():
            report_content.append(f"### {theme.replace('::', ' -> ')}\n")
            for cls in classes:
                report_content.append(f"* `{cls['name']}` (in `{cls['file_path']}`): {cls['summary']}\n")
    else:
        report_content.append("* Keine Klassendokstrings gefunden.\n")

    report_content.append("\n## 4. Wichtige Funktionalitäten (Funktions-Docstrings)\n")
    if function_summaries:
        for theme, functions in function_summaries.items():
            report_content.append(f"### {theme.replace('::', ' -> ')}\n")
            for func in functions:
                report_content.append(f"* `{func['name']}` (in `{func['file_path']}`): {func['summary']}\n")
    else:
        report_content.append("* Keine Funktionsdokstrings gefunden.\n")

    report_content.append("\n---\n\n### Methodik:\n")
    report_content.append(
        "Dieser Bericht wurde durch die Extraktion und semantische Analyse von Docstrings aus den Python-Skripten des Projekts generiert. Die Zusammenfassungen basieren auf den im Code vorhandenen Beschreibungen und einer heuristischen Gruppierung nach Dateipfaden. Es wurden keine externen LLMs für die semantische Analyse verwendet.\n"
    )

    return "".join(report_content)


if __name__ == "__main__":
    json_path = "docs/architecture/docstring_analysis/docstrings.json"
    report_path = "docs/architecture/docstring_analysis/report.md"

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            docstrings_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_path} not found. Please ensure docstrings are extracted first.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_path}. The file might be corrupted.")
        exit(1)

    markdown_report = generate_consolidated_report(docstrings_data)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(markdown_report)

    print(f"Consolidated docstring analysis report generated at: {report_path}")
