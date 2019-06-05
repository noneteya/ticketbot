import discord
from discord.ext import commands
import typing
import asyncio


def setup(bot):
    bot.add_cog(Ticket(bot))


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.settings = {
            585045504170262529: {
                "ticket_id": 0,
                "tickets_category": None,
                "archives_cartegory": None,
                "editing_ticket": None,
                "admin_role": None
            }
        }

    @commands.Cog.listener()
    async def on_ready(self):

        for i in self.settings.keys():
            guild = discord.utils.get(self.bot.guilds, id=i)

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True)
            }

            self.settings[guild.id]["tickets_category"] = discord.utils.get(guild.categories, name='tickets').id
            self.settings[guild.id]["archives_category"] = discord.utils.get(guild.categories, name='archives').id

            if self.settings[guild.id]["tickets_category"] is None:
                tc = await guild.create_category("tickets", overwrites=overwrites)
                self.settings[guild.id]["tickets_category"] = tc.id

            if self.settings[guild.id]["archives_category"] is None:
                ac = await guild.create_category("archives", overwrites=overwrites)
                self.settings[guild.id]["archive_category"] = ac.id

            if len(guild.me.display_name.split()) == 1:
                self.settings[guild.id]["ticket_id"] = 0
                await guild.me.edit(nick=f"{guild.me.display_name} {self.settings[guild.id]['ticket_id']}")
            else:
                self.settings[guild.id]["ticket_id"] = int(guild.me.display_name.split()[1])

        print("ready")

    @commands.command()
    async def new(self, ctx, *, arg):
        arg = arg.replace(" ", "-").lower()
        guild = ctx.author.guild

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            ctx.author: discord.PermissionOverwrite(read_messages=True)
        }

        self.settings[guild.id]['ticket_id'] += 1
        ticket_channel = await guild.create_text_channel(f"ticket-{ self.settings[guild.id]['ticket_id'] }-{ arg }", category=discord.utils.get(guild.categories, id=self.settings[guild.id]["tickets_category"]), overwrites=overwrites, topic=f"{arg},{ctx.author.id}")

        embed = discord.Embed(title="New Ticket Created", description="新しいチケットを作成しました", color=0xdea1ff)
        embed.add_field(name="チャンネル", value=ticket_channel.mention, inline=True)
        embed.add_field(name="トピック", value=arg, inline=True)
        embed.set_footer(text="Made by Noneteya")

        await ctx.send(embed=embed)

        display_name = guild.me.display_name.split()[0]
        await guild.me.edit(nick=f"{display_name} {self.settings[guild.id]['ticket_id']}")

    @commands.command()
    async def add(self, ctx, user: discord.Member, channel: discord.TextChannel = None):
        guild = ctx.author.guild

        if channel is None:
            channel = ctx.message.channel

        if user == self.bot.user:
            embed = discord.Embed(title="Error", description="Botは追加も削除もできません", color=0xdea1ff)
            embed.set_footer(text="Made by Noneteya")

            await channel.send(embed=embed)

        if "ticket-" in channel.name:
            await channel.set_permissions(user, read_messages=True)

            embed = discord.Embed(title="Member Removed", description="メンバーをトピックに追加しました", color=0xdea1ff)
            embed.add_field(name="メンバー", value=user.mention, inline=True)
            embed.set_footer(text="Made by Noneteya")

            await channel.send(embed=embed)

    @commands.command()
    async def remove(self, ctx, user: discord.Member, channel: discord.TextChannel = None):
        guild = ctx.author.guild

        if channel is None:
            channel = ctx.message.channel

        if user == self.bot.user:
            embed = discord.Embed(title="Error", description="Botは追加も削除もできません", color=0xdea1ff)
            embed.set_footer(text="Made by Noneteya")

            await channel.send(embed=embed)

        if "ticket-" in channel.name:
            await channel.set_permissions(user, read_messages=False)
            embed = discord.Embed(title="Member Removed", description="メンバーをトピックから削除しました", color=0xdea1ff)
            embed.add_field(name="メンバー", value=user.mention, inline=True)
            embed.set_footer(text="Made by Noneteya")

            await channel.send(embed=embed)

    @commands.command()
    async def close(self, ctx, *, reason="done"):
        guild = ctx.author.guild
        channel = ctx.message.channel

        if ("ticket-" in channel.name) and (channel != self.settings[guild.id]["editing_ticket"]):
            args = channel.topic.split(",")
            topic = args[0]
            ticket_name = channel.name
            reporter = int(args[1])
            user = await self.bot.fetch_user(reporter)

            embed = discord.Embed(title="Topic Close", description="このチャンネルを10秒後に削除します", color=0xdea1ff)
            embed.add_field(name=":mega: 報告者", value=user.mention, inline=True)
            embed.add_field(name=":speech_balloon: 理由", value=reason, inline=True)
            embed.set_footer(text="Made by Noneteya")

            await channel.send(embed=embed)

            self.settings[guild.id]["editing_ticket"] = channel
            await asyncio.sleep(10)
            await channel.delete()

            embed = discord.Embed(title="Topic Closed", description="あなたの報告したトピックが削除されました", color=0xdea1ff)
            embed.add_field(name=":ticket:  チケットID", value=ticket_name, inline=True)
            embed.add_field(name=":mega: 報告者", value=user.mention, inline=True)
            embed.add_field(name=":wastebasket: 削除者", value=user.mention, inline=True)
            embed.add_field(name=":speech_balloon: 理由", value=reason, inline=True)
            embed.set_footer(text="Made by Noneteya")

            await user.send(embed=embed)
    #
    # @commands.command()
    # async def voice(self, ctx, channel: discord.TextChannel = None):
    #     guild = ctx.author.guild
    #
    #     if channel is None:
    #         channel = ctx.message.channel
    #     print(channel.overwrites)
    #     if discord.utils.get(guild.channels, name=f"{channel.name}-voice") is None:
    #         await guild.create_voice_channel(f"{channel.name}-voice", category=self.tickets_category, overwrites=channel.overwrites)
    #         await channel.send(f"ボイスチャットを追加しました")
    #     else:
    #         await discord.utils.get(guild.channels, name=f"{channel.name}-voice").delete()
    #         await channel.send(f"ボイスチャットを削除しました")
