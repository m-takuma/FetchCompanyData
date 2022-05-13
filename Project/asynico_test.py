import asyncio
import time
from arelle import ModelXbrl
from arelle import ModelManager
from arelle import Cntlr
import multiprocessing
test = "C://Users//taku3//OneDrive//デスクトップ//XBRL_test//PublicDoc//jpcrp030000-asr-001_E03061-000_2021-02-28_01_2021-05-27.xbrl"

async def sleeping(sec):
    loop = asyncio.get_event_loop()
    print(F"start: {sec}秒待つ")
    cntlr = Cntlr.Cntlr(logFileName='logToPrint')
    modelManager = ModelManager.initialize(cntlr=cntlr)
    #await loop.run_in_executor(None,time.sleep, sec)
    await loop.run_in_executor(None,modelManager.load,test)
    print(f"finish: {sec}秒待つ")

def main():
    array = [5,1,8,3,4]
    loop = asyncio.get_event_loop()
    print("===一つだけ実行===")
    loop.run_until_complete(sleeping(2))

    print("\n===5つ並列的に動かす===")
    gather = asyncio.gather(*[sleeping(x) for x in array])
    loop.run_until_complete(gather)

def manager(i):
    print(i)
    cntlr = Cntlr.Cntlr(logFileName='logToPrint')
    modelManager = ModelManager.initialize(cntlr=cntlr)
    modelManager.load(test)
    print(f"end {i}")
    

def manager_2():
    print(2)
    cntlr = Cntlr.Cntlr(logFileName='logToPrint')
    modelManager = ModelManager.initialize(cntlr=cntlr)
    modelManager.load(test)
    print("end 2")
    


if __name__ == "__main__":
    print("start")
    t1 = time.time()
    cpu_num = 5
    ls = [1,2,3,4,5]
    p = multiprocessing.Pool(processes=cpu_num)
    p.map(manager,ls)
    t2 = time.time()
    elapsed_time = t2-t1
    print(f"経過時間：{elapsed_time}")
    print("end")

    #main()

def worker1():
    print('start worker1')
    time.sleep(5)
    print('end worker1')

# プロセスで実行する関数の準備
def worker2(x, y):
    print('start worker2')
    time.sleep(5)
    print('end worker2', x, y)

