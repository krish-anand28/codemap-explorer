import os
import re
from pathlib import Path


class RepoAnalyzer:
    """Analyzes a code repository and builds a dependency graph."""

    SKIP_DIRS = {
        "node_modules", ".git", "__pycache__", "dist", "build",
        ".env", ".venv", "venv",
    }

    BINARY_EXTENSIONS = {
        ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".bmp",
        ".exe", ".dll", ".so", ".dylib",
        ".pdf", ".zip", ".tar", ".gz",
        ".lock",
        ".woff", ".woff2", ".ttf", ".eot",
        ".mp3", ".mp4", ".wav", ".avi", ".mov",
        ".pyc", ".class", ".o",
    }

    EXTENSION_LANGUAGE_MAP = {
        ".py": "Python",
        ".js": "JavaScript",
        ".jsx": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
        ".java": "Java",
        ".go": "Go",
        ".rb": "Ruby",
        ".rs": "Rust",
        ".c": "C",
        ".h": "C",
        ".cpp": "C++",
        ".hpp": "C++",
        ".cc": "C++",
        ".cxx": "C++",
        ".cs": "C#",
        ".php": "PHP",
        ".swift": "Swift",
        ".kt": "Kotlin",
        ".kts": "Kotlin",
        ".scala": "Scala",
        ".md": "Markdown",
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".html": "HTML",
        ".htm": "HTML",
        ".css": "CSS",
        ".scss": "SCSS",
        ".sass": "SCSS",
        ".less": "LESS",
        ".sql": "SQL",
        ".sh": "Shell",
        ".bash": "Shell",
        ".zsh": "Shell",
        ".fish": "Shell",
        ".r": "R",
        ".R": "R",
        ".lua": "Lua",
        ".pl": "Perl",
        ".pm": "Perl",
        ".ex": "Elixir",
        ".exs": "Elixir",
        ".erl": "Erlang",
        ".hs": "Haskell",
        ".ml": "OCaml",
        ".clj": "Clojure",
        ".dart": "Dart",
        ".vue": "Vue",
        ".svelte": "Svelte",
        ".tf": "Terraform",
        ".toml": "TOML",
        ".ini": "INI",
        ".cfg": "INI",
        ".xml": "XML",
        ".graphql": "GraphQL",
        ".gql": "GraphQL",
        ".proto": "Protobuf",
        ".txt": "Text",
        ".env": "Dotenv",
        ".csv": "CSV",
    }

    # Comment prefixes by language for LOC counting
    SINGLE_LINE_COMMENT = {
        "Python": "#",
        "Ruby": "#",
        "Shell": "#",
        "YAML": "#",
        "TOML": "#",
        "Dotenv": "#",
        "R": "#",
        "Perl": "#",
        "Elixir": "#",
        "JavaScript": "//",
        "TypeScript": "//",
        "Java": "//",
        "Go": "//",
        "Rust": "//",
        "C": "//",
        "C++": "//",
        "C#": "//",
        "PHP": "//",
        "Swift": "//",
        "Kotlin": "//",
        "Scala": "//",
        "Dart": "//",
        "Protobuf": "//",
        "GraphQL": "#",
        "SQL": "--",
        "Lua": "--",
        "Haskell": "--",
        "SCSS": "//",
        "LESS": "//",
    }

    MAX_RAW_CONTENT_LENGTH = 8000

    def _detect_language(self, filepath: str) -> str:
        """Detect programming language from file extension or filename."""
        basename = os.path.basename(filepath).lower()

        # Handle special filenames without extensions
        special_names = {
            "dockerfile": "Docker",
            "makefile": "Makefile",
            "gnumakefile": "Makefile",
            "rakefile": "Ruby",
            "gemfile": "Ruby",
            "cmakelists.txt": "CMake",
            ".gitignore": "Git",
            ".dockerignore": "Docker",
            ".editorconfig": "EditorConfig",
            "vagrantfile": "Ruby",
            "procfile": "Procfile",
        }
        if basename in special_names:
            return special_names[basename]

        ext = os.path.splitext(filepath)[1].lower()
        return self.EXTENSION_LANGUAGE_MAP.get(ext, "Unknown")

    def _count_loc(self, content: str, language: str) -> int:
        """Count non-empty, non-comment lines of code."""
        comment_prefix = self.SINGLE_LINE_COMMENT.get(language)
        count = 0
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if comment_prefix and stripped.startswith(comment_prefix):
                continue
            count += 1
        return count

    def _size_category(self, loc: int) -> str:
        """Classify file size by lines of code."""
        if loc < 50:
            return "small"
        elif loc <= 200:
            return "medium"
        else:
            return "large"

    def traverse(self, repo_path: str) -> dict:
        """
        Walk every file in the directory recursively and collect metadata.

        Returns a dict mapping file_id → file info dict.
        """
        repo_root = Path(repo_path).resolve()
        files: dict = {}

        for dirpath, dirnames, filenames in os.walk(repo_root):
            # Filter out skipped directories in-place so os.walk won't descend
            dirnames[:] = [
                d for d in dirnames if d not in self.SKIP_DIRS
            ]

            for filename in filenames:
                full_path = Path(dirpath) / filename
                ext = full_path.suffix.lower()

                # Skip binary files
                if ext in self.BINARY_EXTENSIONS:
                    continue

                # Build relative path as the file ID
                try:
                    rel_path = full_path.relative_to(repo_root)
                except ValueError:
                    continue

                file_id = str(rel_path).replace("\\", "/")

                # Try reading as UTF-8
                try:
                    raw_content = full_path.read_text(encoding="utf-8")
                except (UnicodeDecodeError, PermissionError, OSError):
                    continue

                language = self._detect_language(file_id)
                loc = self._count_loc(raw_content, language)
                size_cat = self._size_category(loc)

                files[file_id] = {
                    "id": file_id,
                    "label": filename,
                    "lines_of_code": loc,
                    "size_category": size_cat,
                    "language": language,
                    "raw_content": raw_content[: self.MAX_RAW_CONTENT_LENGTH],
                }

        return files

    def extract_dependencies(
        self,
        file_id: str,
        content: str,
        language: str,
        all_file_ids: list[str],
    ) -> list[str]:
        """
        Parse import/require statements and resolve them to known internal file IDs.
        Returns a list of file IDs that this file depends on.
        """
        raw_imports: list[str] = []
        file_dir = os.path.dirname(file_id)

        if language == "Python":
            # from X import Y  /  from X import (Y, Z)
            for m in re.finditer(
                r"^\s*from\s+([\w.]+)\s+import\s+", content, re.MULTILINE
            ):
                raw_imports.append(m.group(1))
            # import X  /  import X, Y
            for m in re.finditer(
                r"^\s*import\s+([\w.]+(?:\s*,\s*[\w.]+)*)", content, re.MULTILINE
            ):
                parts = m.group(1).split(",")
                for part in parts:
                    mod = part.strip().split(" ")[0]  # handle `import X as Y`
                    if mod:
                        raw_imports.append(mod)

        elif language in ("JavaScript", "TypeScript"):
            # import ... from 'X' / import ... from "X"
            for m in re.finditer(
                r"""^\s*import\s+.*?\s+from\s+['"]([^'"]+)['"]""",
                content,
                re.MULTILINE,
            ):
                raw_imports.append(m.group(1))
            # import 'X' / import "X" (side-effect imports)
            for m in re.finditer(
                r"""^\s*import\s+['"]([^'"]+)['"]""",
                content,
                re.MULTILINE,
            ):
                raw_imports.append(m.group(1))
            # require('X') / require("X")
            for m in re.finditer(
                r"""require\(\s*['"]([^'"]+)['"]\s*\)""",
                content,
            ):
                raw_imports.append(m.group(1))

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique_imports: list[str] = []
        for imp in raw_imports:
            if imp not in seen:
                seen.add(imp)
                unique_imports.append(imp)

        all_ids_set = set(all_file_ids)
        resolved: list[str] = []

        common_extensions = [".py", ".js", ".jsx", ".ts", ".tsx"]
        index_suffixes = [
            "/index.js", "/index.ts", "/index.jsx", "/index.tsx",
        ]

        for imp in unique_imports:
            candidates: list[str] = []

            if language == "Python":
                # Convert dotted module path to slash-separated path
                as_path = imp.replace(".", "/")
                candidates.append(as_path)
                # Try with .py
                candidates.append(as_path + ".py")
                # Try as package __init__.py
                candidates.append(as_path + "/__init__.py")

            elif language in ("JavaScript", "TypeScript"):
                if imp.startswith("."):
                    # Relative import — resolve against file's directory
                    resolved_path = os.path.normpath(
                        os.path.join(file_dir, imp)
                    ).replace("\\", "/")
                    candidates.append(resolved_path)
                    for ext in common_extensions:
                        candidates.append(resolved_path + ext)
                    for suffix in index_suffixes:
                        candidates.append(resolved_path + suffix)
                else:
                    # Absolute/alias import — try as-is
                    candidates.append(imp)
                    for ext in common_extensions:
                        candidates.append(imp + ext)
                    for suffix in index_suffixes:
                        candidates.append(imp + suffix)

            # Match candidates against known file IDs
            for candidate in candidates:
                # Normalize path separators and remove leading ./
                normalized = candidate.replace("\\", "/")
                if normalized.startswith("./"):
                    normalized = normalized[2:]
                if normalized in all_ids_set and normalized != file_id:
                    if normalized not in resolved:
                        resolved.append(normalized)
                    break

        return resolved

    def build_graph(self, repo_path: str) -> dict:
        """
        Build the full dependency graph for a repository.

        Returns {nodes: [...], edges: [...]}.
        """
        file_map = self.traverse(repo_path)
        all_file_ids = list(file_map.keys())

        nodes: list[dict] = []
        edges: list[dict] = []
        edge_set: set[str] = set()

        # Grid layout parameters
        columns = 5
        x_spacing = 300
        y_spacing = 200

        for idx, (file_id, info) in enumerate(file_map.items()):
            col = idx % columns
            row = idx // columns

            node = {
                "id": info["id"],
                "label": info["label"],
                "lines_of_code": info["lines_of_code"],
                "size_category": info["size_category"],
                "language": info["language"],
                "data": {
                    "raw_content": info["raw_content"],
                    "lines_of_code": info["lines_of_code"],
                    "size_category": info["size_category"],
                    "language": info["language"],
                },
                "position": {
                    "x": col * x_spacing,
                    "y": row * y_spacing,
                },
            }
            nodes.append(node)

            # Extract dependencies
            deps = self.extract_dependencies(
                file_id,
                info["raw_content"],
                info["language"],
                all_file_ids,
            )
            for dep in deps:
                edge_id = f"edge-{file_id}-{dep}"
                if edge_id not in edge_set:
                    edge_set.add(edge_id)
                    edges.append({
                        "id": edge_id,
                        "source": file_id,
                        "target": dep,
                    })

        return {"nodes": nodes, "edges": edges}
