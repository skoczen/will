import click

from will.main import WillBot


@click.command()
@click.option('-c', '--config', type=click.Path())
def clirunner(config):
    bot = WillBot(config_file=config)
    bot.bootstrap()
