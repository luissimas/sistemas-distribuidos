# Trabalho 1

A video chat application.

## Installing

The only recommended and supported method of installation is with [pipx](https://github.com/pypa/pipx).

```sh
pipx install "git+https://github.com/luissimas/sistemas-distribuidos.git@#egg=trabalho-1&subdirectory=trabalho-1"
```

The `sd-trabalho-1` executable will be installed in your system's path. More information about usage is included in the executable itself:

```sh
sd-trabalho-1 --help
```

With that said, you could install with pip at the risk of completely breaking your system's Python environment.

## Developing

This project uses [Poetry](https://python-poetry.org/) to manage its dependencies and development environment. For instructions on how to install Poetry, refer to their [documentation](https://python-poetry.org/docs/#installation).

Install the project and its dependencies:

```sh
poetry install
```

Enter a shell with the project's virtual environment:

```sh
poetry shell
```

Run the server:

```sh
sd-trabalho-1 server
```

Run the client:

```sh
sd-trabalho-1 client
```

For more details on how to run the applications and what options are supported, refer to the CLI's help:

```sh
sd-trabalho-1 --help
```
