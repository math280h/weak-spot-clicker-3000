import nox
from nox.sessions import Session

locations = "main.py", "noxfile.py"
python_versions = ["3.10"]


@nox.session(python=python_versions)
def black(session: Session) -> None:
    """Format code using black."""
    args = session.posargs or locations
    session.install("black")
    session.run("black", *args)


@nox.session(python=python_versions)
def lint(session: Session) -> None:
    """Lint code using flake8."""
    args = session.posargs or locations
    session.install(
        "flake8",
        "flake8-annotations",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-docstrings",
        "flake8-import-order",
    )
    session.run("flake8", *args)
