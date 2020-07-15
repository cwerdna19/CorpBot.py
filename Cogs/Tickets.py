import asyncio, discord, datetime
from    datetime import timedelta
from    discord.ext import commands
from    Cogs import Settings, DisplayName
"""
TO DO:

-Add ticket list to settings ServerStat????
-Search ticket by user name, user id, claimed, unclaimed, date

Need:
List of users with tickets open
    Must include number of tickets opened per user
    User Stat with number of tickets opened?
    User Stat with number of tickets fixed

-Finish all methods

"""
def setup(bot):
    # Add the bot and deps
    settings = bot.get_cog("Settings")
    bot.add_cog(Tickets(bot, settings))

class Tickets(commands.Cog):
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
        global DisplayName
        DisplayName = self.bot.get_cog("DisplayName")
        self.title_length = 25
        self.body_length = 500
        self.max_user_tickets = 10
        self.max_server_tickets = 1000
        self.ticket_list = {}

    class Ticket:
        """Ticket object constructor. Ticket objets are made in the process_new_ticket() method"""
        def __init__(self, title, body, owner, date, id):
            expiry_days = timedelta(days=7)
            self.title = title
            self.body = body
            self.owner_id = owner.id
            self.owner_name = owner
            self.claimed_by = None
            self.date_made = date
            self.expires_on = date + expiry_days
            self.id = id

    @commands.command()
    async def newticket(self, ctx):
        """Create a new ticket and add it to the ticket list"""

        def add_ticket(ticket):
            """Make a ticket list if one doesn't exist for a server
                Append the ticket object to the list."""
            if self.ticket_list.get(ctx.guild.id) == None:
                self.ticket_list[ctx.guild.id] = [ticket]
            else:
                self.ticket_list[ctx.guild.id].append(ticket)

        def is_author(m):
            """Return true if the message author is the user entered the command"""
            return m.author == ctx.message.author

        async def check_response():
            """"""
            return await self.bot.wait_for('message', check=is_author, timeout=30)

        async def get_ticket_item(intro, num):
            """Get ticket info from user
                `intro` is the message introducing the type of information requested.
                `num` is the maximum number of characters the user's message may contain."""
            await ctx.channel.send(intro)
            item = await check_response()
            if len(item.content) <= num:
                msg = f'This is what I got: `{item.content}`\nIs this correct? (yes/no/stop)'
                await ctx.channel.send(msg)
                response = await check_response()

                if response.content.lower() == 'yes':
                    return item.content
                elif response.content.lower() == 'no':
                    await get_ticket_item(intro, num)
                elif response.content.lower() == 'stop':
                    await ctx.channel.send(f'No problem, {DisplayName.name(ctx.author)}! See you later!')
                    return None
                else:
                    await ctx.channel.send('I don\'t know what to say to that. Try making your ticket again.')
                    return None
            else:
                msg = f'Sorry, that message is too long. Try making it shorter than {num} characters.'
                await ctx.channel.send(msg)
                await get_ticket_item(intro, num)

        async def process_new_ticket():
            """Call methods that get user's ticket info and add it to the list."""
            msg = f'Need some help, *{DisplayName.name(ctx.author)}*? Let\'s make a new ticket...\n'

            await ctx.channel.send(msg)

            msg = 'What do you need help with? This will be the title of your ticket, '
            msg += f'so please be concise ({self.title_length} characters maximum).'

            title = await get_ticket_item(msg, self.title_length)
            if title == None:
                return

            msg = f'OK! Tell me about your problem in {self.body_length} words or less.'

            body = await get_ticket_item(msg, self.body_length)
            if body == None:
                return

            user_tickets_open = self.settings.getUserStat(ctx.author, ctx.guild, "TicketsOpen")
            if not user_tickets_open:
                self.settings.setUserStat(ctx.author, ctx.guild, "TicketsOpen", 1)
            elif user_tickets_open >= self.max_user_tickets:
                return await ctx.channel.send(f'Sorry! You\'ve opened too many tickets at once. Try again when you have less than {self.max_user_tickets}.')
            else:
                self.settings.incrementStat(ctx.author, ctx.guild, "TicketsOpen", 1)
                
            server_open_tickets = self.settings.getServerStat(ctx.guild, "OpenTickets")
            if not server_open_tickets:
                self.settings.setServerStat(ctx.guild, "OpenTickets", 1)
            elif server_open_tickets > self.max_server_tickets:
                return await ctx.channel.send(f'Sorry! The server has reached it\'s ticket cap. Please try again later.')
            else:
                server_open_tickets += 1
                self.settings.setServerStat(ctx.guild, "OpenTickets", server_open_tickets)
                
            server_total_tickets = self.settings.getServerStat(ctx.guild, "TotalTickets")
            if not server_total_tickets:
                self.settings.setServerStat(ctx.guild, "TotalTickets")
            else:
                server_total_tickets += 1
                self.settings.setServerStat(ctx.guild, "TotalTickets", server_total_tickets)

            ticket = self.Ticket(title, body, ctx.message.author, datetime.date.today(), server_total_tickets)
            msg = f'Your ticket was added to the queue. Someone will @ you if they claim your ticket.'
            msg += f'\nHere\'s what your ticket looks like:\n`Title:`\n{ticket.title}\n`Message:`\n{ticket.body}'
            msg += f'\n`Owner:`\n{ticket.owner_name}'
            msg += f'\n`Date created:`\n{ticket.date_made}\n`Expires on:`\n{ticket.expires_on}\n`Claimed by:`'
            msg += f'\n{ticket.claimed_by}\n`Ticket ID:`\n{ticket.id}'
            await ctx.channel.send(msg)

            add_ticket(ticket)

        try:
            await process_new_ticket()
        except asyncio.TimeoutError:
            return await ctx.channel.send('I was waiting too long, sorry! Ask me again later if you still need help.')
    """
    @commands.command()
    async def viewtickets(self, ctx, claimed="unclaimed"):
    """"""View all unclaimed tickets
        Pass "claimed" to view claimed tickets""""""
        server = ctx.guild.id
        tickets = self.settings.getServerStat
        msg = f'Here are all the unclaimed tickets:\n\n'
        n = 0
        for ticket in tickets:
            n += 1
            msg += f'{n}. {ticket.title}\nCreated: {ticket.date_made}\nExpires: {ticket.expires_on}\n\n'
        await ctx.channel.send(msg)"""

    @commands.command()
    async def closeticket(self, ctx, *, id : int = None, user : str = None):
        #close a ticket and give credit to whoever helped you
        #must decrement stat "OpenTickets"
        #must remove ticket object from list
        #must give credit to user specified
        tickets = self.ticket_list.get(ctx.guild.id)
        realname = DisplayName.memberForName(user, ctx.guild)
        
        if id == None:
            return await ctx.channel.send('Please specify a ticket ID.')
        elif tickets is None:
            return await ctx.channel.send('Sorry, I couldn\'t find any open tickets.')
        else:
            for ticket in tickets:
            #this needs fixing, breaks after first comparison
                if ticket.id == id:
                    this_ticket = ticket
                    break
                else:
                    print('debug loop')
                    return await ctx.channel.send(f'Sorry, I can\'t find a ticket with ID {id}.')
            #this is all broken, not sure why yet
            if user != None:
                #make a function to decrement/increment ticket stat
                #make a function to decrement/increment ticket credit stat
                if realname != None:
                    #Close ticket and give credit to user specified
                    server_open_tickets = self.settings.getServerStat(ctx.guild, "OpenTickets")
                    server_open_tickets -= 1
                    self.settings.setServerStat(ctx.guild, "OpenTickets", server_open_tickets)
                    
                    user_open_tickets = self.settings.getUserStat(ctx.author, ctx.guild, "TicketsOpen")
                    user_open_tickets -= 1
                    self.settings.setUserStat(ctx.author, ctx.guild, "TicketsOpen", user_open_tickets)
                    
                    tickets.remove(this_ticket)
                    
                    #If user has no TicketCredit stat
                    if not self.settings.getUserStat(realname, ctx.guild, "TicketCredit"):
                        #Make the stat
                        self.settings.setUserStat(realname, ctx.guild, "TicketCredit", 1)
                        print(self.settings.getUserStat(realname, ctx.guild, "TicketCredit"))
                        return await ctx.channel.send(f'Ticket **{this_ticket.id}** has been deleted. Credit for fixing the issue went to *{realname}*.')
                    else:
                        #If user has TicketCredit stat increment it
                        self.settings.incrementStat(realname, ctx.guild, "TicketCredit", 1)
                        print(self.settings.getUserStat(realname, ctx.guild, "TicketCredit"))
                        return await ctx.channel.send(f'Ticket **{this_ticket.id}** has been deleted. Credit for fixing the issue went to *{realname}*.')
                else:
                    return await ctx.channel.send(f'Sorry, I can\'t find a user named *{realname}*.')
            else:
                #If no user specified, close ticket without giving credit
                server_open_tickets = self.settings.getServerStat(ctx.guild, "OpenTickets")
                server_open_tickets -= 1
                self.settings.setServerStat(ctx.guild, "OpenTickets", server_open_tickets)
                
                user_open_tickets = self.settings.getUserStat(ctx.author, ctx.guild, "TicketsOpen")
                user_open_tickets -= 1
                self.settings.setUserStat(ctx.author, ctx.guild, "TicketsOpen", user_open_tickets)
                
                tickets.remove(this_ticket)
                return await ctx.channel.send(f'Ticket **{this_ticket.id}** has been deleted. No credit was given')

    @commands.command()
    async def delticket(self, ctx):
        #delete a ticket without giving credit (maybe implement as part of $closeticket)
        return

    @commands.command()
    async def editticket(self, ctx):
        #edit an existing ticket
        return

    @commands.command()
    async def claimticket(self, ctx):
        #claim a ticket from the queue that you want to work on
        return

    @commands.command()
    async def unclaimticket(self, ctx):
        #unclaim a ticket and add it back to the queue (maybe implement as part of $claimticket)
        return
