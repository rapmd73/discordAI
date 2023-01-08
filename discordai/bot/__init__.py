"""
Copyright © Krypton 2019-2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 5.4.1
"""

import asyncio
import os
import pkgutil
import platform
import shutil
import sys
import tempfile
import appdirs

import discord
from discord.ext import commands
from discord.ext.commands import Bot, Context

intents = discord.Intents.default()
intents.message_content = True
bot = Bot(command_prefix=commands.when_mentioned_or(
    '/'), intents=intents, help_command=None)


def start_bot(config):
    bot.config = config

    @bot.event
    async def on_ready() -> None:
        """
        The code in this even is executed when the bot is ready
        """
        print(f"Logged in as {bot.user.name}")
        print(f"discord.py API version: {discord.__version__}")
        print(f"Python version: {platform.python_version()}")
        print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
        print("-------------------")

    @bot.event
    async def on_message(message: discord.Message) -> None:
        """
        The code in this event is executed every time someone sends a message, with or without the prefix

        :param message: The message that was sent.
        """
        if message.author == bot.user or message.author.bot:
            return
        await bot.process_commands(message)

    @bot.event
    async def on_command_completion(context: Context) -> None:
        """
        The code in this event is executed every time a normal command has been *successfully* executed
        :param context: The context of the command that has been executed.
        """
        full_command_name = context.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        if context.guild is not None:
            print(
                f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})")
        else:
            print(
                f"Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs")

    @bot.event
    async def on_command_error(context: Context, error) -> None:
        """
        The code in this event is executed every time a normal valid command catches an error
        :param context: The context of the normal command that failed executing.
        :param error: The error that has been faced.
        """
        if isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            hours = hours % 24
            embed = discord.Embed(
                title="Hey, please slow down!",
                description=f"You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
                color=0xE02B2B
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Error!",
                description="You are missing the permission(s) `" + ", ".join(
                    error.missing_permissions) + "` to execute this command!",
                color=0xE02B2B
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                title="Error!",
                description="I am missing the permission(s) `" + ", ".join(
                    error.missing_permissions) + "` to fully perform this command!",
                color=0xE02B2B
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Error!",
                # We need to capitalize because the command arguments have no capital letter in the code.
                description=str(error).capitalize(),
                color=0xE02B2B
            )
            await context.send(embed=embed)
        raise error

    async def load_cogs() -> None:
        """
        The code in this function is executed whenever the bot will start.
        """
        if getattr(sys, 'frozen', False):
            # The code is being run as a frozen executable
            # data_dir = appdirs.user_data_dir(appauthor="Adib Baji", appname="discordai")
            # cogs_path = os.path.join(data_dir, "discordai/bot/cogs")
            # if not os.path.exists(cogs_path):
            #     data_dir = sys._MEIPASS
            #     og_cogs_path = os.path.join(data_dir, "discordai/bot/cogs")
            #     shutil.copytree(og_cogs_path, os.path.join(data_dir, cogs_path))

            # Get the user's data directory
            data_dir = appdirs.user_data_dir(appauthor="Adib Baji", appname="discordai")

            # Create a subdirectory to store the cogs
            cogs_path = os.path.join(data_dir, "discordai/bot/cogs")
            if not os.path.exists(cogs_path):
                os.makedirs(cogs_path)

            # Access the cogs as data files within your package
            data = pkgutil.get_data("discordai.bot", "cogs")

            # Write the cogs to a temporary directory
            temp_dir = tempfile.TemporaryDirectory()
            temp_cogs_path = os.path.join(temp_dir, "cogs")
            with open(temp_cogs_path, "wb") as f:
                f.write(data)

            # Copy the cogs to the user's system
            shutil.copytree(temp_cogs_path, cogs_path)
        else:
            # The code is being run normally
            bot_dir = os.path.dirname(__file__)
            cogs_path = os.path.join(bot_dir, "cogs")
        for file in os.listdir(cogs_path):
            if file.endswith(".py"):
                extension = file[:-3]
                if extension != "__init__":
                    try:
                        await bot.load_extension(f".cogs.{extension}", package="discordai.bot")
                        print(f"Loaded extension '{extension}'")
                    except Exception as e:
                        exception = f"{type(e).__name__}: {e}"
                        print(f"Failed to load extension {extension}\n{exception}")
        # Clean up the temporary directory
        if temp_dir:
            temp_dir.cleanup()

    asyncio.run(load_cogs())
    bot.run(config["token"])
