import discord
from discord.ext import commands
import typing
import asyncio


def setup(bot):
    bot.add_cog(Ticket(bot))


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tickets_category = None
        self.archives_cartegory = None
        self.ticket_id = 0

        self.admin_role = None
        self.editing_ticket = None

    @commands.Cog.listener()
    async def on_ready(self):
        guild = discord.utils.get(self.bot.guilds, id=585045504170262529)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }

        self.tickets_category = discord.utils.get(guild.categories, name='tickets')
        self.archives_cartegory = discord.utils.get(guild.categories, name='archives')

        if self.tickets_category is None:
            self.tickets_category = await guild.create_category("tickets", overwrites=overwrites)

        if self.archives_cartegory is None:
            self.archives_cartegory = await guild.create_category("archives", overwrites=overwrites)

        if len(guild.me.display_name.split()) == 1:
            self.ticket_id = 0
            await guild.me.edit(nick=f"{guild.me.display_name} {self.ticket_id}")
        else:
            self.ticket_id = int( guild.me.display_name.split()[1])

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

        self.ticket_id += 1
        ticket_channel = await guild.create_text_channel(f"ticket-{ self.ticket_id }-{ arg }", category=self.tickets_category, overwrites=overwrites, topic=f"{arg},{ctx.author.id}")
        await ctx.send(f"チケット { ticket_channel.mention } を作成しました")

        display_name = guild.me.display_name.split()[0]
        await guild.me.edit(nick=f"{display_name} {self.ticket_id}")

    @commands.command()
    async def add(self, ctx, user: discord.Member, channel: discord.TextChannel = None):
        guild = ctx.author.guild

        if channel is None:
            channel = ctx.message.channel

        if "ticket-" in channel.name:
            await channel.set_permissions(user, read_messages=True)
            await channel.send(f"{user.mention} をチャンネルに追加しました")

    @commands.command()
    async def remove(self, ctx, user: discord.Member, channel: discord.TextChannel = None):
        guild = ctx.author.guild

        if channel is None:
            channel = ctx.message.channel

        if "ticket-" in channel.name:
            await channel.set_permissions(user, read_messages=False)
            await channel.send(f"{user.mention} をチャンネルから削除しました")

    @commands.command()
    async def close(self, ctx, channel: discord.TextChannel = None, *, reason="done"):
        if channel is None:
            channel = ctx.message.channel

        if ("ticket-" in channel.name) and (channel != self.editing_ticket):
            await channel.send(f"このチャンネルを10秒後に削除します\nReason: {reason}")
            args = channel.topic.split(",")
            topic = args[0]
            reporter = int(args[1])
            self.editing_ticket = channel
            await asyncio.sleep(10)
            await channel.delete()
            user = await self.bot.fetch_user(reporter)
            await user.send(f"トピック {topic} はクローズされました。\nReason: {reason}")
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
