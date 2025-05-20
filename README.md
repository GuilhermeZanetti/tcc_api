# Judge API

## Setup

The first step is install poetry and then install the project dependencies

```shell
$ pip install poetry
$ make setup
```

After installing poetry and the dependencies, you need to start docker.

```shell
$ docker-compose up -d
```

After this, run the project.

```shell
$ make run
```

Caso queira debugar no vscode:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: FastAPI",
            "type": "debugpy",
            "request": "launch",
            "module": "hypercorn",
            "args": [
                "judge.main:app",
                "--reload"
            ],
            "jinja": true,
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```