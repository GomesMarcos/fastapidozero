# fastapidozero

## 👋 Apresentação

Bem-vindo ao projeto **fastapidozero**!  
Este projeto foi desenvolvido como parte de uma aula prática de FastAPI, com o objetivo de demonstrar como criar uma API do zero utilizando as melhores práticas do ecossistema Python.

- 🔗 **Acesse o repositório no GitHub:** [Repo](https://github.com/GomesMarcos/fastapidozero)

- 🔗 **Fonte das aulas:** [Slides do DunoSSauro](https://fastapidozero.dunossauro.com/estavel/)
## Local Run
```
cd fast_zero
poetry env use 3.13
poetry shell
uvicorn fast_zero.app:app --reload
# or
poetry run uvicorn fast_zero.app:app --reload
```

## Docs
http://localhost:8000/redoc
or
http://localhost:8000/docs#/

## Linting and Formatting
```
ruff format .
ruff check .
```

## Running Tests
```
pytest --cov=fast_zero -vv
coverage html
```

## TaskPY
```
task run   # para rodar o servidor
task test  # para executar os testes
```

