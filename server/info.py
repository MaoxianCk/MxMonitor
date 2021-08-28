import time
import psutil
import GPUtil
import pprint
import re
import threading

class Info:
    sysInfo = {}
    isRun = False
    timer = True
    timeout = 5 # s
    thread = None

    def formatPercentStr(self, val):
        return '{:g}%'.format(round(val, 2))


    def formatUnitStr(self, val, unit = 'B'):
        units = ['B', 'KB', 'M', 'G', 'T', 'PB']
        i = units.index(unit)
        for i in range(i, len(units)):
            unit = units[i]
            if val < 1024:
                break
            val /= 1024
        return '{:g}{}'.format(round(val, 1), unit)


    def getInfo(self):
        res = {}

        res['cpu'] = {
            # 逻辑数量
            'logicCount': psutil.cpu_count(),
            # 物理数量
            'physicalCount': psutil.cpu_count(logical=False),
            # cpu使用率
            'usageSumPercent': psutil.cpu_percent(interval=1),
            # 每核心使用率
            'usagePercents': psutil.cpu_percent(interval=1, percpu=True)
        }
        res['cpu'].update({
            'usageSumPercentStr': self.formatPercentStr(res['cpu']['usageSumPercent']),
            'usagePercentsStr': [self.formatPercentStr(i) for i in res['cpu']['usagePercents']]
        })

        memInfo = psutil.virtual_memory()
        res['memory'] = {
            'total': memInfo.total,
            'available': memInfo.available,
            'percent': memInfo.percent,
            'free': memInfo.free,
            'used': memInfo.total - memInfo.free
        }
        res['memory'].update({
            'totalStr': self.formatUnitStr(res['memory']['total']),
            'availableStr': self.formatUnitStr(res['memory']['available']),
            'percentStr': self.formatPercentStr(res['memory']['percent']),
            'freeStr': self.formatUnitStr(res['memory']['free']),
            'usedStr': self.formatUnitStr(res['memory']['used'])
        })

        res['disk'] = []
        partitions = psutil.disk_partitions()
        for item in partitions:
            info = psutil.disk_usage(item.mountpoint)
            res['disk'].append({
                'mountPoint': item.mountpoint,
                'total': info.total,
                'used': info.used,
                'free': info.free,
                'percent': info.percent
            })
        for item in res['disk']:
            item.update({
                'mount': re.match('^([a-zA-Z])+', item['mountPoint']).group(1),
                'totalStr': self.formatUnitStr(item['total']),
                'usedStr': self.formatUnitStr(item['used']),
                'freeStr': self.formatUnitStr(item['free']),
                'percentStr': self.formatPercentStr(item['percent'])
            })

        res['gpu'] = []
        Gpus = GPUtil.getGPUs()
        for gpu in Gpus:
            gpu_memoryTotal = gpu.memoryTotal
            gpu.memoryUsed = gpu.memoryUsed
            gpu_memoryUtil = gpu.memoryUtil
            # GPU序号，GPU总量，GPU使用量，gpu使用占比
            res['gpu'].append(
                {
                    'id': gpu.id,
                    'memoryTotal': gpu_memoryTotal,
                    'memoryUsed': gpu.memoryUsed,
                    'memoryUtil': gpu_memoryUtil,
                    'memoryTotalStr': self.formatUnitStr(gpu_memoryTotal, 'M'),
                    'memoryUsedStr': self.formatUnitStr(gpu.memoryUsed, 'M'),
                    'memoryUtilStr': self.formatPercentStr(gpu_memoryUtil)
                })

        return res

    def doUpdateSysInfo(self):
        if Info.isRun == False:
            Info.isRun = True
            while Info.timer:
                Info.sysInfo = self.getInfo()
                # print(time.strftime("update at %Y-%m-%d %H:%M:%S", time.localtime()))
                time.sleep(1)

    def startUpdateSysInfo(self):
        print('Start at: {}'.format(time.strftime("update at %Y-%m-%d %H:%M:%S", time.localtime())))
        Info.thread = threading.Thread(target=self.doUpdateSysInfo)
        Info.thread.setDaemon(True)
        Info.thread.start()

    def stopUpdateSysInfo(self):
        Info.timer = False
        Info.isRun = False

if __name__ == '__main__':
    Info().getInfo()