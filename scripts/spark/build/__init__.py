"""
The build area (W6-U3, P705): a requirements file in, a board that builds out, and the project set up before it. The
build as one run of its stages (`build_service`), check_spine's whole run of the chain around it (`requirements_build`),
each stage's outcome (`stages`), the adapters of the board engine and the diagram converter (`board_engine`), the files
`--keep` writes (`kept_files`), the project's files (`project_setup`), the files AI tools read (`ai_files`) and the
build's codes (`build_codes`). The CLIs `check_spine.py` and `init_project.py` stay in `scripts/` and call these
modules. This file imports nothing, because an `__init__` that imports its modules made the cycles of wave 5.
"""
