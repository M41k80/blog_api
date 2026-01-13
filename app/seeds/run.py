import typer
from .service import run_users
from .service import run_categories
from .service import run_tags
from .service import run_all

app = typer.Typer(help="Seeds: users, categories, tags")


@app.command("all")
def all_():
    run_all()
    typer.echo("All data seeded")
    
@app.command("users")
def users():
    run_users()
    typer.echo("Users seeded")
    
@app.command("categories")
def categories():
    run_categories()
    typer.echo("Categories seeded")
    
@app.command("tags")
def tags():
    run_tags()
    typer.echo("Tags seeded")