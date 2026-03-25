## Description
We are writting AI assistent.
Assistent consists of backend which runs LLM requests and stores dialog history and CLI client for it.

## Libraries and frameworks
We use `python 3` programming language.
We usw `uv` as python package manager.
We use `flask` to implement server code.
We use `langchain` to interact with AI models.
By default we use `gigachat` model.
We use `PostgreSQL` as database.
We use `SQLAlchemy` to work with database.
We use `Alembic` for database migrations.
We use `docker-compose` to run server.

## Architecture
Server code located at `backend` folder.
CLI code located at `cli` folder.
Database migrations located at `database` folder.