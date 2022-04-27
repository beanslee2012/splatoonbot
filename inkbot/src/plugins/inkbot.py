
# -*- coding: utf-8 -*-
# @Time    : 2021-09-12
# @Author  : beanslee(疾风)
# @FileName: inkbot.py
# @purpose: splatoon qq bot
# @qq group id   ：929116038

import json,base64
import requests
import datetime
from datetime import datetime, timedelta
from io import BytesIO
import time
import uuid
import PIL.Image
import PIL.ImageFont
import PIL.ImageDraw
from splatoon_data import weapons,stage,subweapons,specials,subweapon_path,game_types

# import nonebot

import random
from nonebot.rule import to_me
from nonebot import get_driver, on_command, on_keyword
from nonebot.adapters.cqhttp import MessageEvent, Bot, ActionFailed, Message, GroupMessageEvent, Event
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import MessageSegment
import socket

socket.setdefaulttimeout(20)

#国服不可用utcnow
#date =datetime.utcnow().strftime('%Y-%m-%d')
date =datetime.now().strftime('%Y-%m-%d')

base_path='/root/inkbot/src/'
tmp_path = base_path+'plugins/temp/'
img_path=base_path+'resource/'
img_path_sub=base_path+'resource/subspe/'


counter=0
gamemode_rule_name ={'Clam Blitz':'蛤蜊','Tower Control':'占塔','Splat Zones':'区域','Rainmaker':'抢鱼','Turf War':'涂地'}
#gametype_name ={'蛤蜊':'Clam Blitz','塔':'Tower Control','区域':'Splat Zones','鱼':'Rainmaker','涂地':'Turf War'}


	

key_list = ['/随机武器','/图','/下图','、下图','/下下图','、下下图','/工','、工','、随机武器','、图',]





def get_counter(now ):
    global counter
    global date
    if date == now:
       counter += 1
    else:
    	 date =  datetime.now().strftime('%Y-%m-%d')
    	 counter=1

    return counter

def random_id(rtype):
 if rtype == 'wep':
   r= int(random.choice(list(weapons.keys())))
   if r<0:
     r=random_id('wep')
   else:
     return r
 elif rtype =='map':
  r=(random.choice(list(stage.keys())))
  if r.isdigit():
  	return r
  else:
  	r=random_id('map')
 else:
  pass
 
 return r


def img_to_b64(pic: PIL.Image.Image):
    buf = BytesIO()

    pic.save(buf, format="PNG")
    base64_str = base64.b64encode(buf.getbuffer()).decode()
    return "base64://" + base64_str



def circle_corner(img, radii):
    # 画圆（用于分离4个角）
    circle = PIL.Image.new('L', (radii * 2, radii * 2), 0)  # 创建黑色方形
    # circle.save('1.jpg','JPEG',qulity=100)
    draw = PIL.ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 黑色方形内切白色圆形
    # circle.save('2.jpg','JPEG',qulity=100)
    img = img.convert("RGBA")
    w, h = img.size
    alpha = PIL.Image.new('L', img.size, 255)
    alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
    alpha.paste(circle.crop((radii, 0, radii * 2, radii)),(w - radii, 0))  # 右上角
    alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)),(w - radii, h - radii))  # 右下角
    alpha.paste(circle.crop((0, radii, radii, radii * 2)),(0, h - radii))  # 左下角 
    img.putalpha(alpha)		# 白色区域透明可见，黑色区域不可见
    return img

def merge_image(base_img,tmp_img,img_x,img_y,scale):

  #加载底图
  #base_img = Image.open(u'C:\\download\\games\\bg1.png')
  #加载需要P上去的图片
  #tmp_img = Image.open(u'C:\\download\\games\\b.png')
  #这里可以选择一块区域或者整张图片
  region = tmp_img
  
  width = int(region.size[0]*scale)             
  height = int(region.size[1]*scale)
  region = region.resize((width, height), PIL.Image.ANTIALIAS)
  base_img = base_img.convert("RGBA") 
  region = region.convert("RGBA") 
  #透明png不变黑白背景，需要加第三个参数,jpg和png不能直接合并
  base_img.paste(region, (img_x,img_y),region)       
  return base_img

stages = on_command("图", aliases={'下图','下下图','当','当当','当当当' },priority=5)

#GroupMessageEvent
@stages.handle()
async def stage_handle(bot: Bot, event: Event,state: T_State):
    #参数
    # keyword = str(event.get_message()).strip()
    #print('开始受理请求')
    starttime = datetime.now()
    keyword=state['_prefix']['command'][0]
    user = str(event.user_id)
    at_ = "[CQ:at,qq={}]".format(user)
    GameURL = 'https://splatoon2.ink/data/schedules.json'
    if keyword =='图' or keyword == '当':
        times=0
    elif keyword =='下图' or keyword == '当当':
        times=1
    else:
        times=2

    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    header= { 'User-Agent' : user_agent }
    #每次实时获取数据
    GameMode = requests.get(GameURL,headers=header).json()

    #使用文件方式读取（可以1小时异步更新一次）
    #with open('E:\\game\\bot\\qqbot\\inkbot\\src\\plugins\\schedule.json','r',encoding='utf8')as fp:
    #  GameMode = json.load(fp)
    #windows本地默认有时差问题，美国虚拟机没有
    #now = datetime.utcnow()
    now = datetime.now()

    
    game_file=GameMode

    Map1R, Map2R = stage[game_file['regular'][times]['stage_a']['id']]['name'], stage[game_file['regular'][times]['stage_b']['id']]['name']
    GameModeR = gamemode_rule_name[game_file['regular'][times]['rule']['name']]
    StartTimeR, EndTimeR = time.strftime("%H{h}",time.localtime(float(game_file['regular'][times]['start_time']))).format(h='时'),time.strftime("%H{h}",time.localtime(float(game_file['regular'][times]['end_time']))).format(h='时')
    Map1S, Map2S = stage[game_file['gachi'][times]['stage_a']['id']]['name'], stage[game_file['gachi'][times]['stage_b']['id']]['name']
    GameModeS = gamemode_rule_name[game_file['gachi'][times]['rule']['name']]
    if (len(GameModeS)) == 2:
        GameModeS=GameModeS[0]+'\n'+GameModeS[1]
    else:
        GameModeS='\n'+GameModeS[0]
    StartTimeS, EndTimeS = time.strftime("%H{h}",time.localtime(float(game_file['gachi'][times]['start_time']))).format(h='时'),time.strftime("%H{h}",time.localtime(float(game_file['gachi'][times]['end_time']))).format(h='时')
    Map1L, Map2L = stage[game_file['league'][times]['stage_a']['id']]['name'], stage[game_file['league'][times]['stage_b']['id']]['name']
    GameModeL = gamemode_rule_name[game_file['league'][times]['rule']['name']]
    if (len(GameModeL)) == 2:
        GameModeL=GameModeL[0]+'\n'+GameModeL[1]
    else:
        GameModeL='\n'+GameModeL[0]
    StartTimeL, EndTimeL = time.strftime("%H{h}",time.localtime(float(game_file['league'][times]['start_time']))).format(h='时'),time.strftime("%H{h}",time.localtime(float(game_file['league'][times]['end_time']))).format(h='时')
    global img_path
   
    base_img = PIL.Image.open(img_path+'misc/bg.png')
    radii=20
    base_img = circle_corner(base_img, radii)
    base_sep=8
    scale=0.8
    base_xx=100
    base_yy=15
    endtime = datetime.now()
    #print('1:',(endtime-starttime).seconds)
    starttime = endtime
    tmp_img = PIL.Image.open(img_path+stage[game_file['regular'][times]['stage_a']['id']]['image'])
    base_img=merge_image(base_img,tmp_img,base_xx,base_yy,scale)
    base_xx_incr=base_xx+int(tmp_img.size[0]*scale)+base_sep
    tmp_img = PIL.Image.open(img_path+stage[game_file['regular'][times]['stage_b']['id']]['image'])
    base_img=merge_image(base_img,tmp_img,base_xx_incr,base_yy,scale)
    base_yy_incr=int(tmp_img.size[1]*scale)+base_sep+base_yy
    tmp_img=PIL.Image.open(img_path+'mode/regular.png')
    base_img=merge_image(base_img,tmp_img,base_xx_incr-35,int(base_yy_incr/2)-20,0.5)
    
    tmp_img = PIL.Image.open(img_path+stage[game_file['gachi'][times]['stage_a']['id']]['image'])
    base_img=merge_image(base_img,tmp_img,base_xx,base_yy_incr,scale)
    tmp_img = PIL.Image.open(img_path+stage[game_file['gachi'][times]['stage_b']['id']]['image'])
    base_img=merge_image(base_img,tmp_img,base_xx_incr,base_yy_incr,scale)
    tmp_img=PIL.Image.open(img_path+'mode/rank.png')
    base_img=merge_image(base_img,tmp_img,int(base_xx_incr)-35,int(base_yy_incr)+30,0.5)

    tmp_img = PIL.Image.open(img_path+stage[game_file['league'][times]['stage_a']['id']]['image'])
    base_img=merge_image(base_img,tmp_img,base_xx,int(base_yy_incr*1.5)+65,scale)
    tmp_img = PIL.Image.open(img_path+stage[game_file['league'][times]['stage_b']['id']]['image'])
    base_img=merge_image(base_img,tmp_img,base_xx_incr,int(base_yy_incr*1.5)+65,scale)
    tmp_img=PIL.Image.open(img_path+'mode/league1.png')
    base_img=merge_image(base_img,tmp_img,int(base_xx_incr)-35,int(base_yy_incr*2)+20,0.5)


    draw = PIL.ImageDraw.Draw(base_img)
    font = PIL.ImageFont.truetype(img_path+"font/msyh.ttc", 45) 
    draw.text((30,20 ), f"涂\n地", (255, 255, 255), font=font)
    draw.text((30,170), GameModeS, (255, 255, 255), font=font)
    draw.text((30,310), GameModeL, (255, 255, 255), font=font)
    base_img=base_img.resize((int(base_img.size[0]*0.8), int(base_img.size[1]*0.8)),PIL.Image.ANTIALIAS)
    tmp_file = tmp_path+uuid.uuid4().hex+'.png'
    base_img.save(tmp_file,quality =80,subsampling = 0) 
    endtime = datetime.now()
    #print('2:',(endtime-starttime).seconds)
    starttime = endtime

    #imgs = f"[CQ:image,file={img_to_b64(base_img)}]"
    
   
    
    msg = at_+'\n所处时段:'+ StartTimeR+ '-' + EndTimeR
    msg = Message(msg)
    #await test.send(msg)
    
    #f=f'file:///E:\\game\\bot\\splatoonbot\\mybot\\temp\\7781234b8b0f48faa4d496fe7d47970c.jpg'
    imgs = [{
        "type": "image",
        "data": {
            "file": "file:///"+tmp_file
        }
    }]

    '''imgs= [{
        "type": "image",
        "data": {
            "file": base64_str
        }
    }]'''
    img = Message(imgs)
    msg=msg+img
    #await test.send(Message(msg))
    #seq = MessageSegment.image("{}".format('file:///E:/game/bot/splatoonbot/mybot/temp/7781234b8b0f48faa4d496fe7d47970c.jpg'))
    #fa="[CQ:face,id=178]文字[CQ:image,file=file:///E:\\game\\bot\\qqbot\\inkbot\\111.png]"
    #await test.send(seq)
    await stages.send(Message(msg))
    if '当' in keyword:
      at_ = "[CQ:at,qq={}]".format('526674852')
      msg = at_+' 还有人和当当一起约个组排'+GameModeL+'走起吗？'
      msg = Message(msg)
      await stages.send(Message(msg)) 
    endtime = datetime.now()
    #print('3:',(endtime-starttime).seconds)



coop = on_command("工",priority=5)

#GroupMessageEvent
@coop.handle()
async def coop_handle(bot: Bot, event: Event,state: T_State):
    user = str(event.user_id)
    global img_path
    at_ = "[CQ:at,qq={}]".format(user)
    GameURL = 'https://splatoon2.ink/data/coop-schedules.json'
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    header= { 'User-Agent' : user_agent }
    GameMode =(requests.get(GameURL,headers=header)).json()
    salmon_file = GameMode

    #with open('E:\\game\\bot\\qqbot\\inkbot\\src\\plugins\\coop_schedules.json','r',encoding='utf8')as fp:
    #  salmon_file = json.load(fp)
    #windows本地默认有时差问题，美国虚拟机没有
    #now = datetime.utcnow()
    now = datetime.now()
 
    base_img = PIL.Image.open(img_path+ 'misc/bgx.jpg').convert("RGBA")
    radii=20
    base_sep=8
    scale=1.5
    base_xx=20
    base_yy=60
    draw = PIL.ImageDraw.Draw(base_img)
    font = PIL.ImageFont.truetype(img_path+"font/msyh.ttc", 20) 
    
    timecol=30

    now = datetime.now()
    #不使用utc
    if now<=datetime.fromtimestamp(float(salmon_file['details'][0]['start_time'])):
        work_status='距下一开工时段还有:\n'
        time_delay=(datetime.fromtimestamp(float(salmon_file['details'][0]['start_time']))-now)
    else:
        work_status='剩余时间:'
        next_time=datetime.fromtimestamp(float(salmon_file['details'][0]['end_time']))
        time_delay= (next_time-now)
    
    hours,r=divmod((time_delay).seconds,3600)
    minutes,seconds=divmod(r,60)
    days=time_delay.days
    if days>0:
        days=str(days)+'天'
    else:
        days=''
    if hours>0:
        hours=str(hours)+'时'
    else:
        hours=''
    if minutes>0:
        minutes=str(minutes)+'分'
    else:
        minutes=''
    if seconds>0:
        seconds=str(seconds)+'秒'
    else:
        seconds=''		
    #draw.text((base_xx,15), '当前时段剩余时间:'+days+hours+minutes+seconds, (255, 255, 255), font=font)

    #for i in  json.loads(json.dumps(json.loads(rsl.text)))['details']:
    #linux bug on linux @210925
    for i in json.loads(json.dumps(salmon_file))['details']:
      stime,etime=time.strftime("%m{m}%d{d}%H{h}",time.localtime(float(i['start_time']))).format(m='月',d='日',h='时'),time.strftime("%m{m}%d{d}%H{h}",time.localtime(float(i['end_time']))).format(m='月',d='日',h='时')
         
      draw.text((base_xx,timecol), stime +' - '+ etime, (255, 255, 255), font=font)
      tmp_img = PIL.Image.open(img_path+stage[i['stage']['name']]['image'])
      base_x = int(tmp_img.size[0]*scale)+base_sep*2
      base_y = int(tmp_img.size[1]*scale)+base_sep*2
      timecol=base_y+base_yy    
    for i in  json.loads(json.dumps(salmon_file))['details']:
    
        #print (type(i),i['start_time'],i['end_time'],stage[i['stage']['name']]['name'][3:])
    
        stime,etime=time.strftime("%m{m}%d{d}%H{h}",time.localtime(float(i['start_time']))).format(m='月',d='日',h='时'),time.strftime("%m{m}%d{d}%H{h}",time.localtime(float(i['end_time']))).format(m='月',d='日',h='时')
       # draw.text((base_xx,timecol), stime+' - '+etime, (255, 255, 255), font=font)
        tmp_img = PIL.Image.open(img_path+stage[i['stage']['name']]['image'])
        base_x = int(tmp_img.size[0]*scale)+base_sep*2
        base_y = int(tmp_img.size[1]*scale)+base_sep*2
        timecol=base_y+base_yy
 
        #地图图片位置
        base_img = merge_image(base_img,tmp_img,base_xx,base_yy,scale)	
        #武器初始位置=地图位置+空格
        base_wep_y = base_yy
        base_wep_x = base_x+base_xx
        k=0
        #print (base_img.size)
        #linux bug : weapon chinese name can not draw
        for j in i['weapons']:

            if 'weapon' in j.keys():
                tmp_img = PIL.Image.open(img_path+weapons[j['weapon']['id']]['image'])
                draw.text((base_wep_x+base_sep,base_wep_y+int(tmp_img.size[1]*0.5)-base_sep), weapons[j['weapon']['id']]['cn'], (255, 255, 255), font=font)
            else:
                tmp_img = PIL.Image.open(img_path+weapons[j['id']]['image'])
                draw.text((base_wep_x+base_sep,base_wep_y+int(tmp_img.size[1]*0.5)-base_sep), weapons[j['id']]['cn'], (255, 255, 255), font=font)
            #print(weapons[j['id']]['cn'])
            base_img=merge_image(base_img,tmp_img,base_wep_x,base_wep_y,0.5)
            #draw.text((base_wep_x+base_sep,base_wep_y+int(tmp_img.size[1]*0.5)-base_sep), weapons[j['weapon']['id']]['cn'], (255, 255, 255), font=font)
            k=k+1	
            if k==2:
                base_wep_y=base_wep_y+int(tmp_img.size[1]*0.5)+base_sep*4
                base_wep_x=base_x+base_xx+base_sep
            elif k==1 or k==3:
                #base_wep_y=base_wep_y+50
                base_wep_x=base_wep_x+int(tmp_img.size[0]*0.5)+base_sep*3
        base_yy = base_yy+base_y+base_sep*3
        #base_yy=int(tmp_img.size[1]*0.7)+base_sep+base_yy
    base_img = base_img.crop((0,0,base_img.size[0]-60,base_img.size[1])) #	
    base_img = circle_corner(base_img, radii)
    tmp_file = tmp_path+uuid.uuid4().hex+'.png'
    
    base_img.save(tmp_file,quality =80,subsampling = 0) 
    #imgs = f"[CQ:image,file={img_to_b64(base_img)}]"

    #
    img = stage[salmon_file['details'][0]['stage']['name']]['image']
    #img = url+img
    


    msg = at_+'\n打工安排:\n'+ work_status+days+hours+minutes
    msg = Message(msg)
    
    #await test.send(msg)
    
    #f=f'file:///E:\\game\\bot\\splatoonbot\\mybot\\temp\\7781234b8b0f48faa4d496fe7d47970c.jpg'
    imgs = [{
        "type": "image",
        "data": {
            "file": "file:///"+tmp_file
        }
    }]
    #print(imgs)
    img = Message(imgs)
    msg=msg+img
    #await test.send(Message(msg))
    #seq = MessageSegment.image("{}".format('file:///E:/game/bot/splatoonbot/mybot/temp/7781234b8b0f48faa4d496fe7d47970c.jpg'))
    #fa="[CQ:face,id=178]文字[CQ:image,file=file:///E:\\game\\bot\\qqbot\\inkbot\\111.png]"
    #await test.send(seq)
    await coop.send(Message(msg))


rand_wep = on_command("随机武器",priority=5)

#GroupMessageEvent
@rand_wep.handle()
async def rand_handle(bot: Bot, event: Event,state: T_State):
  gamemode_list = ['区域', '鱼', '塔', '蛤蜊', '涂地' ]
  keyword = str(event.get_message()).strip()

  if keyword not in gamemode_list:
    gamemode = random.choice(gamemode_list)
  else:
    gamemode = keyword
  user = str(event.user_id)
  at_ = "[CQ:at,qq={}]".format(user)
  item=[]
  now = datetime.now()
  counters= get_counter(now.strftime('%Y-%m-%d'));
  mapid=str(random_id('map'))

  

  for i in range(0,8):
   item.append(str(random_id('wep')))
  base_img = PIL.Image.open(img_path+'misc/bg_big3.jpg')
  radii=20
  base_img = circle_corner(base_img, radii)
  #subweapon_path ="common/assets/img/subspe/"
  j = 0
  base_sep=8
  scale=0.8
  #模式
  #地图
  base_xx=50
  base_yy=35
  #tmp_img = Image.open('H:\\game\\mysite\\games\\'+stage[mapid]['image'][3:])
  #base_img=merge_image(base_img,tmp_img,base_xx,base_yy,1)
  #武器
  
  #global img_path
  #global img_path_sub
  tmp_img_stage = PIL.Image.open(img_path+stage[mapid]['image'] )
   
  base_img=merge_image(base_img,tmp_img_stage,55,10,1.1)
  for i in item:
  	tmp_img = PIL.Image.open(img_path+weapons[i]['image'])
  	if j == 0:
  		base_xx = 30
  		base_yy=280
  	elif j == 4:
  		base_xx = 240
  		base_yy=280
  	else:
  		pass
  	j=j+1
  	
  	tmp_img_sub = PIL.Image.open(img_path_sub+subweapons[weapons[i]['sub_name']])
  	tmp_img_spe = PIL.Image.open(img_path_sub+specials[weapons[i]['speical_name']])
  	base_img=merge_image(base_img,tmp_img,base_xx,base_yy,scale)
  	base_img=merge_image(base_img,tmp_img_sub,base_xx+int(tmp_img.size[0]*scale)+10,base_yy,scale)
  	base_img=merge_image(base_img,tmp_img_spe,base_xx+int(tmp_img.size[0]*scale)+10,base_yy+int(tmp_img_sub.size[1]*scale)+10,scale)
  	base_yy=base_yy+int(tmp_img.size[1]*scale)+30
  draw = PIL.ImageDraw.Draw(base_img)
  font = PIL.ImageFont.truetype(img_path+"font/msyh.ttc", 45) 
  draw.text((80,200 ), "A队", (255, 255, 255), font=font) 
  draw.text((280,200), "B队", (255, 255, 255), font=font) 
  #矩形处理
  draw.rectangle(((30, 6),(410, 200)), fill=None, outline='white', width=5)  
  draw.rectangle(((30, 250),(210, 790)), fill=None, outline='red', width=5)  
  draw.rectangle(((230, 250),(410, 790)), fill=None, outline='green', width=5)  
  tmp_file = tmp_path+uuid.uuid4().hex+'.png'
  w, h = base_img.size
  base_img = base_img.resize((int(w*0.8), int(h*0.8)))
  base_img.save(tmp_file) 
 
  
  msg = at_+"\n序号:"+str(counters)+'  模式：'+gamemode +'\n地图:'+stage[mapid]['name']+'\n' 
  msg = Message(msg)
  imgs= [{
        "type": "image",
        "data": {
            "file": "file:///"+ img_path+stage[mapid]['image'] 
        }
    }]
  img = Message(imgs)
  #msg = msg+img+'\n'
  imgs = [{
        "type": "image",
        "data": {
            "file": "file:///"+ tmp_file 
        }
    }]
  img = Message(imgs)
  msg=msg+img
  await rand_wep.send(Message(msg))
  
