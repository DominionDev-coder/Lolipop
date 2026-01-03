![Lolipop splash image](assets/images/lolipop.png)
[![Version](https://img.shields.io/badge/version-v1.20.7-blue)](version)
![Package Download]()
![Github stars]()
[![Status](https://img.shields.io/badge/status-active-brightgreen)]()
![Discord]()

<h1 align="center" style=color:deeppink><b> Lolipop </b></h1>
<p align="center">
A developer utility for installing, setting up, and managing projects and environments effortlessly.
</p>
<br>
  
<h2 align="center" style=color:blue> Commands and features </h2>

- `lolipop install "github url/url"`:
installs a project, set it up, and does the required process.

- `lolipop run`:
runs a project with all required process if specified in it lolipop.yaml
e.g. `lolipop run <project_name>` will execute the commands defined in the lolipop.yaml or pyproject.toml file of the project
or `lolipop run` to run the current project.

- `lolipop init`:
create a project, in your own way: from a yaml file.

- `lolipop dev`:
lolipop tools for development.

- `lolipop feature`:
feature manager for your project.

- `lolipop add`:
add things to your environment.

- `lolipop remove`:
remove things from your environment.

- `lolipop env`:
lolipop environment manager tool.

- `lolipop build`:
tool for building project codes and files.

- `lolipop list`:
list projects or environments.

- `lolipop command`:
run a command in/from lolipop environment,
e.g. running a command that is in a lolipop environment:
`lolipop command "command name"` for activated environment,
or `lolipop command -e "env name" "command name"` for a specific environment.

- `lolipop template`:
template manager tool. create templates from your projects,
install templates, use a template for a project. license applies

- `lolipop console`:
TUI workspace for lolipop projects and environments.

- `lolipop fix`:
tool for analysing and fixing errors, using your favourite.

- `lolipop update`:
update lolipop or installed projects.

- `lolipop preview`:
run a project in debug and test mode.

- `lolipop mode`:
switch your mode of development.

<br>

---
<h2 align="center" style="color:green"> Installation </h2>

To install Lolipop, use pip:
```bash
pip install lolipop
```
Homebrew:
```bash
brew install lolipop
```
UV:
```bash
uv add lolipop # or
uv pip install lolipop
```
