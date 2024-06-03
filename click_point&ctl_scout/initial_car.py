import json

import requests
import asyncio
import websockets




# start_server = websockets.serve(status_notice, "localhost", 8089)
#
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()


IP_URL = 'http://10.7.5.88:8080'

mapname = 'wktest3'
# 初始化操作
# init_point_name = 'center'
# url = f'/gs-robot/cmd/initialize?map_name={mapname}&init_point_name={init_point_name}'
# r = requests.get(IP_URL + url)

# # 添加导航点   ###################添加地图上鼠标打的点到导航点,再将导航点添加到任务，最后执行任务
# url = '/gs-robot/cmd/position/add_position'
# data = {
#  "angle": 90,
#  "gridX": 1050,
#  "gridY": 824,
#  "mapName": f'{mapname}',
#  "name": "nav2",
#  "type": 2  # 除了type字段需定义为2外, 以上字段均为自定义
# }
# ndata = json.dumps(data)
# r = requests.post(IP_URL + url, ndata)
# print("r:", r.content)

# 查看所有导航点
url = f'/gs-robot/data/positions?map_name={mapname}&type=2'
r = requests.get(IP_URL + url)
print("所有导航点:", r.content)



# 检查初始化是否完成
url = f'/gs-robot/cmd/is_initialize_finished'
r = requests.get(IP_URL + url)
print("是否完成初始化:", r.json()['data'])

"""
获取小车当前的位置信息（x、y、angle）
"""
pos_url = '/gs-robot/real_time_data/position'
r = requests.get(IP_URL + pos_url)
print("位置:", r.content)
angle = float(r.json()['angle'])
x = r.json()['gridPosition']['x']
y = r.json()['gridPosition']['y']
print("小车现在的位置（angle,x,y）:\n", angle, x, y)


# 添加任务到任务列表，任务就是机器人依次到达栅格化坐标点
tdata = {
    "name": "maintaskwk3",
    "map_name": f'{mapname}',
    "map_id": "",
    "loop": False,
    "tasks": [
        {
            "name": "NavigationTask",
            "start_param":{
                "map_name": f'{mapname}',
                "position_name": "nav1"
            }
        },
        {
            "name": "NavigationTask",
            "start_param": {
                "map_name": f'{mapname}',
                "position_name": "nav2"
            }
        }
        # {"name": "NavigationTask",
        #  "start_param":{
        #      "destinnation":{
        #          "angle": 100,
        #          "gridPosition":{
        #              "x": 1000,
        #              "y": 900
        #          }
        #      }
        #  }
        #  }
    ]
}
jtdata = json.dumps(tdata)
# print("jdata:", data)
url = '/gs-robot/cmd/save_task_queue'
r = requests.post(IP_URL + url, jtdata)
print("添加任务是否成功：", r.json()['successed'])

#开始执行一个任务
url = '/gs-robot/cmd/start_task_queue'
rdata = {
    "name": "maintaskwk3",
    "loop": False,
    "map_name": f'{mapname}'
}
jrdata = json.dumps(rdata)
# r = requests.post(IP_URL + url, jrdata)
# print("执行任务情况：", r.content)

# async def status_notice(websocket, path):
#     # 这里可以添加你的逻辑以获取状态信息
#     status_info = {"status": "running"}  # 示例状态信息
#     await websocket.send(json.dumps(status_info))  # 发送状态信息
#
# start_server = websockets.serve(status_notice, "localhost", 8089)
#
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()
#
# url = f'/gs-robot/notice/status port:8089'


# 导航到指定点
des = [-178, 973, 852]  # nav1
angle = des[0]
x = des[1]
y = des[2]
data = {
    "destination": {
        "angle": angle,
        "gridPosition": {
            "x": x,
            "y": y
        }
    }
}
j_data = json.dumps(data)
print("j_data:", j_data)
url_nav = '/gs-robot/cmd/navigate'
# r = requests.post(IP_URL + url_nav, j_data)
# print("r:", r.content)
########################### 不能连续同时执行让小车到两个不同地点的命令，需要加一个指示，到达一个点后再执行到下一个点的操作。
# 例如再次获取当前位置，看是否与指定点十分接近

data2 = {  # ori1
    "destination": {
        "angle": -5.71,
        "gridPosition": {
            "x": 1152,
            "y": 819
        }
    }
}
# r = requests.post(IP_URL + url_nav, json.dumps(data2))
# print("r:", r.content)