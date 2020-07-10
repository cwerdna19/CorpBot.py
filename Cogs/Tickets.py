import asyncio, discord, random
from   discord.ext import commands
from   Cogs import Utils, Settings, DisplayName, UserTime, PickList

def setup(bot):
    # Add the bot and deps
    settings = bot.get_cog("Settings")
    bot.add_cog(Tickets(bot, settings))

class Tickets(commands.Cog):

    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
        self.ticketactive = {}
        global Utils, DisplayName
        Utils = self.bot.get_cog("Utils")
        DisplayName = self.bot.get_cog("DisplayName")
        self.tickets = {}
        
    def useTickets(self, server):
        
        return

    @commands.command()
    async def allowtickets(self, ctx, *, allow: str = None):
        if not await Utils.is_admin_reply(ctx): return
        
        if allow == None:
            msg = 'Please use **yes** or **no** to allow tickets on your server.'
        elif lower(allow) == 'yes':
            self.settings.setServerStat(ctx.guild, "UseTickets", True)
            msg = f'Tickets are now enabled. Use {ctx.prefix}newticket to get started.'
        elif lower(allow) == 'no':
            self.settings.setServerStat(ctx.guild, "UseTickets", False)
            msg = 'Tickets are now disabled.'
            
        await ctx.send(msg)
        
    @commands.command(pass_context=True)
    async def setticketchannel(self, ctx, *, channel: discord.TextChannel = None):
        """Sets the channel for Tickets (admin only)."""

        if not await Utils.is_admin_reply(ctx): return

        if channel == None:
            self.settings.setServerStat(ctx.guild, "TicketsChannel", "")
            msg = 'Tickets work *only* in pm now.'
            return await ctx.send(msg)

        # If we made it this far - then we can add it
        self.settings.setServerStat(ctx.guild, "TicketsChannel", channel.id)

        msg = 'Tickets channel set to **{}**.'.format(channel.name)
        await ctx.send(Utils.suppressed(ctx,msg))
        
    @commands.command()
    async def newticket(self, ctx):
        """Initiate a new-ticket conversation with the bot. The ticket will be added to the bottom of the queue"""
        
        enabled = self.settings.getServerStat(ctx.guild, "UseTicketing")
        
        # If Tickets aren't enabled,
        
        if not enabled:
            msg = 'Tickets aren\'t enabled for this server. Admins can enable tickets with {}allowtickets [yes/no]'.format(ctx.prefix)
            return await ctx.send(msg)
        
        queue = self.settings.getServerStat(ctx.guild, "")
        
        server = ctx.message.guild.id
        
        ticketChannel = None
        if ctx.guild:
            # Not a pm
            ticketChannel = self.settings.getServerStat(ctx.guild, "TicketsChannel")
            if not (not ticketChannel or ticketChannel = ""):
                # Need channel ID
                if not str(ticketChannel) == str(ctx.channel.id):
                    msg = 'This isn\'t the channel for that...'
                    for chan in ctx.guild.channels:
                        if str(chan.id) == str(ticketChannel):
                            msg = 'This isn\'t the channel for that. Please use the **{}** channel for tickets.'.format(chan.name)
                        return await ctx.send(msg)
                else:
                    ticketChannel = self.bot.get_channel(ticketChannel)
        if not ticketChannel:
            # No channel set - use PM
            ticketChannel = ctx.author
            
        # Ensure not in ticket session already
        if str(ctx.author.id) in self.ticketactive:
            return await ctx.send("You're already in a ticket session! You can leave with `{}cancelhw`".format(ctx.prefix))
            
        # Set TicketActive flag
        ticket_id = self.gen_id()
        self.ticketactive[str(ctx.author.id)] = ticket_id
        
        msg = 'Alright, *{}*, let\'s make a new ticket.\n\n'.format(DisplayName.name(ctx.author))
        try:
            await ticketChannel.send(msg)
        except:
            # Can't send message
            self._stop_ticket(ctx.author)
            if ticketChannel == ctx.author:
                # Must not allow PMs
                await ctx.send("It looks like you don't accept PMs. Please enable them and try again.")
            return
        
        if ticketChannel = ctx.author and ctx.channel != ctx.author.dm_channel:
            await ctx.message.add_reaction("📬")
        msg = '*{}*, What should the subject of the ticket be? Be concise but descriptive. For example, "Error code 0xc0000001 on boot" is better than "My PC won\'t start". (type stop to cancel):'.format(DisplayName.name(ctx.author)
        
        # Get the ticket name
        newTicket = {}
        
        while True:
            ticketName = await self.prompt(ticket_id, ctx, msg, ticketChannel, DisplayName.name(ctx.author))
            
        
        for x in qs:
            if x['serverID'] == server:
                return
                
        await ctx.send(self.queues['serverID']['ticketNum'])
        
    #def gen_id()
    
    #def prompt()
    
    # def _stop_ticket()
    
    #def ticket_timeout()

"""        
    @commands.command()
    async def tickets():
        
        
    @commands.command()
    async def closeticket():
        return
"""