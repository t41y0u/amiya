import logging
import re
from urllib.request import pathname2url

from discord import Embed
from discord.ext import commands

from amiya.utils import arknights, discord_common, paginator


class OperatorCogError(commands.CommandError):
    pass


class Operator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def operator(self, ctx):
        """
        Operator commands
        """

        await ctx.send_help(ctx.command)

    @operator.command(brief="Shows info of an operator", usage="[operator]")
    async def info(self, ctx, *, operator=None):
        """
        Detailed informations of an operator

        E.g: ;operator info Amiya
        """

        if operator is None:
            raise OperatorCogError("You need to provide an operator name!")

        # Get operator info
        info = arknights.get_operator_info(operator)

        await ctx.send(embed=discord_common.embed_info("Command under construction"))

    @operator.command(brief="Shows operator's file", usage="[operator]")
    async def file(self, ctx, *, operator=None):
        """
        Detailed file of specified operator

        E.g: ;operator file Angelina
        """

        if operator is None:
            raise OperatorCogError("You need to provide an operator name!")

        # Get file
        info = arknights.get_operator_file(operator)

        embeds = []
        for idx, story in enumerate(info[1]["storyTextAudio"]):
            # Initialize embed and get each file piece
            endl = "\n"
            embed = Embed(
                title=info[0], description=f'''Painter : {info[1]["drawName"]}\nCV : {info[1]["infoName"]}\n\n**{story["storyTitle"]}**\n{endl.join(list(map(lambda x: x["storyText"], story["stories"])))}''')

            # Add image to make the embed less boring with text only
            # https://github.com/Aceship/AN-EN-Tags/tree/master/img
            embed.set_thumbnail(
                url=f'https://raw.githubusercontent.com/Aceship/AN-EN-Tags/master/img/portraits/{pathname2url(info[1]["charID"])}_1.png')

            embeds.append(embed)

        # Start paginator
        pgnt = paginator.BotEmbedPaginator(ctx, embeds)
        await pgnt.run()

    @operator.command(brief="Shows operator's audio records", usage="[operator]")
    async def audio(self, ctx, *, operator=None):
        """
        Audio records of specified operator

        E.g: ;operator audio Angelina
        """

        if operator is None:
            raise OperatorCogError("You need to provide an operator name!")

        # Get audio records
        info = arknights.get_operator_audio(operator)

        # Get profile to make the embed less boring
        profile = arknights.get_operator_file(operator)

        embeds, lgt = [], len(info[1])
        for i in range(3):
            # Initalize embed
            embed = Embed(
                title=info[0], description=f'Painter : {profile[1]["drawName"]}\nCV : {profile[1]["infoName"]}')

            # Get each voice records from
            # https://aceship.github.io/AN-EN-Tags/etc/voice/
            space = '\u2000'  # Backslashes may not appear inside the expression portions of f-strings
            [embed.add_field(name=voice["voiceTitle"],
                             value=f'[▶️](https://aceship.github.io/AN-EN-Tags/etc/voice/{voice["voiceAsset"]}.mp3){space}{voice["voiceText"].replace("{@nickname}", "???")}', inline=False) for voice in info[1][lgt*i//3:(lgt*(i+1)//3 if i < 2 else lgt)]]

            # FYI
            embed.set_footer(
                text="In case you didn't notice, you can click on the icon ▶️ to listen to the audio records !")

            # Add image to make the embed less boring with text only
            # https://github.com/Aceship/AN-EN-Tags/tree/master/img
            embed.set_thumbnail(
                url=f'https://raw.githubusercontent.com/Aceship/AN-EN-Tags/master/img/portraits/{pathname2url(info[1][0]["charId"])}_1.png')

            embeds.append(embed)

        # Start paginator
        pgnt = paginator.BotEmbedPaginator(ctx, embeds)
        await pgnt.run()

    @operator.command(brief="Shows operator's skins info", usage="[operator]")
    async def skins(self, ctx, *, operator=None):
        """
        Detailed informations of specified operator's skins

        E.g: ;operator skins Angelina
        """

        if operator is None:
            raise OperatorCogError("You need to provide an operator name!")

        # Get skin info
        info = arknights.get_operator_skins(operator)

        embeds = []
        for skin in info:
            # Regex for stuffs like <color name=#ffffff>Bla bla bla</color>
            color = 0x000000
            content = skin["displaySkin"]["content"]
            if content is not None:
                pattern = re.compile(
                    r"<color name=(#[0-9a-f]{6})>(.*)</color>", re.DOTALL
                )
                m = pattern.match(content)
                if m is not None:
                    color = int(m.group(1).replace("#", "0x"), 16)
                    content = m.group(2)

            embed = Embed(
                title=f'{skin["displaySkin"]["skinName"] or skin["displaySkin"]["modelName"]} ({skin["displaySkin"]["skinGroupName"]})',
                description=(
                    content or "No description available"),
                color=color,
            )

            details = f'• Model : {skin["displaySkin"]["modelName"]}\n• Design : {skin["displaySkin"]["drawerName"]}\n'
            # Checks are important because some of the value can be None
            if (
                skin["displaySkin"]["dialog"] is not None
                and skin["displaySkin"]["dialog"] not in content
            ):
                details += f'• Dialog : {skin["displaySkin"]["dialog"]}\n'
            if skin["displaySkin"]["usage"] is not None:
                details += f'• Usage : {skin["displaySkin"]["usage"]}\n'
            if skin["displaySkin"]["description"] is not None:
                details += f'• Description : {skin["displaySkin"]["description"]}\n'
            if skin["displaySkin"]["obtainApproach"] is not None:
                details += (
                    f'• How to obtain : {skin["displaySkin"]["obtainApproach"]}\n'
                )
            embed.add_field(name="Details", value=details, inline=False)

            # Get item image from
            # https://github.com/Aceship/AN-EN-Tags/tree/master/img
            embed.set_image(
                url=f'https://raw.githubusercontent.com/Aceship/AN-EN-Tags/master/img/characters/{pathname2url(skin["portraitId"])}.png')
            embed.set_thumbnail(
                url=f'https://raw.githubusercontent.com/Aceship/AN-EN-Tags/master/img/portraits/{pathname2url(skin["portraitId"].replace("+", "a").replace("#", "b" if skin["displaySkin"]["modelName"] == "Amiya" else ""))}.png')

            embeds.append(embed)

        # Start paginator
        pgnt = paginator.BotEmbedPaginator(ctx, embeds)
        await pgnt.run()

    @operator.command(brief="Shows operator's skills info", usage="[operator]")
    async def skills(self, ctx, *, operator=None):
        """
        Detailed informations of specified operator's skins

        E.g: ;operator skills Angelina
        """

        if operator is None:
            raise OperatorCogError("You need to provide an operator name!")

        # Get skills list
        info = arknights.get_operator_skills(operator)

        await ctx.send(embed=discord_common.embed_info("Command under construction"))

    @discord_common.send_error_if(OperatorCogError)
    async def cog_command_error(self, ctx, error):
        logging.exception(error)
        pass


def setup(bot):
    bot.add_cog(Operator(bot))
