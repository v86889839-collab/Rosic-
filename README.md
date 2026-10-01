# Rosic — a Russian-syntax scripting language for Windows

Rosic is a custom scripting language with Russian keywords, designed for Windows automation, Discord bots, file format tooling, and system utilities.

## Features

- **Russian syntax**: `пусть`, `если`, `для`, `структура`, `функция` — no English required.
- **Multiple file types**:
  - `.рос` — main scripts (entry point)
  - `.rus` — modules/libraries
  - `.функц` — single-function files
  - `.test` — test files with `// ТЕСТ:` markers
  - `.сфайл` — stop-flag files for daemons/scanners
- **Built-in REPL**: run `python rosic.py` for interactive mode.
- **Import system**: `импорт "path"` loads modules without executing them immediately.
- **Test runner**: automatically detects and runs `// ТЕСТ:` blocks in `.test` files.

## Quick Start

1. Clone or download the repo.
2. Ensure Python 3.8+ is installed and in PATH.
3. Run the REPL:
   ```bash
   python rosic.py
Or run a script:
bash
python rosic.py main.рос
Run tests:
bash
python rosic.py tests/verify_basic.test
Example
main.рос:

rosic
импорт "modules/hello.rus"

пусть version = 1.0
печатать("Rosic v" + к_тексту(version))

поздороваться("Developer")

для i от 1 до 3 {
    печатать("Iteration " + к_тексту(i))
}
modules/hello.rus:

rosic
функция поздороваться(name: текст) {
    печатать("Привет, " + name + "! Это модуль .рус")
}
Run:

bash
python rosic.py main.рос
Output:

text
Rosic v1.0
Привет, Developer! Это модуль .рус
Iteration 1
Iteration 2
Iteration 3
Project Structure
text
rosic-project/
├── rosic.py                # interpreter core
├── main.рос                # entry point
├── .gitignore              # ignore build artifacts, venv, __pycache__
├── README.md               # this file
├── README_RU.md            # Russian docs
├── LICENSE                 # license (MIT recommended)
├── modules/                # user modules (.rus, .функц)
│   ├── hello.rus
│   └── ...
└── tests/                  # test files (.test)
    ├── verify_basic.test
    └── ...
Contributing
PRs are welcome! When adding features:

Write at least one // ТЕСТ: in a .test file.
Keep syntax consistent with existing keywords.
Update README_RU.md if you add major features.
License
MIT — see LICENSE.

Made for Windows automation, Discord bot logic, and custom file format tooling. Built by [v86889839-collab(PBSTHelper)].
