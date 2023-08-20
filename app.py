### Import Module ###
import nextcord, toss, sqlite3, random
from nextcord.ext import commands
from nextcord import SlashOption, User

### Config ###
config = {
    ### Discord Config ###
    "token": "",
    "guild_id": 1231313,
    "bot_status": "로나랜드 오리지널",
    ### Toss Config ###
    "toss_token": "",
    "toss_id": ""
}

AdminList = []

### Function ###
def makeTossRequest(amount):
    result = toss.request(token=config['toss_token'], toss_id=config["toss_id"], amount=amount)    
    if result == 'FAIL':
        return False
    else:
        return result

def getTossConfirm(code):
    result = toss.confirm(token=config["toss_token"], code=code)
    if result['result'] == 'FAIL':
        return False, result['message']
    else:
        return True, result['message']

def checkUser(id):
    con = sqlite3.connect('./database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM user WHERE id == ?;", (id,))
    result = cur.fetchone()
    con.close()
    if result == None:
        return False
    else:
        return True

def makeUserData(id):
    con = sqlite3.connect('./database.db')
    cur = con.cursor()
    cur.execute("INSERT INTO user VALUES(?, ?, ?)", (id, 0, '0:0') )
    con.commit()
    con.close()
    return True

def makeEmbed(code, des):
    if code == 'error':
        embed = nextcord.Embed(
            title='로나랜드 오류알림',
            description=f'**```css\n[ ⛔ ] {des}```**'
        )
    return embed

def getUserMoney(id):
    con = sqlite3.connect('./database.db')
    cur = con.cursor()
    cur.execute(f'SELECT * FROM user WHERE id = {id}')
    result = cur.fetchone()
    con.close()
    return result[1]

def removeUserMoney(id, money):
    last_money = getUserMoney(id)
    new_money = int(last_money) - int(money)
    con = sqlite3.connect('./database.db')
    cur = con.cursor()
    cur.execute("UPDATE user SET money = ? WHERE id == ?;", (new_money, id))
    con.commit()
    con.close()
    return True

def adminAddUserMoney(id, money):
    con = sqlite3.connect('./database.db')
    cur = con.cursor()
    cur.execute("UPDATE user SET money = ? WHERE id == ?;", (money, id))
    con.commit()
    cur.execute("UPDATE user SET roll = ? WHERE id == ?;", (f'{money}:0', id))
    con.commit()
    con.close()
    return True

def addUserMoney(id, money):
    con = sqlite3.connect('./database.db')
    cur = con.cursor()
    cur.execute(f"SELECT * FROM user WHERE id = {id}")
    result = cur.fetchone()
    last_money = result[1]
    new_money = int(last_money) + int(money)
    cur.execute("UPDATE user SET money = ? WHERE id == ?;", (new_money, id))
    con.commit()
    con.close()
    return True

def addRolling(id, money):
    con = sqlite3.connect('./database.db')
    cur = con.cursor()
    cur.execute(f"SELECT * FROM user WHERE id = {id}")
    charge_money = cur.fetchone()[2].split(':')[0]
    cur.execute(f"SELECT * FROM user WHERE id = {id}")
    last_money = int(cur.fetchone()[2].split(':')[1])
    new_money = last_money + int(money)
    cur.execute("UPDATE user SET roll = ? WHERE id == ?;", (f'{charge_money}:{new_money}', id))
    con.commit()
    con.close()
    return True

def checkRolling(id):
    con = sqlite3.connect('./database.db')
    cur = con.cursor()
    cur.execute(f"SELECT * FROM user WHERE id = {id}")
    charge_money = int(cur.fetchone()[2].split(':')[0])
    cur.execute(f"SELECT * FROM user WHERE id = {id}")
    last_money = int(cur.fetchone()[2].split(':')[1])
    con.close()
    if charge_money * 2 < last_money:
        return True, '롤링완료'
    else:
        return False, (charge_money * 2) - last_money 

def resetRolling(id):
    con = sqlite3.connect('./database.db')
    cur = con.cursor()
    cur.execute("UPDATE user SET roll = ? WHERE id == ?;", (f'0:0', id))
    con.commit()
    cur.execute("UPDATE user SET money = ? WHERE id == ?;", (f'0', id))
    con.commit()
    con.close()
    return True

### Nextcord ###
intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Game(config["bot_status"]), status=nextcord.Status.online)
    print("""
    ⠀⠀⠀⠀⢀⣤⣶⣶⣶⣦⣄⠀⠀⣶⣶⣆⠀⠀⢰⣶⡆⠀⣶⣶⡆⠀⠀⠀⣶⣶⠀⢰⣶⣶⣄⠀⠀⢰⣶⡆⠀⣶⣶⣶⣶⣶⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⠟⠉⠙⢿⣿⣆⠀⣿⣿⣿⣦⠀⢸⣿⡇⠀⣿⣿⡇⠀⠀⠀⣿⣿⠀⢸⣿⣿⣿⣦⠀⢸⣿⡇⠀⣿⣿⡏⠉⠉⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⠀⠀⠀⢸⣿⣿⠀⣿⣿⠹⣿⣷⣸⣿⡇⠀⣿⣿⡇⠀⠀⠀⣿⣿⠀⢸⣿⣿⠻⣿⣧⣸⣿⡇⠀⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣆⣀⣠⣾⣿⠏⠀⣿⣿⠀⠘⢿⣿⣿⡇⠀⣿⣿⣇⣀⣀⠀⣿⣿⠀⢸⣿⣿⠀⠙⣿⣿⣿⡇⠀⣿⣿⣇⣀⣀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⠿⠿⠿⠿⠋⠀⠀⠿⠿⠀⠀⠈⠿⠿⠇⠀⠿⠿⠿⠿⠿⠇⠿⠿⠀⠸⠿⠿⠀⠀⠈⠿⠿⠇⠀⠿⠿⠿⠿⠿⠃⠀⠀⠀⠀⠀⠀""")

### Nextcord Admin Commands ###
@bot.slash_command(description=f"로나랜드 수동 충전ㅣ관리자용", guild_ids=[config["guild_id"]])
async def 수동충전(interaction: nextcord.Interaction, 금액:int,유저:User):
    if not interaction.user.id in AdminList:
        return await interaction.send('허가되지 않은 접근입니다.', ephemeral=True)

    userResult = checkUser(유저.id) 
    if userResult == False: 
        makeUserData(유저.id) 
    
    adminAddUserMoney(유저.id, 금액)

    embed = nextcord.Embed(
            title='로나랜드 수동충전',
            description=f'**```css\n[ ✅ ] 성공적으로 유저에게 코인을 지급하였습니다.```**\n**```유저 ID : {유저.id}\n충전금 : {금액} 원\n유저 잔액 : {getUserMoney(유저.id)} 원```**'
        )
    
    await interaction.send(embed=embed)

@bot.slash_command(description=f"로나랜드 코인 회수ㅣ관리자용", guild_ids=[config["guild_id"]])
async def 회수(interaction: nextcord.Interaction, 금액:int, 유저:User):
    if not interaction.user.id in AdminList:
        return await interaction.send('**__허가되지 않은 접근입니다.__**', ephemeral=True)

    userResult = checkUser(유저.id) 
    if userResult == False: 
        makeUserData(유저.id) 

    if 금액 > int(getUserMoney(유저.id)):
        return await interaction.send(embed=makeEmbed('error', '잔액이 부족합니다...'), ephemeral=True)

    removeUserMoney(유저.id, 금액)

    embed = nextcord.Embed(
            title='로나랜드 코인회수',
            description=f'**```css\n[ ✅ ] 성공적으로 유저에게 코인을 회수하였습니다.```**\n**```유저 ID : {유저.id}\n회수금 : {금액} 원\n유저 잔액 : {getUserMoney(유저.id)} 원```**'
        )
    
    await interaction.send(embed=embed)

### Nextcord User Commands ###
@bot.slash_command(description=f"로나랜드 잔액 충전", guild_ids=[config["guild_id"]])
async def 충전(interaction: nextcord.Interaction, 금액:int):
    userResult = checkUser(interaction.user.id) 
    if userResult == False: 
        makeUserData(interaction.user.id) 
    tossResult = makeTossRequest(금액)
    if tossResult == False:
        return await interaction.send(embed=makeEmbed('error', '충전 신청 중 오류가 발생하였습니다...'), ephemeral=True)
   
    class confirm(nextcord.ui.View):
        def __init__(self):
            super().__init__()
            self.value = None
        @nextcord.ui.button(label = '입금완료', style=nextcord.ButtonStyle.green)
        async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            self.value = True
            self.stop()
    view = confirm()
    embed = nextcord.Embed(
        title='로나랜드 충전신청',
        description=f'**```css\n[ ✅ ] 성공적으로 충전신청을 진행했습니다.```**\n**```입금자명 : {tossResult[0]}\n입금계좌 : {tossResult[1]}```**\n**```❗❗❗ 꼭 입금을 완료하신 뒤 " 입금완료 " 버튼을 눌러주세요.```**'
    )
    await interaction.send(embed=embed, view=view, ephemeral=True)
    await view.wait()

    if view.value:
        result = getTossConfirm(tossResult[0])
        if result[0] == True:
            try:
                con = sqlite3.connect('./database.db')
                cur = con.cursor()
                cur.execute(f'SELECT * FROM user WHERE id = {interaction.user.id}')
                result1 = cur.fetchone()
                last_m = result1[1]
                new_m = int(last_m) + int(금액)
                cur.execute("UPDATE user SET money = ? WHERE id == ?;", (new_m, interaction.user.id))
                con.commit()
                con.close()
                embed = nextcord.Embed(
                    title='로나랜드 충전성공',
                    description=f'**```css\n[ ✅ ] 성공적으로 충전을 진행했습니다.```**\n**```이전 잔액 : {last_m}\n신규 잔액 : {new_m}```**'
                )
                return await interaction.send(embed=embed, ephemeral=True)
            except Exception as e:
                print(e)
                return await interaction.send(embed=makeEmbed('error', '처리 도중 알 수 없는 오류가 발생하였습니다...'), ephemeral=True)
        elif result[0] == False:
            return await interaction.send(embed=makeEmbed('error', f'{result[1]}'), ephemeral=True)
        else:
            return await interaction.send(embed=makeEmbed('error', '처리 도중 알 수 없는 오류가 발생하였습니다...'), ephemeral=True)

@bot.slash_command(description=f"로나랜드 잔액 확인", guild_ids=[config["guild_id"]])
async def 잔액(interaction: nextcord.Interaction):
    userResult = checkUser(interaction.user.id) 
    if userResult == False: 
        makeUserData(interaction.user.id) 
    
    con = sqlite3.connect('./database.db')
    cur = con.cursor()
    cur.execute(f'SELECT * FROM user WHERE id = {interaction.user.id}')
    result = cur.fetchone()
    embed = nextcord.Embed(
            title='로나랜드 잔액확인',
            description=f'**```css\n[ ✅ ] 성공적으로 잔액을 확인했습니다.```**\n**```잔액 : {result[1]} 원```**'
        )
    await interaction.send(embed=embed)

@bot.slash_command(description=f"로나랜드 롤링 확인", guild_ids=[config["guild_id"]])
async def 롤링(interaction: nextcord.Interaction):
    result = checkRolling(interaction.user.id)
    if result[0] == False:
        embed = nextcord.Embed(
                title='로나랜드 롤링확인',
                description=f'**```css\n[ ⛔ ] 롤링을 완료하지 못했습니다.\n남은 롤링액은 : {result[1]} 원 입니다.```**'
            )
        await interaction.send(embed=embed)
    elif result:
        embed = nextcord.Embed(
                title='로나랜드 롤링확인',
                description=f'**```css\n[ ✅ ] 성공적으로 롤링을 완료했습니다.```**'
            )
        await interaction.send(embed=embed)
    
@bot.slash_command(description=f"로나랜드 롤링 초기화ㅣ주의 돈도 초기화됩니다.", guild_ids=[config["guild_id"]])
async def 롤링초기화(interaction: nextcord.Interaction):
    result = resetRolling(interaction.user.id)
    if result:
        embed = nextcord.Embed(
                title='로나랜드 롤링 초기화',
                description=f'**```css\n[ ✅ ] 성공적으로 롤링/잔여금 을 초기화했습니다.```**'
            )
        await interaction.send(embed=embed)

@bot.slash_command(description=f"로나랜드 오리지널 다이스", guild_ids=[config["guild_id"]])
async def 다이스(interaction: nextcord.Interaction, 배팅액:int, 언옵:str = SlashOption(name='언옵', choices={"언더": 'UNDER', "오버": 'OVER'})):
    num = random.randint(1, 6)
    userResult = checkUser(interaction.user.id) 
    if userResult == False: 
        makeUserData(interaction.user.id) 
    
    if 배팅액 > int(getUserMoney(interaction.user.id)):
        return await interaction.send(embed=makeEmbed('error', '잔액이 부족합니다...'))
    addRolling(interaction.user.id, 배팅액)
    if removeUserMoney(interaction.user.id, 배팅액):
        if num >= 4:
            if 언옵 == 'OVER': # 승리 
                addUserMoney(interaction.user.id, round(배팅액 * 1.8))
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 다이스',
                    description=f'**```css\n[ ✅ ] 다이스 진행 결과.. 승리```**\n**```주사위 : {num}ㅣ결과 : 오버ㅣ배팅 : 오버ㅣ승리금 : {round(배팅액 * 1.8)} 원```**'
                )
                await interaction.send(embed=embed)
            elif 언옵 == 'UNDER': #패배 
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 다이스',
                    description=f'**```css\n[ ✅ ] 다이스 진행 결과.. 패배```**\n**```주사위 : {num}ㅣ결과 : 오버ㅣ배팅 : 언더ㅣ패배금 : {배팅액} 원```**'
                )
                await interaction.send(embed=embed)
        if num <= 3:
            if 언옵 == 'UNDER': # 승리 
                addUserMoney(interaction.user.id, round(배팅액 * 1.8))
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 다이스',
                    description=f'**```css\n[ ✅ ] 다이스 진행 결과.. 승리```**\n**```주사위 : {num}ㅣ결과 : 언더ㅣ배팅 : 언더ㅣ승리금 : {round(배팅액 * 1.8)} 원```**'
                )
                await interaction.send(embed=embed)
            else: #패배 
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 다이스',
                    description=f'**```css\n[ ✅ ] 다이스 진행 결과.. 패배```**\n**```주사위 : {num}ㅣ결고 : 언더ㅣ배팅 : 오버ㅣ패배금 : {배팅액} 원```**'
                )
                await interaction.send(embed=embed)
                
@bot.slash_command(description=f"로나랜드 오리지널 온오프", guild_ids=[config["guild_id"]])
async def 온오프(interaction: nextcord.Interaction, 배팅액:int, 온오프:str = SlashOption(name='온오프', choices={"온라인": 'ON', "오프라인": 'OFF'})):
    num = random.randint(0, 1)
    userResult = checkUser(interaction.user.id) 
    if userResult == False: 
        makeUserData(interaction.user.id) 
    
    if 배팅액 > int(getUserMoney(interaction.user.id)):
        return await interaction.send(embed=makeEmbed('error', '잔액이 부족합니다...'))
    addRolling(interaction.user.id, 배팅액)
    if removeUserMoney(interaction.user.id, 배팅액):
        if num == 0:
            if 온오프 == 'ON': # 승리 
                addUserMoney(interaction.user.id, round(배팅액 * 1.5))
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 온오프',
                    description=f'**```css\n[ ✅ ] 온오프 진행 결과.. 승리```**\n**```결과 : 온라인ㅣ배팅 : 온라인ㅣ승리금 : {round(배팅액 * 1.5)} 원```**'
                )
                await interaction.send(embed=embed)
            else: #패배 
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 온오프',
                    description=f'**```css\n[ ✅ ] 온오프 진행 결과.. 패배```**\n**```결과 : 온라인ㅣ배팅 : 오프라인ㅣ패배금 : {배팅액} 원```**'
                )
                await interaction.send(embed=embed)
        
        if num == 1:
            if 온오프 == 'OFF': # 승리 
                addUserMoney(interaction.user.id, round(배팅액 * 1.5))
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 온오프',
                    description=f'**```css\n[ ✅ ] 온오프 진행 결과.. 승리```**\n**```결과 : 오프라인ㅣ배팅 : 오프라인ㅣ승리금 : {round(배팅액 * 1.5)} 원```**'
                )
                await interaction.send(embed=embed)
            else: #패배 
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 온오프',
                    description=f'**```css\n[ ✅ ] 온오프 진행 결과.. 패배```**\n**```결과 : 오프라인ㅣ배팅 : 온라인ㅣ패배금 : {배팅액} 원```**'
                )
                await interaction.send(embed=embed)

@bot.slash_command(description=f"로나랜드 오리지널 말달리기", guild_ids=[config["guild_id"]])
async def 말달리기(interaction: nextcord.Interaction, 배팅액:int, 말:int = SlashOption(name='말', choices={"1번말": 1, "2번말": 2, "3번말": 3, "4번말": 4, "5번말": 5})):
    arr = [1, 2, 3, 4, 5]
    random.shuffle(arr) # 왼쪽에서부터 1등

    userResult = checkUser(interaction.user.id) 
    if userResult == False: 
        makeUserData(interaction.user.id) 
    
    if 배팅액 > int(getUserMoney(interaction.user.id)):
        return await interaction.send(embed=makeEmbed('error', '잔액이 부족합니다...'))
    addRolling(interaction.user.id, 배팅액)
    if removeUserMoney(interaction.user.id, 배팅액):
            if arr[0] == 말: # 1등 
                addUserMoney(interaction.user.id, round(배팅액 * 2))
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 말달리기',
                    description=f'**```css\n[ ✅ ] 말달리기 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ배팅 : {말}번말ㅣ승리금 : {round(배팅액 * 2)} 원```**\n**```{arr}```**'
                )
                await interaction.send(embed=embed)
            elif arr[1] == 말: # 2등
                addUserMoney(interaction.user.id, round(배팅액 * 1.7))
                embed = nextcord.Embed(
                    title='로나랜드 오리지널 말달리기',
                    description=f'**```css\n[ ✅ ] 말달리기 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ배팅 : {말}번말ㅣ승리금 : {round(배팅액 * 1.7)} 원```**\n**```{arr}```**'
                )
                await interaction.send(embed=embed)
            else:
                embed = nextcord.Embed(
                        title='로나랜드 오리지널 말달리기',
                        description=f'**```css\n[ ✅ ] 말달리기 진행 결과.. 패배```**\n**```경기결과 : [하단참조]ㅣ배팅 : {말}번말ㅣ패배금 : {배팅액} 원```**\n**```{arr}```**'
                    )
                await interaction.send(embed=embed)

@bot.slash_command(description=f"로나랜드 오리지널 마리오", guild_ids=[config["guild_id"]])
async def 마리오(interaction: nextcord.Interaction, 배팅액:int):
    arr = ['A', 'J', 'M', 'T', 'F', 'F', 'F', 'F', 'F']
    random.shuffle(arr) # A , J 조커 , M 마리오 , T 터틀 , F 탈락

    userResult = checkUser(interaction.user.id) 
    if userResult == False: 
        makeUserData(interaction.user.id) 
    
    if 배팅액 > int(getUserMoney(interaction.user.id)):
        return await interaction.send(embed=makeEmbed('error', '잔액이 부족합니다...'))
    
    addRolling(interaction.user.id, 배팅액)

    if removeUserMoney(interaction.user.id, 배팅액):
        if arr[0] == 'A':
            addUserMoney(interaction.user.id, round(배팅액 * 2))
            embed = nextcord.Embed(
                    title='로나랜드 오리지널 마리오',
                    description=f'**```css\n[ ✅ ] 마리오 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 2)} 원```**\n**```{arr}```**'
                )
            await interaction.send(embed=embed)
        elif arr[0] == 'J':
            addUserMoney(interaction.user.id, round(배팅액 * 2.5))
            embed = nextcord.Embed(
                    title='로나랜드 오리지널 마리오',
                    description=f'**```css\n[ ✅ ] 마리오 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 2.5)} 원```**\n**```{arr}```**'
                )
            await interaction.send(embed=embed)
        elif arr[0] == 'M':
            addUserMoney(interaction.user.id, round(배팅액 * 3))
            embed = nextcord.Embed(
                    title='로나랜드 오리지널 마리오',
                    description=f'**```css\n[ ✅ ] 마리오 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 3)} 원```**\n**```{arr}```**'
                )
            await interaction.send(embed=embed)
        elif arr[0] == 'T':
            addUserMoney(interaction.user.id, round(배팅액 * 0.5))
            embed = nextcord.Embed(
                    title='로나랜드 오리지널 마리오',
                    description=f'**```css\n[ ✅ ] 마리오 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 0.5)} 원```**\n**```{arr}```**'
                )
            await interaction.send(embed=embed)
        elif arr[0] == 'F':
            embed = nextcord.Embed(
                    title='로나랜드 오리지널 마리오',
                    description=f'**```css\n[ ✅ ] 마리오 진행 결과.. 패배```**\n**```경기결과 : [하단참조]ㅣ패배금 : {배팅액} 원```**\n**```{arr}```**'
                )
            await interaction.send(embed=embed)
        
@bot.slash_command(description=f"로나랜드 오리지널 로또", guild_ids=[config["guild_id"]])
async def 로또(interaction: nextcord.Interaction, 배팅액:int, 일번볼:int, 이번볼:int, 삼번볼:int, 사번볼:int, 오번볼:int, 육번볼:int, 칠번볼:int,):
    userResult = checkUser(interaction.user.id) 
    if userResult == False: 
        makeUserData(interaction.user.id) 
    
    if 배팅액 > int(getUserMoney(interaction.user.id)):
        return await interaction.send(embed=makeEmbed('error', '잔액이 부족합니다...'))
    
    addRolling(interaction.user.id, 배팅액)

    user_data = {
        "1" : 일번볼,
        "2" : 이번볼,
        "3" : 삼번볼,
        "4" : 사번볼,
        "5" : 오번볼,
        "6" : 육번볼,
        "7" : 칠번볼,
    }
    server_data = {
        "1" : random.randint(1,10),
        "2" : random.randint(1,10),
        "3" : random.randint(1,10),
        "4" : random.randint(1,10),
        "5" : random.randint(1,10),
        "6" : random.randint(1,10),
        "7" : random.randint(1,10),
    }
    true_data = 0 
    for i in range(7):
        if user_data[f"{i + 1}"] == server_data[f"{i + 1}"]:
            true_data = true_data + 1
    
    if removeUserMoney(interaction.user.id, 배팅액):
        if true_data == 6:
            addUserMoney(interaction.user.id, round(배팅액 * 8))
            embed = nextcord.Embed(
                    title='로나랜드 오리지널 로또',
                    description=f'**```css\n[ ✅ ] 로또 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 8)} 원```**\n**```서버 결과\nㄴ {server_data}\n유저 결과\nㄴ {user_data}\n당첨볼 : {true_data} 개```**'
                )
            return await interaction.send(embed=embed)
        elif true_data >= 4:
            addUserMoney(interaction.user.id, round(배팅액 * 4))
            embed = nextcord.Embed(
                    title='로나랜드 오리지널 로또',
                    description=f'**```css\n[ ✅ ] 로또 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 4)} 원```**\n**```서버 결과\nㄴ {server_data}\n유저 결과\nㄴ {user_data}\n당첨볼 : {true_data} 개```**'
                )
            return await interaction.send(embed=embed)
        elif true_data >= 3:
            addUserMoney(interaction.user.id, round(배팅액 * 2))
            embed = nextcord.Embed(
                    title='로나랜드 오리지널 로또',
                    description=f'**```css\n[ ✅ ] 로또 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 2)} 원```**\n**```서버 결과\nㄴ {server_data}\n유저 결과\nㄴ {user_data}\n당첨볼 : {true_data} 개```**'
                )
            return await interaction.send(embed=embed)
        elif true_data >= 2:
            addUserMoney(interaction.user.id, round(배팅액 * 0.5))
            embed = nextcord.Embed(
                    title='로나랜드 오리지널 로또',
                    description=f'**```css\n[ ✅ ] 로또 진행 결과.. 승리```**\n**```경기결과 : [하단참조]ㅣ승리금 : {round(배팅액 * 0.5)} 원```**\n**```서버 결과\nㄴ {server_data}\n유저 결과\nㄴ {user_data}\n당첨볼 : {true_data} 개```**'
                )
            return await interaction.send(embed=embed)
        elif true_data <= 1:
            embed = nextcord.Embed(
                    title='로나랜드 오리지널 로또',
                    description=f'**```css\n[ ✅ ] 로또 진행 결과.. 패배```**\n**```경기결과 : [하단참조]ㅣ패배금 : {배팅액} 원```**\n**```서버 결과\nㄴ {server_data}\n유저 결과\nㄴ {user_data}\n당첨볼 : {true_data} 개```**'
                )
            await interaction.send(embed=embed)
    
bot.run(config["token"])